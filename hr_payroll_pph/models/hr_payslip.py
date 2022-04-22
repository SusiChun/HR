# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class hr_payslip(models.Model):
    _inherit        = 'hr.payslip'

    month_date      = fields.Integer('Month Payslip', compute='compute_month_date', store=True)
    month_join      = fields.Integer('Joined Month', compute='compute_month_date', store=True)
    working_days    = fields.Integer('Working Days', compute='compute_month_date', store=True)
    rapel_amount    = fields.Float('Rapel Amount', compute='compute_month_date', store=True)
    total_attend    = fields.Float('Total Attend', compute='compute_attends', store=True)
    total_late      = fields.Float('Total Late', compute='compute_attends', store=True)
    total_overtime  = fields.Float('Total Overtime', compute='compute_attends', store=True)
    total_holiday   = fields.Float('Total Public Holiday', compute='compute_attends', store=True)

    @api.multi
    @api.depends('contract_id', 'date_from', 'date_to')
    def compute_attends(self):
        for x in self:
            if x.date_to and x.contract_id:
                date_from = datetime.strptime(x.date_from, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")
                date_to = datetime.strptime(x.date_to, '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S")
                total_attend = 0.0
                total_late = 0.0
                jam = 0.0
                menit = 0.0
                attends = x.env[('hr.attendance')].search([('employee_id', '=', x.employee_id.id), ('check_in', '>=', x.date_from), ('check_in', '<=', x.date_to)])
                for y in attends:
                    total_attend += 1
                    check_in = datetime.strptime(y.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    check_in = datetime.strftime(check_in, "%H:%M:%S")
                    # Hitung Late
                    jam = int(check_in[-8:-6])
                    # jam = 8
                    menit = int(check_in[-5:-3])
                    # menit = 35
                    d1 = datetime(1992,11,06,8,30,0)
                    d2 = datetime(1992,11,06,jam,menit,0)
                    diff = relativedelta(d2, d1)
                    if diff.minutes > 0:
                        total_late += diff.minutes
                        print 'BBBBBBBBBBBBBBBBB>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',total_attend,y.check_in
                        # print 'BBBBBBBBBBBBBBBBB>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',total_attend,jam
                        # print 'BBBBBBBBBBBBBBBBB>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',total_attend,menit
                        print 'BBBBBBBBBBBBBBBBB>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',total_attend,diff.minutes
                x.total_attend = total_attend
                x.total_late = total_late

                # Overtime
                total_overtime = 0.0
                over = x.env[('attendance.regular')].search([('employee_id', '=', x.employee_id.id), ('from_date', '>', date_from), ('from_date', '<', date_to)])
                for y in over:
                    total_overtime += y.overtime_total
                x.total_overtime = total_overtime

                # Public Holiday
                total_holiday = 0.0
                total_holiday = x.env[('hr.holiday.lines')].search_count([('holiday_date', '>=', x.date_from), ('holiday_date', '<=', x.date_to)])
                x.total_holiday = total_holiday

    @api.multi
    @api.depends('contract_id', 'date_from', 'date_to')
    def compute_month_date(self):
        for x in self:
            if x.date_to:
                x.month_date = x.date_to[5:7]

                if x.employee_id.date_join:
                    start = datetime.strptime(x.date_to, '%Y-%m-%d')
                    ends = datetime.strptime(x.employee_id.date_join, '%Y-%m-%d')
                    diff = relativedelta(start, ends)
                    x.working_days = (diff.years * 365) + (diff.months * 30) + (diff.days)
                    x.month_join = x.employee_id.date_join[5:7]
                    # Hitung Rapel
                    month_date_from = 0.0
                    month_rapel_request = 0.0
                    month_rapel_approve = 0.0
                    last_wage = x.env[('hr.contract.wage')].search([('contract_id.employee_id', '=', x.employee_id.id)], order='id desc', limit=1)
                    last_slip = x.env[('hr.payslip.line')].search([('employee_id', '=', x.employee_id.id), ('code', '=', 'FS'), ('slip_id.state', '=', 'done')], order='id desc', limit=1)
                    if x.date_from:
                        month_date_from = int(x.date_from[5:7])
                    if last_wage.start_periode:
                        month_rapel_request = int(last_wage.start_periode[5:7])
                    if last_wage.date_rapel_approve:
                        month_rapel_approve = int(last_wage.date_rapel_approve[5:7])
                    if month_rapel_approve == month_date_from:
                        diff_wage = last_wage.total - last_slip.total
                        diff_month = int(month_date_from) - int(month_rapel_request)
                        # print ('>>>>>>>>>>> Selisih Gaji'),diff_wage
                        # print ('>>>>>>>>>>> Selisih Bulan'),diff_month
                        x.rapel_amount = diff_wage * diff_month

    # Disable payslip double for define bonus salary rule
    @api.constrains('date_from', 'date_to', 'employee_id', 'contract_id')
    def _constraint_from_date_to_to_date(self):
        return True

    @api.multi
    def unlink(self):
        if any(self.filtered(lambda payslip: payslip.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
        return super(hr_payslip, self).unlink()
