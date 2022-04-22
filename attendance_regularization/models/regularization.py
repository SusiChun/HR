# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DSDTF
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from dateutil import relativedelta

class Holiday(models.Model):
    _inherit = 'hr.holidays'

    start_date = fields.Date(string='Start Date', compute='compute_tgl', store=True)
    end_date = fields.Date(string='End Date', compute='compute_tgl', store=True)

    @api.depends('date_from', 'date_to')
    @api.multi
    def compute_tgl(self):
        for x in self:
            if x.date_from:
                dt_from = datetime.strptime(x.date_from, '%Y-%m-%d %H:%M:%S').date()
                x.start_date = dt_from
            if x.date_to:
                dt_to = datetime.strptime(x.date_to, '%Y-%m-%d %H:%M:%S').date()
                x.end_date = dt_to


class Regular1(models.Model):
    _name = 'attendance.regular'
    _description = 'Approval Request'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(compute="_compute_name")
    company_id      = fields.Many2one(comodel_name='res.company', string='Company',
                        default = lambda self: self.env['res.company']._company_default_get('attendance.regular')
                        )
    employee_id = fields.Many2one(comodel_name='hr.employee', required=True, string='Employee',
                                  default=_default_employee)
    security = fields.Boolean(related='employee_id.job_id.security')
    from_date = fields.Datetime(string='From Date', required=True,default=datetime.utcnow().strftime('%Y-%m-01 00:00:00'))
    to_date = fields.Datetime(string='To Date', required=True,
                              default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1,hours=4,minutes=59,seconds=00)))
    state_select = fields.Selection([('To Submit', 'To Submit'), ('requested', 'Requested'),
                                     ('Confirm Manager', 'Confirm Manager'),
                                     ('Confirm HRD', 'Confirm HRD')
                                     ], default='To Submit', track_visibility='onchange', string='State', copy=False)
    attendance_ids = fields.One2many('attendance.correction.line', 'atten_id')
    overtime_total = fields.Float(string='OT Total', compute='compute_ot_total', store=True)
    grade = fields.Selection([('1', '1'),
                              ('2', '2'),
                              ('3', '3'),
                              ('4', '4'),
                              ('5', '5'),
                              ('6', '6'),
                              ('7', '7'),
                              ('8', '8')], related='employee_id.grade', string='Grade')
    min_hour_overtime = fields.Float(string='Min Hour Overtime')
    basic_salary = fields.Float(string='Basic Salary', compute='compute_salary')

    @api.depends('employee_id', 'from_date', 'to_date')
    @api.multi
    def _compute_name(self):
        for x in self:
            if x.employee_id and x.from_date and x.to_date:
                x.name = "%s/%s/%s" % (x.employee_id.name, x.from_date, x.to_date)

    @api.multi
    @api.depends('employee_id')
    def compute_salary(self):
        for x in self:
            kontrak = self.env['hr.contract'].search(
                [('employee_id', '=', x.employee_id.id),
                 ('state', '=', 'pending'),
                 ], limit=1)
            if kontrak:
                x.basic_salary = kontrak.wage

    @api.multi
    @api.depends('attendance_ids.meal_allowance', 'attendance_ids.overtime_amount')
    def compute_ot_total(self):
        for record in self:
            meal_allow = sum(line.meal_allowance for line in record.attendance_ids)
            ot_amount = sum(line.overtime_amount for line in record.attendance_ids)
            record.overtime_total = ot_amount + meal_allow

    @api.multi
    def unlink(self):
        for x in self:
            if x.attendance_ids:
                x.attendance_ids.unlink()
        return super(Regular1, self).unlink()

    @api.onchange('employee_id')
    def compute_salary(self):
        for x in self:
            kontrak = self.env['hr.contract'].search(
                [('employee_id', '=', x.employee_id.id),
                 ('state', '=', 'pending'),
                 ], limit=1)
            if kontrak:
                x.basic_salary = kontrak.wage

    @api.onchange('employee_id', 'from_date', 'to_date')
    def attendance_change(self):
        if self.employee_id and self.from_date and self.to_date:
            if self.employee_id.grade == '1' or self.employee_id.grade == '2':
                self.min_hour_overtime = 17.30
            elif self.employee_id.grade == '3':
                self.min_hour_overtime = 19.00
            elif self.employee_id.grade == '4' or self.employee_id.grade == '5':
                self.min_hour_overtime = 21.00
            else:
                self.min_hour_overtime = 0.0
            data = []
            # date_from1 = datetime.strptime(self.from_date, '%Y-%m-%d %H:%M:%S').date()
            # print (date_from1,'date_from1')
            # tgl = datetime.strftime(date_from1, '%Y-%m-%d')
            # print (tgl, 'tgl')
            # time = '00:00:00'
            # date_check_form= tgl +time
            # print(date_check_form, 'date_check_form')

            date_from = fields.Date.from_string(self.from_date)
            date_to = fields.Date.from_string(self.to_date)
            delta = date_to - date_from
            if delta.days < 0:
                self.attendance_ids = None
                return None
            for n in range(delta.days + 1):
                data.append((0, 0, {
                    'employee_id': self.employee_id.id,
                    'check_in': (date_from + timedelta(days=n)),
                    'state': self.state_select,
                }))
            self.attendance_ids = data

    @api.multi
    def generate_attendance(self):
        attendance = self.env['hr.attendance'].search(
            [('check_in', '>=', self.from_date),
             ('check_in', '<=', self.to_date), ('employee_id', '=', self.employee_id.id),
             ])
        if self.employee_id.grade == '1' or self.employee_id.grade == '2':
            self.min_hour_overtime = 17.30
        elif self.employee_id.grade == '3':
            self.min_hour_overtime = 19.00
        elif self.employee_id.grade == '4' or self.employee_id.grade == '5':
            self.min_hour_overtime = 21.00
        else:
            self.min_hour_overtime = 0.0
            # attendance = self.env['hr.attendance'].search(
            #     [('check_in', '>=', self.from_date),
            #      ('check_out', '<=', self.to_date), ('employee_id', '=', self.employee_id.id),
            #      ])
        if self.attendance_ids:
            for line in self.attendance_ids:
                check1 = datetime.strptime(line.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                check = datetime.strftime(check1, '%Y-%m-%d')
                print ("ini generate attendance")
                for x in attendance:
                    date = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S').date()
                    datetime1 = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    datetime2 = datetime.strftime(datetime1, '%Y-%m-%d')
                    time = datetime.strftime(datetime1, "%H:%M:%S")
                    jam = '08:30:00'
                    if check == datetime2:
                        line.write({'check_in': x.check_in,
                                    'check_out': x.check_out,
                                    'hr_attendance_id': x.id,
                                    'marks': ' '
                                    })
                        if time > jam:
                            line.write({'marks': 'Telat'})
                if not line.hr_attendance_id and not line.check_out:
                    line.write({'marks': 'Alpha'})
                day = datetime.strptime(line.check_in, '%Y-%m-%d %H:%M:%S').strftime("%A")
                public_holiday = self.env['hr.holiday.lines'].search(
                    [('holiday_date', '=', check)
                     ], limit=1, order='holiday_date desc')
                if day == 'Saturday' or day == 'Sunday':
                    line.write({'marks': 'Hari Libur'})
                if public_holiday:
                    line.write({'marks': 'Libur Nasional'})
                if line.check_in:
                    line.write({'hari': day})
                cuti = self.env['hr.holidays'].search(
                    [('start_date', '<=', check),
                     ('end_date', '>=', check), ('employee_id', '=', line.employee_id.id),
                     ('state', '=', 'validate'), ('type', '=', 'remove')
                     ])
                if cuti:
                    line.write({'marks': 'Cuti'})

    @api.multi
    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state_select': 'requested'
        })
        return

    @api.multi
    def reject(self):
        self.sudo().write({
            'state_select': 'To Submit'
        })
        return

    @api.constrains('from_date', 'to_date')
    def _check_date(self):
        for att in self:
            domain = [
                ('from_date', '<=', att.to_date),
                ('to_date', '>=', att.from_date),
                ('employee_id', '=', att.employee_id.id),
                ('id', '!=', att.id),
                ('state_select', 'in', ['To Submit', 'requested']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 attendance correction that overlaps on same day!'))

    @api.multi
    def regular_approval(self):
        for x in self.attendance_ids:
            check = datetime.strptime(x.check_in,'%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            datetime2 = datetime.strftime(check, '%Y-%m-%d %H:%M:%S')
            in_str = str(datetime2)
            if x.hr_attendance_id and x.check_in_correction and x.check_out_correction:
                out_str = 'Tidak Check Out'
                if x.check_out :
                    check_out = x.check_out
                    check2 = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    datetime3 = datetime.strftime(check2, '%Y-%m-%d %H:%M:%S')
                    out_str = str(datetime3)
                x.hr_attendance_id.write({'check_in': x.check_in_correction, 'check_out': x.check_out_correction,
                                          'note': 'Absensi Sebelum Correction ' + in_str + ' s/d ' + out_str})
            if not x.hr_attendance_id and x.check_in_correction and x.check_out_correction:
                vals = {
                    'employee_id': x.employee_id.id,
                    'check_in': x.check_in_correction,
                    'check_out': x.check_out_correction,
                    'note': 'Create By Attendance Correction'
                }
                atten = self.env['hr.attendance'].sudo().create(vals)
            self.write({
                'state_select': 'Confirm HRD'
            })

    @api.multi
    def confirm_manager(self):
        self.write({
            'state_select': 'Confirm Manager'
        })
        return


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    note = fields.Text(string="Note")


class approve_attendance(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "approve.attendance"
    _description = "Approve attendance correction"

    @api.multi
    def approve_masal(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['attendance.regular'].browse(active_ids):
            record.regular_approval()
        return {'type': 'ir.actions.act_window_close'}
