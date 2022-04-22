# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import Warning


class hr_cheque_summary_report(models.AbstractModel):

    _name = 'report.idn_payroll_reports.cheque_summary_report_tmp'

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

        employee_ids = employee_obj.search([('id', 'in',
                                             data.get('employee_ids')),
                                            ('department_id', '=', False)])
        department_total_amount = 0.0
        for employee in employee_ids:
            payslip_ids = []
            if employee.bank_account_id:
                payslip_id = payslip_obj.search([('date_from', '>=', date_from),
                                                 ('date_from', '<=', date_to),
                                                 ('employee_id', '=' ,
                                                  employee.id),
                                                 ('pay_by_cheque', '=', True),
                                                 ('state', 'in', ['draft',
                                                                  'done',
                                                                  'verify'])])
                if payslip_id:
                    payslip_id = payslip_id.ids
                    payslip_ids.append(payslip_id[0])
            else:
                payslip_id = payslip_obj.search([('date_from', '>=', date_from),
                                                 ('date_from', '<=', date_to),
                                                 ('employee_id', '=' ,
                                                  employee.id),
                                                 ('state', 'in', ['draft',
                                                                  'done',
                                                                  'verify'])])
                if payslip_id:
                    payslip_id = payslip_id.ids
                    payslip_ids.append(payslip_id[0])
            net = 0.0
            if not payslip_ids:
                continue
            cheque_number = ''
            for payslip in payslip_obj.browse(payslip_ids):
                if not cheque_number:
                    cheque_number = payslip.cheque_number
                if not payslip.employee_id.department_id.id:
                    net = sum([line.total for line in payslip.line_ids
                               if line.code == 'NET'])
            payslip_data = {
                            'employee_id': employee.user_id and
                            employee.user_id.login or ' ',
                            'employee_name':employee.name or ' ',
                            'cheque_number':cheque_number or '',
                            'amount':net,
            }
            department_total_amount += net
            if 'Undefine' in result:
                result.get('Undefine').append(payslip_data)
            else:
                result.update({'Undefine': [payslip_data]})
        department_total = {'total': department_total_amount,
                            'department_name': "Total Undefine"}
        if 'Undefine' in department_info:
            department_info.get('Undefine').append(department_total)
        else:
            department_info.update({'Undefine': [department_total]})

        for hr_department in self.env['hr.department'].search([]):
            employee_ids = employee_obj.search([('id', 'in',
                                                 data.get('employee_ids')),
                                                ('department_id', '=',
                                                 hr_department.id)
                                                ])
            department_total_amount = 0.0
            for employee in employee_ids:
                payslip_ids = []
                if employee.bank_account_id:
                    payslip_id = payslip_obj.search([('date_from', '>=',
                                                      date_from),
                                                     ('date_from', '<=', date_to),
                                                     ('employee_id', '=' ,
                                                       employee.id),
                                                     ('pay_by_cheque', '=',
                                                      True),
                                                     ('state', 'in', ['draft',
                                                                      'done',
                                                                      'verify'])
                                                     ])
                    if payslip_id:
                        payslip_id = payslip_id.ids
                        payslip_ids.append(payslip_id[0])
                else:
                    payslip_id = payslip_obj.search([('date_from', '>=',
                                                      date_from),
                                                     ('date_from', '<=',
                                                      date_to),
                                                     ('employee_id', '=' ,
                                                      employee.id),
                                                     ('state', 'in', ['draft',
                                                                      'done',
                                                                      'verify'])
                                                     ])
                    if payslip_id:
                        payslip_id = payslip_id.ids
                        payslip_ids.append(payslip_id[0])
                net = 0.0
                if not payslip_ids:
                    continue
                cheque_number = ''
                for payslip in payslip_obj.browse(payslip_ids):
                    if not cheque_number:
                        cheque_number = payslip.cheque_number
                    net = sum([line.total for line in payslip.line_ids
                               if line.code == 'NET'])

                payslip_data = {
                                'employee_id': employee.user_id and
                                employee.user_id.login or ' ',
                                'employee_name':employee.name or ' ',
                                'cheque_number':cheque_number,
                                'amount':net,
                }
                department_total_amount += net
                if hr_department.id in result:
                    result.get(hr_department.id).append(payslip_data)
                else:
                    result.update({hr_department.id: [payslip_data]})
            department_total = {'total': department_total_amount,
                                'department_name': "Total " + hr_department.name}
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
        empl_ids_lst = data.get('employee_ids') or False
        employee_rec = self.env['hr.employee'].search([('id', 'in',
                                                        empl_ids_lst)])
        total_ammount = 0
        payslip_ids = []
        for employee in employee_rec:
            if employee.bank_account_id:
                payslip_id = self.env['hr.payslip'].search([('date_from', '>=',
                                                             date_from),
                                                            ('date_from', '<=',
                                                             date_to),
                                                            ('employee_id',
                                                             '=' , employee.id),
                                                            ('pay_by_cheque',
                                                             '=', True),
                                                            ('state', 'in',
                                                             ['draft', 'done',
                                                              'verify'])])
                if payslip_id:
                    payslip_ids.append(payslip_id)
        total_ammount = sum([line.total for line in payslip_id.line_ids
                             for payslip_rec in payslip
                             for payslip in payslip_ids if line.code == 'NET'])
        return total_ammount

    @api.model
    def get_totalrecord(self, data):
        date_from = data.get('date_start') or False
        date_to = data.get('date_end') or False
        emp_ids_lst = data.get('employee_ids') or False
        employee_rec = self.env['hr.employee'].search([('id', 'in',
                                                        emp_ids_lst)])
        payslip_obj = self.env['hr.payslip']
        ttl_emp = 0
        payslip_list = []
        for employee in employee_rec:
            payslip_rec = payslip_obj.search([('date_from', '>=', date_from),
                                              ('date_from', '<=', date_to),
                                              ('pay_by_cheque', '=', True),
                                              ('employee_id', '=' ,
                                               employee.id),
                                              ('state', 'in', ['draft', 'done',
                                                           'verify'])])

            if payslip_rec and payslip_rec.ids:
                payslip_list.append(payslip_rec.ids)
        ttl_emp = len(payslip_list)
        if ttl_emp == 0:
            raise Warning("No payslip found!")
        return ttl_emp

    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        data = docs.read([])[0]
        docargs = {'doc_ids' : self.ids,
                   'doc_model' : self.model,
                   'data' : data,
                   'docs' : docs,
                   'get_info' : self.get_info(data),
                   'get_total' : self.get_total(data),
                   'get_totalrecord' : self.get_totalrecord(data),
                   }
        return self.env['report'].render('idn_payroll_reports.cheque_summary_report_tmp', docargs)
