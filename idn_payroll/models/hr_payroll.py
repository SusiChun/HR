# -*- coding:utf-8 -*-

from dateutil import rrule
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF
from odoo.exceptions import ValidationError


class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    branch_id = fields.Char("Branch ID", size=48)
    # Added by Baim
    partner_id = fields.Many2one('res.partner', 'Account Holder', ondelete='cascade', index=True, domain=[])


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    code = fields.Char('Code', size=52, required=False, readonly=False,
                       help="The code that can be used in the salary rules")
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False,
                                  help="The contract for which applied \
                                  this input")


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    id = fields.Integer('ID', readonly=True)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    cheque_number = fields.Char("Cheque Number", size=64)
    active = fields.Boolean('Pay', default=True)
    pay_by_cheque = fields.Boolean('Pay By Cheque')

    @api.constrains('date_from', 'date_to', 'employee_id', 'contract_id')
    def _constraint_from_date_to_to_date(self):
        """
        Check Payslip should be overlap or not
        """
        for rec in self:
            if rec.employee_id and rec.date_from and rec.date_to and \
            not rec.credit_note:
                self._cr.execute("""select id from hr_payslip where employee_id
                 = %s and id != %s and
                 ((date_from between %s and %s) or
                 (date_to between %s and %s))""", (rec.employee_id.id,
                                                      rec.id,
                                                      rec.date_from,
                                                      rec.date_to,
                                                      rec.date_from,
                                                      rec.date_to,))
                payslip_ids = self._cr.fetchall()
                if payslip_ids:
                    raise ValidationError("You can not have 2 payslip that \
                    overlaps on same Periods!")
            if rec.contract_id and rec.contract_id.state == 'close':
                raise ValidationError("You can not create payslip !\n \
                Employee's contract is Expired !")

    @api.onchange('date_from', 'date_to', 'employee_id', 'contract_id')
    def onchange_employee_contract_id(self):
        """
        This onchange method is used to add working day and input.
        """
        employee_id = self.employee_id or False
        date_from = self.date_from or False
        date_to = self.date_to or False
        contract_id = self.contract_id.id or False
        result = self.onchange_employee_id(date_from, date_to,
                                           self.employee_id.id, contract_id)
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

            res = {'code':'TTLPREVDAYINMTH',
                   'name':'Total number of days for previous month',
                   'number_of_days':len(dates), 'sequence': 2}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVSUNINMONTH',
                   'name':'Total sundays in previous month',
                   'number_of_days':sunday, 'sequence': 3}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVSATINMONTH',
                   'name':'Total saturdays in previous month',
                   'number_of_days':saturday, 'sequence': 4}
            result.get('value').get('worked_days_line_ids').append(res)
            res = {'code':'TTLPREVWKDAYINMTH',
                   'name':'Total weekdays in previous month',
                   'number_of_days':weekdays, 'sequence': 5}
            result.get('value').get('worked_days_line_ids').append(res)

        if employee_id:
            holiday_status_ids = self.env["hr.holidays.status"].search([])
            for holiday_status in holiday_status_ids:
                flag = False
                total_leave = 0
                for payslip_data in result["value"].get("worked_days_line_ids"):
                    if payslip_data.get("code") == holiday_status.name:
                        flag = True
                if not flag:
                    # Modify by Baim - Bug fix holiday in payslip
                    leaves = self.env['hr.holidays'].search([('type','=','remove'), ('state','in',('validate1','validate')), ('employee_id','=',employee_id.id), ('holiday_status_id.name','=',holiday_status.name), ('date_from', '>', date_from), ('date_from', '<', date_to), ('date_to', '>', date_from), ('date_to', '<', date_to)])
                    for leave in leaves:
                        total_leave += leave.number_of_days_temp
                    res = {'code' : holiday_status.name,
                           'name' : holiday_status.name2,
                           'number_of_days' : total_leave,
                           'sequence' : 0
                        }
                    result.get('value').get('worked_days_line_ids').append(res)

        if not employee_id:
            result.get('value', {}).update({'date_from' : date_from,
                                           'date_to': date_to,
                                           })
        result.get('value', {}).update({'employee_id' : employee_id,
                                       'state':'draft',
                                       'number': self.number,
                                       })
        return result

    @api.multi
    def compute_sheet(self):
        """
        Override this method to delete payslip line which have amount = 0.0
        """
        result = super(HrPayslip, self).compute_sheet()
        lines = []
        for payslip_rec in self:
            lines = [line_rec.id for line_rec in payslip_rec.line_ids
                  if line_rec.amount == 0]
        if lines:
            self.env['hr.payslip.line'].browse(lines).unlink()
        return result


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    @api.model
    def create(self, vals):
        """
        Override to to check state of payslip
        """
        slip_id = self.env['hr.payslip'].browse(vals.get('slip_id'))
        if slip_id and slip_id.state not in ['draft', 'verify']:
                raise ValidationError("You can not create Payslip lines.")
        return super(HrPayslipLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Override to check state of payslip
        """
        for rec in self:
            if rec.slip_id and rec.slip_id.state not in ['draft', 'verify']:
                raise ValidationError("You can not update Payslip lines.")
        return super(HrPayslipLine, self).write(vals)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    wage_to_pay = fields.Float('Wage To Pay')
    rate_per_hour = fields.Float('Rate per hour for part timer')
    # inherit name field to made required=false
    name = fields.Char('Contract Reference', required=False)

    @api.model
    def create(self, vals):
        """
        Override this method to update name from sequence.
        """
        vals.update({'name': self.env['ir.sequence'
                                      ].next_by_code('hr.contract')})
        return super(HrContract, self).create(vals)

    @api.model
    def reminder_to_change_year_number(self):
        curr_date = datetime.now()
        contract_seq = self.env.ref('idn_payroll.reset_contract_name')
        if contract_seq and curr_date.day == 1 and curr_date.month == 1:
            contract_seq.write({'number_next': 1})
        return True


# class HrEmployee(models.Model):
#     _inherit = 'hr.employee'
#
#     @api.model
#     def search(self, args, offset=0, limit=None, order=None, count=False):
#         """
#             Override Search method for put filter on current working status.
#         """
#         context = self._context
#         if context and context.get('batch_start_date') and \
#         context.get('batch_end_date'):
#             batch_start_date = context.get('batch_start_date')
#             batch_end_date = context.get('batch_end_date')
#             active_contract_employee_list = []
#             domain = ['|', ('date_end', '>=', batch_start_date),
#                       ('date_end', '=', False),
#                       ('date_start', '<=', batch_end_date)]
#             contract_ids = self.env['hr.contract'].search(domain)
#             for contract in contract_ids:
#                 active_contract_employee_list.append(contract.employee_id.id)
#             args.append(('id', 'in', active_contract_employee_list))
#         return super(HrEmployee, self).search(args, offset, limit, order, count)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Payslip Batches'

    @api.multi
    def open_payslip_employee(self):
        context = dict(self._context)
        if context is None:
            context = {}
        if not self.ids:
            return True
        context.update({
                        'default_date_start': self.date_start,
                        'default_date_end': self.date_end
        })
        return {'name': ('Payslips by Employees'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.payslip.employees',
                'type': 'ir.actions.act_window',
                'target': 'new',
        }


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_ids = fields.Many2many('res.users', 'ppd_res_user_payroll_rel',
                                'usr_id', 'user_id', 'User Name')

    employee_payroll_ids = fields.Many2many('hr.employee', 'ppd_hr_employee_payroll_rel',
                                'usr_id', 'user_id', 'Employee Name')
