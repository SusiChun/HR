# -*- coding: utf-8 -*-

from dateutil import rrule
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF


class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    structure_id = fields.Many2one(related='contract_id.struct_id', string='Structure', readonly=False)
    structure_move_id = fields.Many2one(comodel_name='hr.payroll.structure', string='Structure Move')

    @api.onchange('contract_id')
    def _onchange_contract_bm(self):
        for row in self:
            row.structure_move_id = row.contract_id.struct_id.id

    @api.onchange('structure_id')
    def _onchange_structure_id(self):
        for row in self:
            row.struct_id = row.structure_id.id

    @api.multi
    def action_payslip_done(self):
        res = super(hr_payslip, self).action_payslip_done()
        contract = self.env['hr.contract'].browse(self.contract_id.id)
        contract.write({'struct_id' : self.structure_move_id.id})
        return res

    @api.multi
    def get_employee_contract_id(self):
        """
        This onchange method is used to add working day and input.
        """
        employee_id = self.employee_id
        date_from = self.date_from or False
        date_to = self.date_to or False
        contract_id = self.contract_id.id or False
        if date_from and date_to:
            current_date_from = date_from
            current_date_to = date_to
            date_from_cur = datetime.strptime(date_from, DSDF)
            frm_dt = datetime.strptime(date_from, DSDF).date()
            to_date = datetime.strptime(date_to, DSDF).date()

            dates = list(rrule.rrule(rrule.DAILY, dtstart=frm_dt,
                                     until=to_date))
            sunday = saturday = weekdays = 0
            for day in dates:
                if day.weekday() == 5:
                    saturday += 1
                elif day.weekday() == 6:
                    sunday += 1
                else:
                    weekdays += 1

            result = []
            res = {'code':'TTLPREVDAYINMTH', 'payslip_id': self.id, 'contract_id': self.contract_id.id,
                   'name':'Total number of days for previous month',
                   'number_of_days':len(dates), 'sequence': 2}
            result.append(res)
            res = {'code':'TTLPREVSUNINMONTH', 'payslip_id': self.id, 'contract_id': self.contract_id.id,
                   'name':'Total sundays in previous month',
                   'number_of_days':sunday, 'sequence': 3}
            result.append(res)
            res = {'code':'TTLPREVSATINMONTH', 'payslip_id': self.id, 'contract_id': self.contract_id.id,
                   'name':'Total saturdays in previous month',
                   'number_of_days':saturday, 'sequence': 4}
            result.append(res)
            res = {'code':'TTLPREVWKDAYINMTH', 'payslip_id': self.id, 'contract_id': self.contract_id.id,
                   'name':'Total weekdays in previous month',
                   'number_of_days':weekdays, 'sequence': 5}
            result.append(res)

        if employee_id:
            holiday_status_ids = self.env["hr.holidays.status"].search([])
            for holiday_status in holiday_status_ids:
                flag = False
                total_leave = 0
                for payslip_data in result:
                    if payslip_data.get("code") == holiday_status.name:
                        flag = True
                if not flag:
                    # Modify by Baim - Bug fix holiday in payslip
                    leaves = self.env['hr.holidays'].search([('type','=','remove'), ('state','in',('validate1','validate')), ('employee_id','=',employee_id.id), ('holiday_status_id.name','=',holiday_status.name), ('date_from', '>', date_from), ('date_from', '<', date_to), ('date_to', '>', date_from), ('date_to', '<', date_to)])
                    for leave in leaves:
                        total_leave += leave.number_of_days_temp
                    res = {'code' : holiday_status.name,
                           'payslip_id': self.id, 'contract_id': self.contract_id.id,
                           'name' : holiday_status.name2,
                           'number_of_days' : total_leave,
                           'sequence' : 0
                        }
                    result.append(res)
        for x in result:
            self.worked_days_line_ids.create(x)


class hr_payslip_employees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    structure_id = fields.Many2one(comodel_name='hr.payroll.structure', string='Structure')

    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'structure_id': data['structure_id'],
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
                'company_id': employee.company_id.id,
            }
            if slip_data['value'].get('contract_id'):
                payslips = self.env['hr.payslip'].create(res)
                payslips.get_employee_contract_id()
                payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}
