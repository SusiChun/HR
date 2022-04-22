# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning


class hr_employee(models.Model):
    _inherit= 'hr.employee'

    total_pay_salary = fields.Float('Total Gross in Years', compute='compute_total_salary', store=True)
    total_pay_balance = fields.Float('Gross Balance')
    total_pph23 = fields.Float('Total PPH21 in Years', compute='compute_total_salary', store=True)
    total_pph23_balance = fields.Float('PPH21 Balance')
    pengurang_pajak = fields.Float('Total Pengurang Pajak in Years', compute='compute_total_salary', store=True)
    pengurang_pajak_balance = fields.Float('Pengurang Pajak Balance')
    penambah_pajak = fields.Float('Total Penambah Pajak in Years', compute='compute_total_salary', store=True)
    penambah_pajak_balance = fields.Float('Penambah Pajak Balance')
    rate_jamsostek = fields.Float('Rate Jamsostek')
    rate_bpjs = fields.Float('Rate BPJS')
    date_join = fields.Date('Date Joined', compute='compute_date_join', store=True)
    have_january_slip = fields.Boolean('January Slip ?', compute='compute_total_salary', store=True)
    first_slip_join = fields.Boolean('First Slip Join ?', compute='compute_total_salary', store=True)
    pphprediksipen = fields.Float('PPH Prediksi', compute='compute_total_salary', store=True)

    @api.multi
    @api.depends('slip_ids.state', 'total_pay_balance', 'total_pph23_balance', 'pengurang_pajak_balance', 'penambah_pajak_balance')
    def compute_total_salary(self):
        for x in self:
            total = 0.0
            pph23 = 0.0
            pphprediksipen = 0.0
            pengurang_pajak = 0.0
            penambah_pajak = 0.0
            first_slip_join = False
            date_start = time.strftime('%Y-01-01 00:00:00')
            date_end = time.strftime('%Y-12-31 23:50:50')
            employee_id = x.id or self._origin.id
            data = self.env[('hr.payslip.line')].search([('employee_id', '=', employee_id), ('slip_id.state', '=', 'done'), ('slip_id.date_to', '>=', date_start), ('slip_id.date_to', '<=', date_end)])
            for y in data:
                if y.code == 'GROSS':
                    total += y.total
                if y.code == 'PPH21PENAMPUNG':
                    pph23 += y.total
                if y.code == 'JHTE' or y.code == 'JPE':
                    pengurang_pajak += y.total
                if y.code == 'JKKER' or y.code == 'JKMER':
                    penambah_pajak += y.total
                if y.slip_id.date_to[5:7] == '01':
                    x.have_january_slip = True
                if not x.total_pay_salary:
                    if y.slip_id.month_date == y.slip_id.month_join:
                        first_slip_join = True

                print '>>>>>>>>>>>>>>>>>>>>>1',y.slip_id.month_date  
                print '>>>>>>>>>>>>>>>>>>>>>1',x.pphprediksipen 
                if not x.pphprediksipen or x.have_january_slip:
                    if y.code == 'PPHPREDIKSIPEN':
                        # pphprediksipen = y.total
                        x.pphprediksipen = y.total
                # else:
                    # pphprediksipen = x.pphprediksipen

            # x.pphprediksipen = pphprediksipen
            x.first_slip_join = first_slip_join
            x.total_pay_salary = total + x.total_pay_balance
            x.total_pph23 = pph23 + x.total_pph23_balance
            x.pengurang_pajak = pengurang_pajak + x.pengurang_pajak_balance
            x.penambah_pajak = penambah_pajak + x.penambah_pajak_balance

    @api.multi
    @api.depends('contract_ids.state', 'contract_ids.date_start')
    def compute_date_join(self):
        for x in self:
            employee_id = x.id or self._origin.id
            data = self.env[('hr.contract')].search([('employee_id', '=', employee_id)], order='id asc', limit=1)
            x.date_join = data.date_start
