# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class Regular(models.Model):
    _inherit = "attendance.regular"

    state_select = fields.Selection([
        ('To Submit', 'Draft'),
        ('requested', 'Confirm Manager'),
        ('Confirm Manager', 'Confirm HRD'),
        ('Confirm HRD', 'Approved')], 
        default='To Submit',
        track_visibility='onchange',
        string='State',
        copy=False
    )

    att_number = fields.Char(string="Number")
    from_date = fields.Datetime(
        string='From Date',
        required=True,
        default=False,
    )
    to_date = fields.Datetime(
        string='To Date',
        required=True,
        default=False,
    )

    @api.multi
    def submit_reg(self):
        self.ensure_one()
        self.sudo().write({
            'state_select': 'requested'
        })
        seq_no = self.env['ir.sequence'].get('att.number')
        self.att_number = seq_no
        return

    @api.onchange('from_date')
    def set_hour_from(self):
        if self.from_date:
            date = datetime.strptime(self.from_date, '%Y-%m-%d %H:%M:%S')
            newdate = date.replace(hour=00, minute=00, second=00)
            self.from_date = newdate

    @api.onchange('to_date')
    def set_hour_to(self):
        if self.to_date:
            date = datetime.strptime(self.to_date, '%Y-%m-%d %H:%M:%S')
            newdate = date.replace(hour=11, minute=00, second=00)
            self.to_date = newdate

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state_select not in ['To Submit'] and rec.env.user.has_group('brt_health_reimburse.manager') or rec.state_select not in ['To Submit'] and rec.env.user.has_group('hr.group_hr_manager'):
                return super(Regular, rec).unlink()
            elif rec.state_select in ['To Submit']:
                return super(Regular, rec).unlink()
            else:
                raise UserError(_('Employee can only delete request on Draft state.'))

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
                x.hr_attendance_id.write({
                    'check_in': x.check_in_correction, 
                    'check_out': x.check_out_correction,
                    'note': 'Absensi Sebelum Correction ' + in_str + ' s/d ' + out_str,
                    'is_correction': True,
                    'correction_reason': x.reg_reason,
                    'correction_duration': x.overtime,
                    'correction_amount': x.overtime_amount,
                    'correction_meal': x.meal_allowance,
                    'correction_total': x.ot_total,
                })
            if not x.hr_attendance_id and x.check_in_correction and x.check_out_correction:
                vals = {
                    'employee_id': x.employee_id.id,
                    'check_in': x.check_in_correction,
                    'check_out': x.check_out_correction,
                    'note': 'Create By Attendance Correction',
                    'is_correction': True,
                    'correction_reason': x.reg_reason,
                    'correction_duration': x.overtime,
                    'correction_amount': x.overtime_amount,
                    'correction_meal': x.meal_allowance,
                    'correction_total': x.ot_total,
                }
                atten = self.env['hr.attendance'].sudo().create(vals)
            self.write({
                'state_select': 'Confirm HRD'
            })


