# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import Warning


class HrBankSummaryReport(models.AbstractModel):

    _name = "report.idn_payroll_reports.hr_bank_summary_report_tmp"

    @api.model
    def get_info(self, data):
        date_from = data.get('date_start') or False
        date_to = data.get('date_end') or False
        payslip_obj = self.env['hr.payslip']
        employee_obj = self.env['hr.employee']
        result = {}
        payslip_data = {}
        department_info = {}
        final_result = {}
        employee_ids_lst = data.get('employee_ids')
        employee_ids = employee_obj.search([('id', 'in', employee_ids_lst),
                                            ('department_id', '=', False),
                                            ('bank_account_id', '!=', False)
                                            ])
        department_total_amount = 0.0
        for employee in employee_ids:
            payslip_ids = payslip_obj.search([('date_from', '>=', date_from),
                                              ('date_from', '<=', date_to),
                                              ('employee_id', '=' , employee.id),
                                              ('pay_by_cheque', '=', False),
                                              ('state', 'in', ['draft', 'done',
                                                               'verify'])])
            net = 0.0
            if not payslip_ids:
                continue
            for payslip in payslip_ids:
                if not payslip.employee_id.department_id.id:
                    for line in payslip.line_ids:
                        if line.code == 'NET':
                            net += line.total
            bank_rec = employee.bank_account_id or False
            payslip_data = {
                            'bank_name': bank_rec and bank_rec.bank_id and
                            bank_rec.bank_id.name or '',
                            'bank_id': bank_rec and bank_rec.bank_id and
                            bank_rec.bank_id.bic or '',
                            'branch_id': bank_rec and bank_rec.branch_id or '',
                            'employee_id': employee and employee.user_id and
                            employee.user_id.login or '',
                            'employee_name': employee.name,
                            'account_number': bank_rec and bank_rec.acc_number
                            or '',
                            'amount':net,
            }
            department_total_amount += net
            if 'Undefine' in result:
                result.get('Undefine').append(payslip_data)
            else:
                result.update({'Undefine': [payslip_data]})
        department_total = {'total': department_total_amount,
                            'department_name': 'Total Undefine'}

        if 'Undefine' in department_info:
            department_info.get('Undefine').append(department_total)
        else:
            department_info.update({'Undefine': [department_total]})

        for hr_department in self.env['hr.department'].search([]):
            employee_ids = employee_obj.search([('id', 'in', employee_ids_lst),
                                                ('department_id', '=',
                                                 hr_department.id),
                                                ('bank_account_id', '!=', False)
                                                ])
            department_total_amount = 0.0
            for employee in employee_ids:
                payslip_ids = payslip_obj.search([('date_from', '>=',
                                                   date_from),
                                                  ('date_from', '<=', date_to),
                                                  ('employee_id', '=' ,
                                                   employee.id),
                                                  ('pay_by_cheque', '=', False),
                                                  ('state', 'in', ['draft',
                                                                   'done',
                                                                   'verify'])
                                                  ])
                net = 0.0
                if not payslip_ids:
                    continue
                    net = sum([line.total for line in payslip.line_ids
                                   if line.code == 'NET'])
                    bank_rec = employee.bank_account_id or False
                    payslip_data = {
                                'bank_name': bank_rec and bank_rec.bank_id and
                                bank_rec.bank_id.name or '',
                                'bank_id': bank_rec and bank_rec.bank_id and
                                bank_rec.bank_id.bic or '',
                                'branch_id': bank_rec and bank_rec.branch_id or '',
                                'employee_id': employee and employee.user_id and
                                employee.user_id.login or ' ',
                                'employee_name':employee.name,
                                'account_number':bank_rec and bank_rec.acc_number \
                                or '',
                                'amount':net,
                    }
                department_total_amount += net
                if hr_department.id in result:
                    result.get(hr_department.id).append(payslip_data)
                else:
                    result.update({hr_department.id: [payslip_data]})
            department_total = {'total': round(department_total_amount, 2),
                                'department_name': "Total " +
                                hr_department.name}
            if hr_department.id in department_info:
                department_info.get(hr_department.id).append(department_total)
            else:
                department_info.update({hr_department.id: [department_total]})
        for key, val in result.items():
            final_result[key] = {'lines': val,
                                 'departmane_total': department_info[key] }
        return final_result.values()

    @api.model
    def get_total(self, data):
        date_from = data.get('date_start') or False
        date_to = data.get('date_end') or False
        total_ammount = 0
        emp_ids_lst = data.get('employee_ids')
        payslip_obj = self.env['hr.payslip']
        payslip_ids = payslip_obj.search([('date_from', '>=', date_from),
                                          ('pay_by_cheque', '=', False),
                                          ('employee_id', 'in' , emp_ids_lst),
                                          ('state', 'in', ['draft', 'done',
                                                           'verify']),
                                          ('employee_id.bank_account_id', '!=',
                                           False),
                                          ('date_from', '<=', date_to), ])
        if payslip_ids and payslip_ids.ids:
            total_ammount = sum([line.total for payslip in payslip_ids
                             if payslip.line_ids for line in payslip.line_ids
                             if line.code == 'NET'])
        return total_ammount

    @api.model
    def get_totalrecord(self, data):
        emp_list = []
        ttl_emp = 0
        date_from = data.get('date_start') or False
        date_to = data.get('date_end') or False
        emp_obj = self.env['hr.employee']
        payslip_obj = self.env['hr.payslip']
        employee_ids = emp_obj.search([('bank_account_id', '!=', False),
                                       ('id', 'in', data.get('employee_ids'))])
        for employee in employee_ids:
            payslip_ids = payslip_obj.search([('date_from', '>=', date_from),
                                              ('date_from', '<=', date_to),
                                              ('employee_id', '=' ,
                                               employee.id),
                                              ('pay_by_cheque', '=', False),
                                              ('state', 'in', ['draft', 'done',
                                                               'verify'])])
            if payslip_ids and payslip_ids.ids:
                emp_list.append(employee.id)
        ttl_emp = len(emp_list)
        if ttl_emp == 0:
            raise Warning("No payslip found!")
        return ttl_emp

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        data = docs.read([])[0]
        docargs = {
            'doc_ids':self.ids,
            'doc_model':self.model,
            'data':data,
            'docs':docs,
            'get_info': self.get_info(data),
            'get_totalrecord': self.get_totalrecord(data),
            'get_total': self.get_total(data),
            }
        return self.env['report'].render('idn_payroll_reports.hr_bank_summary_report_tmp', docargs)
