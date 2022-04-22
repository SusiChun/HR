# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class RegularLine(models.Model):
    _name = 'attendance.correction.check'
    _description = 'Attendance Correction Check'
    _order = 'check_in asc'

    atten_id            = fields.Many2one('attendance.regular.check')
    employee_id         = fields.Many2one(comodel_name='hr.employee',string="Employee")
    security            = fields.Boolean(related='employee_id.job_id.security')
    grade               = fields.Selection([('1', '1'),
                                   ('2', '2'),
                                   ('3', '3'),
                                   ('4', '4'),
                                   ('5', '5'),
                                   ('6', '6'),
                                     ('7', '7'),
                                     ('8', '8')],related='employee_id.grade',string='Grade')
    min_hour_overtime = fields.Float(related='atten_id.min_hour_overtime',string='Min Hour Overtime')
    max_overtime        = fields.Float(string='Max Overtime',default=0.0,compute='compute_max_overtime',store=True)
    hr_attendance_id    = fields.Many2one(comodel_name='hr.attendance', string="HR Attendance")
    check_in            = fields.Datetime(string='Check In')
    hari                = fields.Char(string='Day')
    check_out           = fields.Datetime(string='Check Out')
    check_in_correction = fields.Datetime(string='Check In Correction')
    check_out_correction = fields.Datetime(string='Check Out Correction')
    reg_reason          = fields.Text(string='Reason')
    overtime            = fields.Float(string='OT Duration')
    overtime_amount     = fields.Float(string='OT Amount',compute='compute_ot_amount',store=True)
    meal_allowance      = fields.Float(string='Meal Allowance')
    marks               = fields.Char(string='Marks')
    basic_salary             = fields.Float(string='Basic Salary',related='atten_id.basic_salary',store=True)
    state_select            = fields.Selection([('To Submit', 'To Submit'), ('requested', 'Requested'),
                                     ('Confirm Manager', 'Confirm Manager'),
                                     ('Confirm HRD', 'Confirm HRD')
                                     ], default='To Submit', related='atten_id.state_select', string='State')
    date_check = fields.Date(string="Date")

    @api.multi
    @api.depends('overtime','marks','security')
    def compute_ot_amount(self):
        for x in self:
            if x.security == True:
                if x.overtime > 0.0:
                    x.overtime_amount = (x.overtime / 173) * x.basic_salary
            else:
                if x.marks != 'Libur Nasional':
                    if x.overtime > 0.0:
                        x.overtime_amount = (x.overtime / 173) * x.basic_salary
                if x.marks == 'Libur Nasional':
                    if x.overtime > 0 or x.overtime <= 7:
                        x.overtime_amount = (x.overtime / 173) * x.basic_salary
                    if x.overtime > 7.0:
                        setelah = 0.0
                        setelah = (x.overtime - 7.0)
                        x.overtime_amount = (7.0 * 1.5) + ((setelah *2) / 173) * x.basic_salary



    @api.onchange('overtime','security')
    def change_ot(self):
        for x in self:
            if x.security == True:
                if x.overtime > 0.0:
                    x.overtime_amount = (x.overtime / 173) * x.basic_salary
            else:
                if x.marks != 'Libur Nasional':
                    if x.overtime > 0.0:
                        x.overtime_amount = (x.overtime / 173) * x.basic_salary
                if x.marks == 'Libur Nasional':
                    if x.overtime > 0.0 and  x.overtime <= 7.0:
                        x.overtime_amount = (x.overtime / 173) * x.basic_salary
                    if x.overtime > 7.0:
                        setelah = 0.0
                        setelah = (x.overtime - 7.0)
                        x.overtime_amount = (7.0 * 1.5) + ((setelah *2) / 173) * x.basic_salary

    @api.onchange('check_out_correction')
    def check_max_overtime(self):
        for x in self:
            if x.check_out_correction and x.grade and x.marks != 'Libur Nasional':
                datetime1 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                x.max_overtime = (float(time)) - x.min_hour_overtime

    @api.multi
    @api.depends('check_in','check_out')
    def change_date(self):
        if self.check_in:
            self.check_in_correction = self.check_in
        if self.check_out:
            self.check_out_correction = self.check_out

    @api.multi
    @api.depends('check_out_correction','check_out')
    def compute_max_overtime(self):
        for x in self:
            if x.check_out_correction and x.grade and x.marks != 'Libur Nasional':
                datetime1 = datetime.strptime(x.check_out_correction, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                x.max_overtime = (float(time)) - x.min_hour_overtime
            if x.check_out and x.grade and x.marks != 'Libur Nasional' and not x.check_out_correction:
                datetime1 = datetime.strptime(x.check_out, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                time = datetime.strftime(datetime1, "%H.%M")
                x.max_overtime = (float(time)) - x.min_hour_overtime

    @api.constrains('overtime','marks','security')
    def _check_overtime(self):
        for line in self:
            if line.marks != 'Libur Nasional' and line.security != True:
                if line.overtime > 0.0:
                    if line.overtime > line.max_overtime :
                        raise ValidationError(_(
                                'Total jam lembur tidak boleh melebihi ketentuan!'))



    @api.onchange('overtime','marks','security')
    def _change_overtime(self):
        for line in self:
            if line.marks != 'Libur Nasional' and line.security != True:
                print ("gkgkgkgkggkgkgkgkgkgkgkgkgkgkgkgk")
                if line.overtime > 0.0:
                    if line.overtime > line.max_overtime:
                        line.overtime = None
                        raise UserError(_('Total jam lembur tidak boleh melebihi ketentuan!!'))
