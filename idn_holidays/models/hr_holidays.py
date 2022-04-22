# -*- coding: utf-8 -*-

import pytz
from datetime import timedelta, datetime
from dateutil import rrule

from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
DEFAULT_SERVER_DATETIME_FORMAT as DSDTF
from odoo.report import render_report
from openerp.tools import float_compare
HOURS_PER_DAY = 8

class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def _get_hr_year(self):
        '''
        The method used to get HR year value.
        @param self : Object Pointer
        @return : id of HR year
        ------------------------------------------------------
        '''
        today = datetime.strftime(datetime.today().date(), DSDF)
        return  self.fetch_hryear(today)

    @api.model
    def fetch_hryear(self, date=False):
        '''
        The method used to fetch HR year value.
        @param self : Object Pointer
        @return : id of HR year
        ------------------------------------------------------
        '''
        if not date:
            date = datetime.today().date()
        hr_year_obj = self.env['hr.year']
        args = [('date_start', '<=' , date), ('date_stop', '>=', date)]
        hr_year_brw = hr_year_obj.search(args)
        if hr_year_brw and hr_year_brw.ids:
            hr_year_ids = hr_year_brw
        else:
            if date:
                year = datetime.strptime(date, DSDF).year
            else:
                year = datetime.today().date().year
            end_date = str(year) + '-12-31'
            start_date = str(year) + '-01-01'
            hr_year_ids = hr_year_obj.create({'date_start': start_date,
                                              'date_stop' : end_date,
                                              'code': str(year),
                                              'name': str(year)})
        return hr_year_ids.ids[0]

    hr_year_id  = fields.Many2one('hr.year', 'HR Year', default=_get_hr_year)
    rejection   = fields.Text('Reason')
    user_view   = fields.Boolean(compute='_user_view_validate',
                               string="validate")
    ttl_days    = number_of_days = fields.Float('Total Days')
    virtual_remaining_leaves = fields.Float(related='holiday_status_id.virtual_remaining_leaves')
    sisa_cuti_bulanan       = fields.Float(string='Sisa Alokasi Bulanan')
    leave_month             = fields.Char(string='Month')
    state = fields.Selection([
        ('draft', 'Draft'), #Draft Employee
        ('cancel', 'Cancelled'), #cancel
        ('confirm', 'Confirm Head Group'), #Approve Head Group
        ('refuse', 'Refused'),
        ('validate1', 'Confirm Manager'), #approve hr holiday manager
        ('validate', 'Approved')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
            help="The status is set to 'To Submit', when a holiday request is created." +
            "\nThe status is 'To Approve', when holiday request is confirmed by user." +
            "\nThe status is 'Refused', when holiday request is refused by manager." +
            "\nThe status is 'Approved', when holiday request is approved by manager.")




    @api.multi
    def action_validate(self):
        if self.state == 'confirm' and not self.env.user.has_group('brt_health_reimburse.manager'):
            raise UserError(_('Only an Head Group Access can approve leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr.group_hr_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            if holiday.double_validation:
                holiday.write({'manager_id2': manager.id})
            else:
                holiday.write({'manager_id': manager.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                meeting_values = {
                    'name': holiday.display_name,
                    'categ_ids': [(6, 0, [holiday.holiday_status_id.categ_id.id])] if holiday.holiday_status_id.categ_id else [],
                    'duration': holiday.number_of_days_temp * HOURS_PER_DAY,
                    'description': holiday.notes,
                    'user_id': holiday.user_id.id,
                    'start': holiday.date_from,
                    'stop': holiday.date_to,
                    'allday': False,
                    'state': 'open',            # to block that meeting date in the calendar
                    'privacy': 'confidential'
                }
                #Add the partner_id (if exist) as an attendee
                if holiday.user_id and holiday.user_id.partner_id:
                    meeting_values['partner_ids'] = [(4, holiday.user_id.partner_id.id)]

                meeting = self.env['calendar.event'].with_context(no_mail_to_attendees=True).create(meeting_values)
                holiday._create_resource_leave()
                holiday.write({'meeting_id': meeting.id})
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True

     # Modify by Baim #
    @api.constrains('state', 'number_of_days_temp', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            print ('Tracing >>>>>>>>>>>>>>>>>>',holiday.employee_id.name)
            if holiday.holiday_type != 'employee' or holiday.type != 'remove' or not holiday.employee_id or holiday.holiday_status_id.limit or self.env.user.has_group('hr.group_hr_manager'):
                continue
            leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
              float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                        'Please verify also the leaves waiting for validation.'))

    # @api.constrains('state', 'number_of_days_temp', 'holiday_status_id')
    # def _check_holidays(self):
        # for holiday in self:
            # if holiday.holiday_type != 'employee' or holiday.type != 'remove' or not holiday.employee_id or holiday.holiday_status_id.limit:
                # continue
            # leave_days = holiday.holiday_status_id.get_days(holiday.employee_id.id)[holiday.holiday_status_id.id]
            # if not self.env.user.has_group('hr.group_hr_manager'):
                # if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                    # float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    # raise ValidationError(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                            # 'Please verify also the leaves waiting for validation.'))

    @api.multi
    def write(self, vals):
        result = super(HrHolidays, self).write(vals)
        if self.type == 'remove' and self.holiday_status_id.id == 1:
            if self.sisa_cuti_bulanan < 0.0:
                raise ValidationError(_('Cuti Bulanan anda melebihi alokasi bulan ini!'))
        return result

    @api.multi
    def _user_view_validate(self):
        """
        This method used to visible Approve button to user if user has rights 
        of HR manager and user id = 1 can see this button.
        @param self : Object Pointer
        ---------------------------------------------------------------------
        """
        cr, uid, context = self.env.args
        res_user = self.env['res.users']
        for holiday in self:
            if uid != 1 and \
            (res_user.has_group('base.group_user') or \
             res_user.has_group('hr.group_hr_user')) and not \
             (res_user.has_group('hr.group_hr_manager')):
                if holiday.employee_id.user_id.id == uid:
                    self.user_view = True
                else:
                    self.user_view = False
            else:
               self.user_view = False

    @api.constrains('date_from', 'date_to', 'hr_year_id', 'holiday_status_id',
                    'number_of_days_temp')
    def _check_current_year_leave_req(self):
        '''
        The method is used to validate only current year leave request.
        @param self : Object Pointer
        @return : True or False
        ------------------------------------------------------
        '''
        if self._context is None:
            self._context = {}
        current_year = datetime.today().year
        for rec in self:
            if rec.type == 'remove' and rec.holiday_status_id.id:
                from_date = datetime.strptime(rec.date_from, DSDTF)
                to_date = datetime.strptime(rec.date_to, DSDTF)
                # convert start and end date in string format
                f_date = datetime.strftime(from_date.date(), DSDF)
                t_date = datetime.strftime(to_date.date(), DSDF)
                # fetch Holiday line record
                domain = [('holiday_date', '=' , f_date),
                          ('holiday_date', '=' , t_date),
                          ('holiday_id.state', '=', 'validated')]
                holiday_line_rec = self.env['hr.holiday.lines'].search(domain)
                # check if start date or end date is not in HR year
                if current_year != from_date.year or \
                current_year != to_date.year:
                        raise ValidationError(_('You can apply leave Request \
                        only for the current year!'))
                #  check start and end date is between selected HR year's
                # start and stop date
                if rec.hr_year_id and rec.hr_year_id.date_start and \
                rec.hr_year_id.date_stop:
                    if rec.hr_year_id.date_start > rec.date_from or \
                    rec.hr_year_id.date_stop < rec.date_to:
                        raise ValidationError(_('Start date and end date must \
                        be related to selected HR year!'))
                    if rec.hr_year_id and rec.hr_year_id.state == 'done':
                        raise ValidationError(_("You can not take leave \
                        in close HR year!"))

                # check start and end date is on holidays (weekends or public
                # holidays and count day by working_days_only)
                if ((from_date.weekday() in [5, 6] and  \
                    to_date.weekday() in [5, 6]) or holiday_line_rec) and \
                    rec.holiday_status_id.count_days_by and \
                    rec.holiday_status_id.count_days_by == \
                    'working_days_only':
                    raise ValidationError("Start date or End date should not \
                    on holiday(s)!")
                # check constraint on number_of_days_temp field
                if rec.number_of_days_temp and rec.ttl_days and \
                rec.number_of_days_temp != rec.ttl_days:
                    raise ValidationError("Enter \
                                 appropriate values for days !")

    @api.multi
    def action_refuse(self):
        '''
            Sets state to refused
        '''
        view_id = self.env.ref('idn_holidays.view_refuse_leave_form')
        return {
                'name': 'Refuse Leave',
                'type': 'ir.actions.act_window',
                'view_id': view_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'refuse.leave',
                'target': 'new',
            }

    @api.multi
    def _get_number_of_daystmp(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates 
        given as string."""
        diff_day = 0.0
        if date_from and date_to:
            diffnt_days = (date_to - date_from)
            if diffnt_days:
                diff_day = diffnt_days.days
        return diff_day

    @api.multi
    def get_date_from_range(self, from_date, to_date):
        '''
            Returns list of dates from from_date tp to_date
            @param from_date: Starting date for range
            @param to_date: Ending date for range
            @return : Returns list of dates from from_date to to_date  
        '''
        dates = []
        if from_date and to_date:
            from_dt = from_date.date()
            to_dt = to_date.date()
            dates = list(rrule.rrule(rrule.DAILY, dtstart=from_dt, until=to_dt))
        return dates

    @api.multi
    def _check_holiday_to_from_dates(self, start_date, end_date):
        '''
        Checks that there is a public holiday,Saturday and Sunday on date 
        of leave
        @param self : Object Pointer
        @param from_date: Starting date for range
        @param to_date: Ending date for range
        @return : Returns the numbers of days
        --------------------------------------------------------------------
        '''
        if start_date and end_date:
            dates = self.get_date_from_range(start_date, end_date)
            dates = [x.strftime(DSDF) for x in dates]
            remove_date = []
            for day in dates:
                date = datetime.strptime(day, DSDF).date()
                if date.isoweekday() in [6, 7]:
                    remove_date.append(day)
            for remov in remove_date:
                if remov in dates:
                    dates.remove(remov)
            date_f = start_date.date()
            public_holiday_obj = self.env['hr.holiday.public']
            public_holiday_ids = public_holiday_obj.search([('state', '=',
                                                             'validated'),
                                                            ('name', '=',
                                                             date_f.year)])
            if public_holiday_ids and public_holiday_ids.ids:
                for public_holiday_record in public_holiday_ids:
                    for holidays in public_holiday_record.holiday_line_ids:
                        if holidays.holiday_date in dates:
                            dates.remove(holidays.holiday_date)
            no_of_day = len(dates) or 0.0
            return no_of_day

    @api.onchange('date_from', 'date_to', 'holiday_status_id')
    def onchange_date_from(self, date_from=False, date_to=False,
                           holiday_status_id=False):
        '''
        when you change from date, this method will set 
        leave type and numbers of leave days accordingly.
        @param self: The object pointer
        ------------------------------------------------------
        @return: Dictionary of values.
        '''
        user = self.env.user
        date_from = self.date_from
        date_to = self.date_to
        tz = "Etc/GMT+7"
        local_tz = pytz.timezone(user.tz or tz)
        from_dt = to_dt = False
        if date_from:
            from_dt = datetime.strptime(date_from,
                                        DSDTF).replace(tzinfo=pytz.utc
                                         ).astimezone(local_tz)
        if date_to:
            to_dt = datetime.strptime(date_to, DSDTF).replace(tzinfo=pytz.utc
                                             ).astimezone(local_tz)
        holiday_status_id = self.holiday_status_id
        leave_day_count = False
        ttl_days = 0.0
        if holiday_status_id:
            leave_day_count = self.holiday_status_id.count_days_by
        if (date_from and date_to) and (date_from > date_to):
            raise UserError(_('Warning!\nThe start date must be anterior to \
            the end date.'))
        elif (date_from and date_to):
            to_dt = from_dt
        result = {'value': {}}
        if date_from and not date_to:
            date_to_with_delta = datetime.strptime(date_from, DSDTF) + \
                                 timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)
        if date_to and date_from and leave_day_count \
        and leave_day_count == 'working_days_only':
            diff_day = self._check_holiday_to_from_dates(from_dt, to_dt)
            ttl_days = diff_day
        else:
            diff_day = self._get_number_of_daystmp(from_dt, to_dt)
            ttl_days = diff_day + 1
        result['value']['number_of_days_temp'] = ttl_days
        result['value']['ttl_days'] = ttl_days
        return result

    @api.onchange('date_from', 'date_to', 'holiday_status_id')
    def onchange_date_to(self, date_from=False, date_to=False,
                         holiday_status_id=False):
        '''
        when you change to date, this method will set 
        leave type and numbers of leave days accordingly.
        @param self: The object pointer
        ------------------------------------------------------
        @return: Dictionary of values.
        '''
        user = self.env.user
        date_from = self.date_from
        date_to = self.date_to
        tz = "Etc/GMT+7"
        local_tz = pytz.timezone(user.tz or tz)
        from_dt = to_dt = False
        if date_from:
            from_dt = datetime.strptime(date_from,
                                        DSDTF).replace(tzinfo=pytz.utc
                                         ).astimezone(local_tz)
        if date_to:
            to_dt = datetime.strptime(date_to, DSDTF).replace(tzinfo=pytz.utc
                                             ).astimezone(local_tz)
        holiday_status_id = self.holiday_status_id
        leave_day_count = False
        ttl_days = 0.0
        if holiday_status_id and holiday_status_id != False:
            leave_day_count = holiday_status_id.count_days_by
        result = {'value': {}}
        if (date_to and date_from) and leave_day_count and \
        leave_day_count == 'working_days_only':
            diff_day = self._check_holiday_to_from_dates(from_dt, to_dt)
            ttl_days = diff_day
        else:
            diff_day = self._get_number_of_daystmp(from_dt, to_dt)
            ttl_days = diff_day + 1
        result['value']['number_of_days_temp'] = ttl_days
        result['value']['ttl_days'] = ttl_days
        return result

    @api.model
    def assign_carry_forward_leave(self):
        '''
        This method will be called by scheduler which will assign 
        carry forward leave on end of the year i.e YYYY/12/31 23:59:59
        '''
        emp_obj = self.env['hr.employee']
        holiday_status_obj = self.env['hr.holidays.status']
        # fetch users who have rights of HR manager
        res_user_rec = self.env['res.users'].search([])
        res_user_ids = res_user_rec.filtered(lambda x :
                                            x.has_group('hr.group_hr_manager')\
                                             ).ids
        emp_ids = emp_obj.search([('user_id', 'in', res_user_ids)])
        # fetch work email of HR manager
        work_email = list(set([str(emp.work_email or emp.user_id.login)
                               for emp in emp_ids]))
        today = datetime.today().date()
        year = today.year
        next_year_date = str(year + 1) + '-01-01'
        empl_ids = emp_obj.search([('active', '=', True)])
        holiday_status_ids = holiday_status_obj.search([
                                                        ('cry_frd_leave',
                                                         '>', 0)])
        fiscalyear_id = self.fetch_hryear(next_year_date)
        current_fiscalyear_id = self.fetch_hryear(datetime.strftime(today, DSDF))
        fiscalyear_rec = self.env['hr.year'].browse(current_fiscalyear_id)
        start_date = fiscalyear_rec.date_start
        end_date = fiscalyear_rec.date_stop
        for holiday in holiday_status_ids:
            for employee in empl_ids:
                if employee.user_id and employee.user_id.id == 1:
                    continue
                add = 0.0
                remove = 0.0
                self._cr.execute("""SELECT sum(number_of_days_temp) FROM 
                hr_holidays where employee_id=%d and state='validate' and 
                holiday_status_id = %d and type='add' and hr_year_id=%d
                """ % (employee.id, holiday.id, current_fiscalyear_id))
                all_datas = self._cr.fetchone()
                if all_datas and all_datas[0]:
                    add += all_datas[0]
                self._cr.execute("""SELECT sum(number_of_days_temp) FROM 
                hr_holidays where employee_id=%d and state='validate' and 
                holiday_status_id = %d and type='remove' and date_from >= 
                '%s' and date_to <= '%s'""" % (employee.id, holiday.id,
                                               start_date, end_date))
                leave_datas = self._cr.fetchone()
                if leave_datas and leave_datas[0]:
                    remove += leave_datas[0]
                final = add - remove
                final = final > holiday.cry_frd_leave and \
                holiday.cry_frd_leave or final
                if final > 0.0:
                    cleave_dict = {
                        'name' : 'Default Carry Forward Leave Allocation for '
                    + str(year + 1),
                        'employee_id': employee.id,
                        'holiday_type' : 'employee',
                        'holiday_status_id' : holiday.id,
                        'number_of_days_temp' : final,
                        'type' : 'add',
                        'hr_year_id' : fiscalyear_id,
                        }
                    self.create(cleave_dict)
        if work_email:
            obj_mail_server = self.env['ir.mail_server']
            mail_server_ids = obj_mail_server.search([])
            if mail_server_ids and mail_server_ids.ids:
                mail_server_record = mail_server_ids[0]
                email_from = mail_server_record.smtp_user
                if email_from:
                    body = "Hi,<br/><br/><b> " + self._cr.dbname + "</b> has finished performing the Auto Allocation For <b>\
            " + str(year + 1) + "</b>.<br/><br/>Kindly login to <b> " + self._cr.dbname + "</b> to confirm the leave allocations. \
            <br/><br/>Thank You,<br/><br/><b>" + self._cr.dbname + "</b>"
                    message_hrmanager = obj_mail_server.build_email(
                        email_from=email_from,
                        email_to=work_email,
                        subject='Notification : Auto Allocation Complete for ' + str(year + 1),
                        body=body,
                        body_alternative=body,
                        email_cc=None,
                        email_bcc=None,
                        attachments=None,
                        references=None,
                        object_id=None,
                        subtype='html',
                        subtype_alternative=None,
                        headers=None)
                    obj_mail_server.send_email(message=message_hrmanager,
                                               mail_server_id=mail_server_record.id)
        return True

    @api.multi
    def assign_default_leave(self):
        '''
        This method will be called by scheduler which will assign 
        Annual leave at end of the year i.e YYYY/12/01 00:01:01
        '''
        emp_obj = self.env['hr.employee']
        holi_stts_obj = self.env['hr.holidays.status']

        today = datetime.today().date()
        year = today.year
        next_year_date = str(year) + '-01-01'
        fiscalyear_id = self.fetch_hryear(next_year_date)

        holi_status_ids = holi_stts_obj.search([('default_leave_allocation',
                                                 '>', 0)])
        if holi_status_ids:
            empl_ids = emp_obj.search([('active', '=', True)])
            for holiday in holi_status_ids:
                for employee in empl_ids:
                    if employee.user_id and employee.user_id.id == 1:
                        continue
                    leave_dict = {
                        'name' : 'Assign Default Allocation for ' + str(year + 1),
                        'employee_id': employee.id,
                        'holiday_type' : 'employee',
                        'holiday_status_id' : holiday.id,
                        'number_of_days_temp' : holiday.default_leave_allocation,
                        'type' : 'add',
                        'hr_year_id' : fiscalyear_id
                    }
                    self.create(leave_dict)
                    holiday_name = holiday.name
                    ttl_days = holiday.default_leave_allocation
                    work_email = []
                    if employee.user_id.login or employee.work_email:
                        work_email = [str(employee.work_email or
                                          employee.user_id.login)]
                    if work_email:
                        obj_mail_server = self.env['ir.mail_server']
                        mail_server_ids = obj_mail_server.search([])
                        if mail_server_ids and mail_server_ids.ids:
                            mail_server_record = mail_server_ids[0]
                            email_from = mail_server_record.smtp_user
                            if email_from:
                                body = """Hello,<br/>
        This mail is regarding to default annual leave allocation to you for
        """ + str(year + 1) + """ year.<br/>
        Leave details are as follow:<br/>
        <p style="border-left: 1px solid #8e0000; margin-left: 30px;" >
        &nbsp; Leave Type : <strong>""" + holiday_name + """</strong><br/>
        &nbsp; No. of Days : <strong>""" + str(ttl_days) + """</strong>
        </p>
        Regards,"""
                                message_hrmanager = obj_mail_server.build_email(
                                    email_from=email_from,
                                    email_to=work_email,
                                    subject='Notification : Default Annual \
                                    Leave Allocation for ' + str(year + 1),
                                    body=body,
                                    body_alternative=body,
                                    email_cc=None,
                                    email_bcc=None,
                                    attachments=None,
                                    references=None,
                                    object_id=None,
                                    subtype='html',
                                    subtype_alternative=None,
                                    headers=None)
                                obj_mail_server.send_email(message=message_hrmanager,
                                                       mail_server_id=mail_server_record.id)
        return True


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    @api.constrains('name')
    def _check_duplication_leave_type(self):
        for rec in self:
            if rec.name:
                leave_type_rec = self.search([('id', '!=', rec.id),
                                              ('name', '=', rec.name)])
                if leave_type_rec:
                    raise ValidationError("Code must be unique!")

    cry_frd_leave = fields.Float('Carry Forward Leave',
                                 help='Maximum number of Leaves to be carry \
                                 forwarded!')
    name2 = fields.Char('Leave Type', translate=True)
    default_leave_allocation = fields.Integer('Default Annual Leave Allocation')
    weekend_calculation = fields.Boolean('Weekend Calculation')
    count_days_by = fields.Selection([('calendar_day', 'Calendar Days'),
                                      ('working_days_only', 'Working Days only')
                                      ], string="Count Days By",
             help="If Calendar Days : system will counts all calendar days in \
             leave request. \nIf Working Days only : system will counts all \
             days except public and weekly holidays in leave request. ",
             default='calendar_day')

    @api.multi
    def get_days(self, employee_id):
        # need to use `dict` constructor to create a dict per id
        today = datetime.strftime(datetime.today().date(), DSDF)
        hr_year_id = self.env['hr.holidays'].fetch_hryear(today)
        result = dict((id, dict(max_leaves=0, leaves_taken=0,
                                remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in self.ids)
        holidays = self.env['hr.holidays'].search([('employee_id', '=',
                                                    employee_id),
                                                  ('state', 'in', ['confirm',
                                                                   'validate1',
                                                                   'validate']),
                                                  ('holiday_status_id', 'in',
                                                   self.ids),
                                                  ('hr_year_id', '=',
                                                   hr_year_id)])
        for holiday in holidays:
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                if holiday.state == 'validate':
                    # note: add only validated allocation even for the virtual
                    # count; otherwise pending then refused allocation allow
                    # the employee to create more leaves than possible
                    status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        hr_holiday_rec = self.search([('name', operator, name)] + args, limit=limit)
        return hr_holiday_rec.name_get()

    @api.multi
    def name_get(self):
        res = []
        if not self._context.get('employee_id'):
            for record in self:
                res.append((record.id, record.name))
            return res
        for record in self:
            name = record and record.name or ''
            if not record.limit:
                name = name + ('  (%g remaining out of %g)' %
                               (record.virtual_remaining_leaves or 0.0,
                                record.max_leaves or 0.0))
            res.append((record.id, name))
        return res


class HrHolidayPublic(models.Model):
    '''
        This class stores a list of public holidays
    '''
    _name = 'hr.holiday.public'
    _description = 'Public holidays'

    @api.constrains('holiday_line_ids')
    def _check_holiday_line_year(self):
        '''
        The method used to Validate duplicate public holidays.
        @param self : Object Pointer
        @return : True or False
        ------------------------------------------------------
        '''
        for holiday in self:
            if holiday:
                for line in holiday.holiday_line_ids:
                    if line.holiday_date:
                        holiday_line_ids = line.search([('holiday_date', '=',
                                                         line.holiday_date),
                                                        ('holiday_id', '=',
                                                         line.holiday_id.id)])
                        if len(holiday_line_ids) > 1:
                            raise ValidationError(_('You can not create \
                            holiday for same date!'))
                    holiday_year = datetime.strptime(line.holiday_date, DSDF).year
                    if holiday.name != str(holiday_year):
                        raise ValidationError(_('You can not create holidays \
                        for different year!'))

    @api.constrains('name')
    def _check_public_holiday(self):
        for rec in self:
            pub_holiday_ids = rec.search([('name', '=', rec.name),
                                          ('id', '!=', rec.id)])
            if pub_holiday_ids and pub_holiday_ids.ids:
                raise ValidationError(_('You can not have multiple public \
                holiday for same year!'))

    name = fields.Char('Holiday', required=True, help='Name of holiday list')
    holiday_line_ids = fields.One2many('hr.holiday.lines', 'holiday_id',
                                       'Holidays')
    email_body = fields.Text('Email Body', default='Dear Manager,\n\nKindly \
    find attached pdf document containing Public Holiday List.\n\nThanks,')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('validated', 'Validated'),
                              ('refused', 'Refused'),
                              ('cancelled', 'Cancelled'), ], 'State',
                             index=True, readonly=True, default='draft')

    @api.multi
    def action_draft(self):
        '''
            Set state to draft
        '''
        self.write({'state':'draft'})
        return True

    @api.multi
    def action_cancel(self):
        '''
            Set state to cancelled
        '''
        self.write({'state': 'cancelled'})
        return True

    @api.multi
    def action_validate(self):
        '''
        Set state to validated and HR manager will notify via email and it 
        content pdf file of public holidays.
        '''
        file_name = 'HolidayList'  # Name of report file
        attachments = []
        email_body = ''  # To store email body text specified for each employee
        mail_obj = self.env["ir.mail_server"]
        data_obj = self.env['ir.model.data']
        emp_obj = self.env['hr.employee']
        for self_rec in self:
            mail_server_ids = self.env['ir.mail_server'].search([])
            if  mail_server_ids and mail_server_ids.ids:
                mail_server_id = mail_server_ids[0]
                email_from = mail_server_id.smtp_user
                if self_rec.email_body and email_from:
                    # fetch users who have rights of HR manager
                    res_user_rec = self.env['res.users'].search([('id', '!=', 1)])
                    res_user_ids = res_user_rec.filtered(lambda x :
                                                        x.has_group('hr.group_hr_manager')\
                                                         ).ids
                    emp_ids = emp_obj.search([('user_id', 'in', res_user_ids)])
                    # fetch work email of HR manager
                    work_email = list(set([str(emp.work_email or emp.user_id.login)
                                           for emp in emp_ids]))
                    if work_email:
                        # Create report. Returns tuple (True,filename) if successfuly
                        # executed otherwise (False,exception)
                        report_name = 'idn_holidays.public_holiday_report'
                        report = self.create_report(report_name, file_name)
                        if report[0]:
                            # Inserting file_data into dictionary with file_name as a key
                            attachments.append((file_name, report[1]))
                            email_body = self_rec.email_body
                            specific_email_body = email_body
                            message_app = mail_obj.build_email(
                                email_from=email_from,
                                email_to=work_email,
                                subject='Holiday list',
                                body=specific_email_body or '',
                                body_alternative=specific_email_body or '',
                                email_cc=None,
                                email_bcc=None,
                                reply_to=None,
                                attachments=attachments,
                                references=None,
                                object_id=None,
                                subtype='html',
                                subtype_alternative=None,
                                headers=None)
                            mail_obj.send_email(message=message_app,
                                                mail_server_id=mail_server_id.id)
            self_rec.write({'state': 'validated'})
        return True

    @api.multi
    def action_refuse(self):
        '''
        Sets state to refused
        '''
        for rec in self:
            rec.write({'state': 'refused'})
        return True

    @api.multi
    def action_confirm(self):
        '''
        Set state to confirmed
        '''
        for rec in self:
            if not rec.holiday_line_ids:
                raise ValidationError(_('Please add holidays!'))
            rec.write({'state': 'confirmed'})
        return True

    def create_report(self, report_name=False, file_name=False):
        '''
        Creates report from report_name that contains records of res_ids 
        and saves in report directory of module as 
        file_name.
        @param res_ids : List of record ids
        @param report_name : Report name defined in .py file of report
        @param file_name : Name of temporary file to store data
        @return: On success returns tuple (True,filename) 
                 otherwise tuple (False,execpotion)
        '''
        if not report_name or not self._ids:
            return (False, Exception('Report name and Resources \
            ids are required !'))
        try:
#            service = netsvc.LocalService(report_name);
            result, format = render_report(self.env.cr, self.env.uid,
                                           self._ids, report_name, {}, {})
        except Exception, e:
            return (False, str(e))
        return (True, result)


    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise Warning(_('You cannot delete a public holiday which is \
                not in draft state !'))
        return super(HrHolidayPublic, self).unlink()


class HrHolidayLines(models.Model):
    '''
       This model stores holiday lines
    '''
    _name = 'hr.holiday.lines'

    _description = 'Holiday Lines'

    holiday_date = fields.Date('Date', help='Holiday date', required=True)
    name = fields.Char('Reason', help='Reason for holiday')
    day = fields.Char('Day', help='Day')
    holiday_id = fields.Many2one('hr.holiday.public', 'Holiday List',
                                 help='Holiday list')

    @api.onchange('holiday_date')
    def onchange_holiday_date(self):
        '''
            This methods returns name of day of holiday_date
        '''
        if self.holiday_date:
            daylist = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                       'Saturday', 'Sunday']
            parsed_date = datetime.strptime(self.holiday_date, DSDF)
            day = parsed_date.weekday()
            self.day = str(daylist[day])


class HrEmployeeExtended(models.Model):
    _inherit = 'hr.employee'

    employee_leave_ids = fields.One2many('hr.holidays', 'employee_id',
                                         'Leaves')

    @api.multi
    def copy(self, default={}):
        default = default or {}
        default['employee_leave_ids'] = []
        return super(HrEmployeeExtended, self).copy(default)
