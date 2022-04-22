# -*- coding: utf-8 -*-

import datetime
import base64

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF
from odoo import api, fields, models, _
from odoo.exceptions import Warning

import xlwt
from cStringIO import StringIO


@api.model
def intcomma(self, n, thousands_sep):
    sign = '-' if n < 0 else ''
    n = str(abs(n)).split('.')
    dec = '' if len(n) == 1 else '.' + n[1]
    n = n[0]
    m = len(n)
    return sign + (str(thousands_sep[1]).join([n[0:m % 3]] +
                                              [n[i:i + 3] for i in
                                               range(m % 3, m, 3)])
                   ).lstrip(str(thousands_sep[1])) + dec


class PayrollExcelExportSummay(models.TransientModel):
    _name = "payroll.excel.export.summay"

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name" , default='generic summary.xls')


class PayrollGenericSummaryWizard(models.TransientModel):

    _name = 'payroll.generic.summary.wizard'

    date_from = fields.Date('Date Start')
    date_to = fields.Date('Date End')
    employee_ids = fields.Many2many('hr.employee',
                                    'ppt_hr_employee_payroll_rel', 'emp_id4',
                                    'employee_id', 'Employee Name')
    salary_rule_ids = fields.Many2many('hr.salary.rule',
                                       'ppt_hr_employe_salary_rule_rel',
                                       'salary_rule_id', 'employee_id',
                                       'Employee payslip')

    @api.onchange('date_from', 'date_to')
    def onchnage_date(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise Warning(_('End date must be greater than start date!'))

    @api.multi
    def print_order(self):
        context = dict(self._context)
        data = self.read([])[0]
        context.update({'employee_ids': data['employee_ids'],
                        'salary_rules_id':data['salary_rule_ids'],
                        'date_from': data['date_from'],
                        'date_to': data['date_to']
                        })
        if data['date_from'] and data['date_to'] and \
        data['date_from'] > data['date_to']:
            raise Warning(_('End date must be greater than start date!'))

        # Create xls file and selected employee record write.
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        header = xlwt.easyxf('font: bold 1, height 280')
        hr_depart_obj = self.env['hr.department']
        res_user = self.env.user
        payslip_obj = self.env['hr.payslip']
        rule_id = context.get('salary_rules_id')
        date_start = context.get("date_from")
        date_end = context.get("date_to")
        salary_rule = [rule.name for rule in
                       self.env['hr.salary.rule'].browse(rule_id)]
        start_date = datetime.datetime.strptime(date_start, DSDF)
        start_date_formate = start_date.strftime('%d/%m/%Y')
        end_date = datetime.datetime.strptime(date_end, DSDF)
        end_date_formate = end_date.strftime('%d/%m/%Y')
        date_period = str(start_date_formate) + ' To ' + str(end_date_formate)
        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        worksheet.row(2).height = 500

        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        border_style1 = xlwt.easyxf('font: bold 1')
        border_style1.borders = borders
        worksheet.write(0, 0, "Company Name :- " + res_user.company_id.name, header)
        worksheet.write(1, 0, "Payroll Summary Report :", header)
        worksheet.write(1, 2, "", header)
        worksheet.write(2, 0, "Period :", header)
        worksheet.write(2, 1, date_period , header)

        row = 4
        col = 5
        worksheet.write(4, 0, "Employee No", border_style1)
        worksheet.write(4, 1, "Employee Name", border_style1)
        worksheet.write(4, 2, "Wage", border_style1)
        worksheet.write(4, 3, "Wage To Pay", border_style1)
        worksheet.write(4, 4, "Rate Per Hour", border_style1)
        for rule in salary_rule:
            worksheet.write(row, col, rule, border_style1)
            col += 1

        row += 2
        result = {}
        total = {}
        employee_ids = self.env['hr.employee'].search([('id', 'in',
                                                        context.get("employee_ids"))])
        if not res_user.lang:
            raise Warning(_('Please select user language.'))
        res_lang_ids = self.env['res.lang'].search([('code', '=',
                                                     res_user.lang)], limit=1)
        thousands_sep = ","
        if res_lang_ids and res_lang_ids.ids:
            monetary = False
            thousands_sep = res_lang_ids._data_get()
        tot_categ_cont_wage = tot_categ_cont_wage_to_pay = \
        tot_categ_cont_rate_per_hour = 0.0

        for employee in employee_ids:
            payslip_ids = payslip_obj.search([('employee_id', '=', employee.id),
                                              ('date_from', '>=', date_start),
                                              ('date_from', '<=', date_end),
                                              ('state', 'in', ['draft', 'done',
                                                               'verify'])])
            if not payslip_ids:
                continue
            contract_wage = 0.0
            contract_wage_to_pay = 0.0
            contract_rate_per_hour = 0.0

            new_payslip_result = {}
            for rule in salary_rule:
                new_payslip_result.update({rule:0.00})
            for payslip in payslip_ids:
                contract_rate_per_hour += payslip and payslip.contract_id and \
                payslip.contract_id.rate_per_hour or 0.0
                for rule in payslip.details_by_salary_rule_category:
                    if rule.code == 'BASIC':
                        contract_wage += payslip and payslip.contract_id and \
                        payslip.contract_id.wage or 0.0
                        contract_wage_to_pay += payslip and \
                        payslip.contract_id and payslip.contract_id.wage_to_pay \
                        or 0.0
                    for set_rule in salary_rule:
                        rule_total = 0.00
                        if rule.name == set_rule:
                            rule_total += rule.total
                        new_payslip_result.update({set_rule: new_payslip_result.get(set_rule, 0) + float(rule_total)})
            payslip_result = {'department': employee.department_id.id or "Undefine",
                              'ename': employee.name,
                              'eid': employee.user_id.login,
                              'wage': contract_wage,
                              'wage_to_pay': contract_wage_to_pay,
                              'rate_per_hour': contract_rate_per_hour
                              }
            value_found = True
            for key, val in new_payslip_result.items():
                if val:
                    value_found = False
            if value_found:
                continue
            payslip_result.update(new_payslip_result)
            if payslip.employee_id.department_id:
                if payslip.employee_id.department_id.id in result:
                    result.get(payslip.employee_id.department_id.id).append(payslip_result)
                else:
                    result.update({payslip.employee_id.department_id.id: [payslip_result]})
            else:
                if 'Undefine' in result:
                    result.get('Undefine').append(payslip_result)
                else:
                    result.update({'Undefine': [payslip_result]})
        final_total = {'name':"Grand Total"}
        for rule in salary_rule:
            final_total.update({rule:0.0})
        for key, val in result.items():
            categ_cont_wage = categ_cont_wage_to_pay = categ_cont_rate_per_hour = 0.0
            style = xlwt.easyxf('font: bold 0')
            if key == 'Undefine':
                category_name = 'Undefine'
                category_id = 0
            else:
                category_name = hr_depart_obj.browse(key).name
                category_id = hr_depart_obj.browse(key).id
            total = {'categ_id':category_id, 'name': category_name}
            for rule in salary_rule:
                total.update({rule:0.0})
            for line in val:
                for field in line:
                    if field in total:
                        total.update({field:  total.get(field) + line.get(field)})
            style1 = xlwt.easyxf()
            style1.num_format_str = '0.00'
            if total.get("name") == "Undefine":
                for payslip_result in result[total.get("name")]:
                    categ_cont_wage += payslip_result.get("wage")
                    tot_categ_cont_wage += payslip_result.get("wage")
                    categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    tot_categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    tot_categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")

                    contract_wage = str(abs(payslip_result.get("wage")))
                    contract_wage = intcomma(self, float(contract_wage), thousands_sep)
                    contract_wage = contract_wage.ljust(len(contract_wage.split('.')[0]) + 3, '0')

                    contract_wage_to_pay = str(abs(payslip_result.get("wage_to_pay")))
                    contract_wage_to_pay = intcomma(self, float(contract_wage_to_pay), thousands_sep)
                    contract_wage_to_pay = contract_wage_to_pay.ljust(len(contract_wage_to_pay.split('.')[0]) + 3, '0')

                    contract_rate_per_hour = str(abs(payslip_result.get("rate_per_hour")))
                    contract_rate_per_hour = intcomma(self, float(contract_rate_per_hour), thousands_sep)
                    contract_rate_per_hour = contract_rate_per_hour.ljust(len(contract_rate_per_hour.split('.')[0]) + 3, '0')

                    worksheet.write(row, 0, payslip_result.get("eid"))
                    worksheet.write(row, 1, payslip_result.get("ename"))
                    style.alignment = alignment
                    worksheet.write(row, 2, contract_wage, style)
                    worksheet.write(row, 3, contract_wage_to_pay, style)
                    worksheet.write(row, 4, contract_rate_per_hour, style)
                    col = 5
                    for rule in salary_rule:
                        split_total_rule = str(abs(payslip_result.get(rule)))
                        split_total_rule = intcomma(self, float(split_total_rule), thousands_sep)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0]) + 3, '0')
                        style.alignment = alignment
                        worksheet.write(row, col, split_total_rule, style)
                        col += 1
                    row += 1
            else:
                for payslip_result in result[total.get("categ_id")]:
                    categ_cont_wage += payslip_result.get("wage")
                    tot_categ_cont_wage += payslip_result.get("wage")
                    categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    tot_categ_cont_wage_to_pay += payslip_result.get("wage_to_pay")
                    categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")
                    tot_categ_cont_rate_per_hour += payslip_result.get("rate_per_hour")

                    contract_wage = str(abs(payslip_result.get("wage")))
                    contract_wage = intcomma(self, float(contract_wage), thousands_sep)
                    contract_wage = contract_wage.ljust(len(contract_wage.split('.')[0]) + 3, '0')

                    contract_wage_to_pay = str(abs(payslip_result.get("wage_to_pay")))
                    contract_wage_to_pay = intcomma(self, float(contract_wage_to_pay), thousands_sep)
                    contract_wage_to_pay = contract_wage_to_pay.ljust(len(contract_wage_to_pay.split('.')[0]) + 3, '0')

                    contract_rate_per_hour = str(abs(payslip_result.get("rate_per_hour")))
                    contract_rate_per_hour = intcomma(self, float(contract_rate_per_hour), thousands_sep)
                    contract_rate_per_hour = contract_rate_per_hour.ljust(len(contract_rate_per_hour.split('.')[0]) + 3, '0')

                    worksheet.write(row, 0, payslip_result.get("eid"))
                    worksheet.write(row, 1, payslip_result.get("ename"))
                    style.alignment = alignment
                    worksheet.write(row, 2, contract_wage, style)
                    worksheet.write(row, 3, contract_wage_to_pay, style)
                    worksheet.write(row, 4, contract_rate_per_hour, style)
                    col = 5
                    for rule in salary_rule:
                        split_total_rule = str(abs(payslip_result.get(rule)))
                        split_total_rule = intcomma(self, float(split_total_rule), thousands_sep)
                        split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0]) + 3, '0')
                        style.alignment = alignment
                        worksheet.write(row, col, split_total_rule, style)
                        col += 1
                    row += 1

            borders = xlwt.Borders()
            borders.top = xlwt.Borders.MEDIUM
            borders.bottom = xlwt.Borders.MEDIUM
            border_top = xlwt.XFStyle()  # Create Style
            border_top.borders = borders
            style = xlwt.easyxf('font: bold 1')
            style.num_format_str = '0.00'

            worksheet.write(row, 0, str("Total " + total["name"]) , style)
            worksheet.write(row, 1, "" , style)
            col = 5

            categ_cont_wage = str(abs(categ_cont_wage))
            categ_cont_wage = intcomma(self, float(categ_cont_wage), thousands_sep)
            categ_cont_wage = categ_cont_wage.ljust(len(categ_cont_wage.split('.')[0]) + 3, '0')

            categ_cont_wage_to_pay = str(abs(categ_cont_wage_to_pay))
            categ_cont_wage_to_pay = intcomma(self, float(categ_cont_wage_to_pay), thousands_sep)
            categ_cont_wage_to_pay = categ_cont_wage_to_pay.ljust(len(categ_cont_wage_to_pay.split('.')[0]) + 3, '0')

            categ_cont_rate_per_hour = str(abs(categ_cont_rate_per_hour))
            categ_cont_rate_per_hour = intcomma(self, float(categ_cont_rate_per_hour), thousands_sep)
            categ_cont_rate_per_hour = categ_cont_rate_per_hour.ljust(len(categ_cont_rate_per_hour.split('.')[0]) + 3, '0')

            style.alignment = alignment
            worksheet.write(row, 2, categ_cont_wage, style)
            worksheet.write(row, 3, categ_cont_wage_to_pay, style)
            worksheet.write(row, 4, categ_cont_rate_per_hour, style)
            for rule in salary_rule:
                rule_total = 0.0
                split_total_rule = str(abs(total[rule]))
                split_total_rule = intcomma(self, float(split_total_rule), thousands_sep)
                split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0]) + 3, '0')
                style.alignment = alignment
                worksheet.write(row, col, split_total_rule, style)
                rule_total = final_total[rule] + total[rule]
                final_total.update({rule:rule_total})
                col += 1
            row += 2

        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        border_total = xlwt.XFStyle()  # Create Style
        border_total.borders = borders
        row += 1
        worksheet.write(row, 0, final_total["name"] , style)
        worksheet.write(row, 1, "" , border_total)
        col = 5

        tot_categ_cont_wage = str(abs(tot_categ_cont_wage))
        tot_categ_cont_wage = intcomma(self, float(tot_categ_cont_wage), thousands_sep)
        tot_categ_cont_wage = tot_categ_cont_wage.ljust(len(tot_categ_cont_wage.split('.')[0]) + 3, '0')

        tot_categ_cont_wage_to_pay = str(abs(tot_categ_cont_wage_to_pay))
        tot_categ_cont_wage_to_pay = intcomma(self, float(tot_categ_cont_wage_to_pay), thousands_sep)
        tot_categ_cont_wage_to_pay = tot_categ_cont_wage_to_pay.ljust(len(tot_categ_cont_wage_to_pay.split('.')[0]) + 3, '0')

        tot_categ_cont_rate_per_hour = str(abs(tot_categ_cont_rate_per_hour))
        tot_categ_cont_rate_per_hour = intcomma(self, float(tot_categ_cont_rate_per_hour), thousands_sep)
        tot_categ_cont_rate_per_hour = tot_categ_cont_rate_per_hour.ljust(len(tot_categ_cont_rate_per_hour.split('.')[0]) + 3, '0')

        style.alignment = alignment
        worksheet.write(row, 2, tot_categ_cont_wage, style)
        worksheet.write(row, 3, tot_categ_cont_wage_to_pay, style)
        worksheet.write(row, 4, tot_categ_cont_rate_per_hour, style)
        for rule in salary_rule:
            split_total_rule = str(abs(final_total[rule]))
            split_total_rule = intcomma(self, float(split_total_rule), thousands_sep)
            split_total_rule = split_total_rule.ljust(len(split_total_rule.split('.')[0]) + 3, '0')
            style.alignment = alignment
            worksheet.write(row, col, split_total_rule, style)
            col += 1
        row += 1
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.b64encode(data)

        # Create record for Binary data.
        pay_excell_rec = self.env['payroll.excel.export.summay'].create({'name': 'generic summary.xls', 'file': res, })
        return {
          'name': _('Binary'),
          'res_id': pay_excell_rec.id,
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'payroll.excel.export.summay',
          'type': 'ir.actions.act_window',
          'target': 'new',
          'context': context,
          }