class RegularLine(models.Model):
    _inherit = 'attendance.correction.line'

    is_early_ot = fields.Boolean(string="Early Overtime")
    start_shift = fields.Float(string="Shift Start")

    @api.onchange('check_in_correction', 'check_out_correction')
    def check_correction(self):
        if self.check_in_correction and self.check_out_correction:
            if self.check_out_correction <= self.check_in_correction:
                raise UserError(_("Tanggal check out correction harus lebih besar dari check in correction"))

    @api.onchange('overtime','marks','security')
    def _change_overtime(self):
        if self.check_in_correction and self.check_out_correction:
            check_in = datetime.strptime(self.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            check_out = datetime.strptime(self.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            date_in = datetime.strftime(check_in, "%Y-%m-%d")
            date_out = datetime.strftime(check_out, "%Y-%m-%d")
            in_date = datetime.strptime(date_in, '%Y-%m-%d')
            out_date = datetime.strptime(date_out, '%Y-%m-%d')
            if in_date == out_date:
                if not self.is_early_ot or in_date == out_date:
                    for line in self:
                        if line.security != True:
                            if line.overtime > 0.0:
                                if line.overtime > line.max_overtime:
                                    line.overtime = None
                                    raise UserError(_('Total jam lembur tidak boleh melebihi ketentuan!!'))

    @api.constrains('overtime', 'marks', 'security')
    def _check_overtime(self):
        if self.check_in_correction and self.check_out_correction:
            check_in = datetime.strptime(self.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            check_out = datetime.strptime(self.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
            date_in = datetime.strftime(check_in, "%Y-%m-%d")
            date_out = datetime.strftime(check_out, "%Y-%m-%d")
            in_date = datetime.strptime(date_in, '%Y-%m-%d')
            out_date = datetime.strptime(date_out, '%Y-%m-%d')
            if in_date == out_date:
                if not self.is_early_ot:
                    for line in self:
                        if line.security != True:
                            if line.overtime > 0.0:
                                if line.overtime > line.max_overtime:
                                    raise ValidationError(_(
                                        'Total jam lembur tidak boleh melebihi ketentuan!'))
            # if in_date != out_date:
            #         for line in self:
            #             if line.security != True:
            #                 if line.overtime > 0.0:
            #                     print line.overtime
            #                     print line.max_overtime
            #                     print "======================"
            #                     if line.overtime > line.max_overtime:
            #                         raise ValidationError(_(
            #                             'Total jam lembur tidak boleh melebihi ketentuan!!!'))

    @api.multi
    def recalculate_ot(self):
        if not self.check_in_correction:
            raise UserError(_("Please set Check in correction first"))
        shifts = self.atten_id.employee_id.calendar_id.attendance_ids
        if self.is_early_ot:
            for shift in shifts:
                day_shift = dict(shift._fields['dayofweek'].selection).get(shift.dayofweek)
                if self.hari == day_shift:
                    self.start_shift = shift.hour_from
                    check_in = datetime.strptime(self.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    check_in_hour = datetime.strftime(check_in, "%H:%M")
                    start_times = str(timedelta(hours=self.start_shift))
                    start_time = datetime.strptime(start_times, '%H:%M:%S')
                    start_hour = datetime.strftime(start_time, "%H:%M")

                    time_start = datetime.strptime(start_hour, '%H:%M')
                    time_check = datetime.strptime(check_in_hour, '%H:%M')
                    result = time_start - time_check
                    t_seconds = result.total_seconds()
                    total_hour = t_seconds/3600.0
                    self.overtime += total_hour
                    self.max_overtime += total_hour
        if self.atten_id.employee_id.grade == '1' or self.atten_id.employee_id.grade == '2':
            min_hour_overtime = "17:30:00"
        elif self.atten_id.employee_id.grade == '3':
            min_hour_overtime = "19:00:00"
        elif self.atten_id.employee_id.grade == '4' or self.atten_id.employee_id.grade == '5':
            min_hour_overtime = "21:00:00"
        else:
            min_hour_overtime = "00:00:00"
        curr_checkin = datetime.strptime(self.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        emp_shift = datetime.strftime(curr_checkin, '%Y-%m-%d ' + min_hour_overtime)
        emp_shift_time = datetime.strptime(emp_shift, '%Y-%m-%d %H:%M:%S')
        emp_checkout_time = datetime.strptime(self.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
        calculate = emp_checkout_time - emp_shift_time
        calculate_second = calculate.total_seconds()
        time_total = calculate_second/3600.0
        self.overtime += time_total
        self.max_overtime = time_total

    @api.onchange('check_out_correction')
    def check_max_overtime(self):
        for x in self:
            if x.check_out_correction and x.grade and x.marks not in('Libur Nasional','Hari Libur'):
                datetime1 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                # x.max_overtime = (float(time)) - x.min_hour_overtime
                check_out = datetime.strftime(datetime1, "%H:%M")
                min_hour = str(timedelta(hours=x.min_hour_overtime))
                out = datetime.strptime(check_out, '%H:%M')
                min_out = datetime.strptime(min_hour, '%H:%M:%S')
                res = out - min_out
                res_seconds = res.total_seconds()
                res_total = res_seconds/3600.0
                x.max_overtime = res_total
            if x.check_out_correction and x.check_in_correction and x.grade and x.marks in ('Libur Nasional', 'Hari Libur'):
                datetime1 = datetime.strptime(x.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                datetime2 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time1 = datetime.strftime(datetime1, "%H.%M")
                time2 = datetime.strftime(datetime2, "%H.%M")
                print ("heehheheheeeeeeeeeeeeeee",time1)
                print ("heehheheheeeeeeeeeeeeeee",time2)
                x.max_overtime = (float(time2)) - (float(time1))
                print (x.max_overtime)

    @api.multi
    @api.depends('check_out_correction','check_out')
    def compute_max_overtime(self):
        for x in self:
            if x.check_out_correction and x.grade and x.marks not in('Libur Nasional','Hari Libur'):
                datetime1 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                # x.max_overtime = (float(time)) - x.min_hour_overtime
                check_out = datetime.strftime(datetime1, "%H:%M")
                min_hour = str(timedelta(hours=x.min_hour_overtime))
                out = datetime.strptime(check_out, '%H:%M')
                min_out = datetime.strptime(min_hour, '%H:%M:%S')
                res = out - min_out
                res_seconds = res.total_seconds()
                res_total = res_seconds/3600.0
                x.max_overtime = res_total
            if x.check_out and x.grade and x.marks not in('Libur Nasional','Hari Libur') and not x.check_out_correction:
                datetime1 = datetime.strptime(x.check_out, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                # x.max_overtime = (float(time)) - x.min_hour_overtime
                check_out = datetime.strftime(datetime1, "%H:%M")
                min_hour = str(timedelta(hours=x.min_hour_overtime))
                out = datetime.strptime(check_out, '%H:%M')
                min_out = datetime.strptime(min_hour, '%H:%M:%S')
                res = out - min_out
                res_seconds = res.total_seconds()
                res_total = res_seconds/3600.0
                x.max_overtime = res_total
            if x.check_out_correction and x.check_in_correction and x.grade and x.marks in ('Libur Nasional', 'Hari Libur'):
                datetime1 = datetime.strptime(x.check_in_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                datetime2 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time1 = datetime.strftime(datetime1, "%H.%M")
                time2 = datetime.strftime(datetime2, "%H.%M")
                x.max_overtime = (float(time2)) - (float(time1))

class approve_attendance(models.TransientModel):
    _inherit = "approve.attendance"

    @api.multi
    def approve_masal(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['attendance.regular'].browse(active_ids):
            if not record.env.user.has_group('hr.group_hr_manager'):
                raise UserError(_('Only HR Manager can Approve this Request.'))
            else:
                record.regular_approval()
        return {'type': 'ir.actions.act_window_close'}


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    is_correction = fields.Boolean(string="Is Correction")
    correction_reason = fields.Char(string="Reason")
    correction_duration = fields.Float(string="OT Duration")
    correction_amount = fields.Float(string="OT Amount")
    correction_meal = fields.Float(string="Meal Allowance")
    correction_total = fields.Float(string="OT Total")
