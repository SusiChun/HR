# -*- coding: utf-8 -*-

import base64
import locale

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import tools
from odoo.exceptions import Warning
from odoo import api, fields , models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import xlwt
from cStringIO import StringIO


class ExcelExportSummay(models.TransientModel):

    _name = "excel.export.summay"

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name" , size=32, default='Bank_summary.xls')


class BankSummaryReportWizard(models.TransientModel):

    _name = 'bank.summary.report.wizard'

    employee_ids = fields.Many2many('hr.employee', 'bank_wizard_employee_id',
                                    'wizard_id', 'employee_id',
                                    string='Employees')
    date_start = fields.Date('Date Start',
                             default=lambda *a: datetime.today().date() +
                             relativedelta(day=1))
    date_end = fields.Date('Date End',
                           default=lambda *a: datetime.today().date() +
                           relativedelta(day=31))
    export_report = fields.Selection([('pdf', 'PDF'), ('excel', 'Excel')] ,
                                     "Export", default='pdf')

    @api.onchange('date_start', 'date_end')
    def onchnage_date(self):
        """
        This onchange method is used to check end date should be greater than 
        start date.
        """
        if self.date_start and self.date_end and \
        self.date_start > self.date_end:
            raise Warning(_('End date must be greater than start date'))


    @api.multi
    def print_bank_summary_report(self):
        cr, uid, context = self.env.args
        if context is None:
            context = {}
        context = dict(context)
        data = self.read()[0]
        start_date = data.get('date_start', False)
        end_date = data.get('date_end', False)
        if start_date and end_date and end_date < start_date:
            raise Warning(_("End date should be greater than start date!"))
        res_user = self.env["res.users"].browse(uid)
        if data.get("export_report") == "pdf":
            data.update({'currency': " " + tools.ustr(res_user.company_id.currency_id.symbol), 'company': res_user.company_id.name})
            datas = {
                'ids': [],
                'form': data,
                'model':'hr.payslip',
                'date_from':start_date,
                'date_to':end_date
            }
            return self.env['report'].get_action(self, 'idn_payroll_reports.hr_bank_summary_report_tmp', data=datas)
        else:
            context.update({'employee_ids': data['employee_ids'], 'date_from': start_date, 'date_to': end_date})
            # Create bank summary report in Excel file.
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            font = xlwt.Font()
            font.bold = True
            header = xlwt.easyxf('font: bold 1, height 280')
            start_date = datetime.strptime(context.get("date_from"),
                                           DEFAULT_SERVER_DATE_FORMAT)
            start_date_formate = start_date.strftime('%d/%m/%Y')
            end_date = datetime.strptime(context.get("date_to"),
                                         DEFAULT_SERVER_DATE_FORMAT)
            end_date_formate = end_date.strftime('%d/%m/%Y')
            start_date_to_end_date = tools.ustr(start_date_formate) + ' To ' + tools.ustr(end_date_formate)

            style = xlwt.easyxf('align: wrap yes')
            worksheet.col(0).width = 5000
            worksheet.col(1).width = 5000
            worksheet.row(0).height = 500
            worksheet.row(1).height = 500
            worksheet.write(0, 0, "Company Name" , header)
            worksheet.write(0, 1, res_user.company_id.name, header)
            worksheet.write(0, 7, "By Bank", header)
            worksheet.write(1, 0, "Period", header)
            worksheet.write(1, 1, start_date_to_end_date, header)
            worksheet.col(9).width = 5000
            worksheet.col(11).width = 5000
            borders = xlwt.Borders()
            borders.top = xlwt.Borders.MEDIUM
            borders.bottom = xlwt.Borders.MEDIUM
            border_style = xlwt.XFStyle()  # Create Style
            border_style.borders = borders
            border_style1 = xlwt.easyxf('font: bold 1')
            border_style1.borders = borders
            payslip_obj = self.env['hr.payslip']
            employee_obj = self.env['hr.employee']
            employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids")),
                                                ('department_id', '=', False),
                                                ('bank_account_id', '!=', False)
                                                ])
            row = 2
            if employee_ids and employee_ids.ids:
                payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                  ('date_from', '<=', context.get("date_to")),
                                                  ('employee_id', 'in' , employee_ids.ids),
                                                  ('pay_by_cheque', '=', False),
                                                  ('state', 'in', ['draft', 'done', 'verify'])
                                                  ])
                if payslip_ids:
                    row = 4
                    worksheet.write(4, 0, "", border_style1)
                    worksheet.write(4, 1, "Employee Name" , border_style1)
                    worksheet.write(4, 2, "", border_style1)
                    worksheet.write(4, 3, "Employee Login"  , border_style1)
                    worksheet.write(4, 4, "", border_style1)
                    worksheet.write(4, 5, "Amount" , border_style1)
                    worksheet.write(4, 6, "", border_style1)
                    worksheet.write(4, 7, "Name Of Bank", border_style1)
                    worksheet.write(4, 8, "", border_style1)
                    worksheet.write(4, 9, "Bank Code", border_style1)
                    worksheet.write(4, 10, "", border_style1)
                    worksheet.write(4, 11, "Account Number", border_style1)
                    worksheet.write(4, 12, "", border_style1)
                    worksheet.write(4, 13, "Branch Code", border_style1)
                    row += 1
            style = xlwt.easyxf('align: wrap yes', style)
            result = {}
            payslip_data = {}
            department_total_amount = 0.0
            for employee in employee_ids:
                payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                  ('date_from', '<=', context.get("date_to")),
                                                  ('employee_id', '=' , employee.id),
                                                  ('pay_by_cheque', '=', False),
                                                  ('state', 'in', ['draft', 'done', 'verify'])
                                                  ])
                net = 0.00
                if not payslip_ids:
                    continue
                net = sum([line.total for payslip in payslip_ids
                     for line in payslip.line_ids if line.code == 'NET'])
                net_total = '%.2f' % net
                bank_rec = employee.bank_account_id or False

                worksheet.write(row, 1, employee.name)
                worksheet.write(row, 2, "")
                worksheet.write(row, 3, employee and employee.user_id and employee.user_id.login or '')
                worksheet.write(row, 4, "")
                worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(net_total), grouping=True)))
                worksheet.write(row, 6, "")
                worksheet.write(row, 7, bank_rec and bank_rec.bank_id and bank_rec.bank_id.name or '')
                worksheet.write(row, 8, "")
                worksheet.write(row, 9, bank_rec and bank_rec.bank_id and bank_rec.bank_id.bic or '')
                worksheet.write(row, 10, "")
                worksheet.write(row, 11, bank_rec and bank_rec.acc_number or '')
                worksheet.write(row, 12, "")
                worksheet.write(row, 13, bank_rec and bank_rec.branch_id or '')
                # worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' '+ tools.ustr(net_total))
                row += 1
                department_total_amount += net
                if 'Undefine' in result:
                    result.get('Undefine').append(payslip_data)
                else:
                    result.update({'Undefine': [payslip_data]})
            if department_total_amount:
                worksheet.write(row, 0, 'Total Undefine', border_style)
                worksheet.write(row, 1, '', border_style)
                worksheet.write(row, 2, '', border_style)
                worksheet.write(row, 3, '', border_style)
                worksheet.write(row, 4, '', border_style)
                worksheet.write(row, 5, '', border_style)
                worksheet.write(row, 6, '', border_style)
                worksheet.write(row, 7, '', border_style)
                worksheet.write(row, 8, '', border_style)
                worksheet.write(row, 9, '', border_style)
                worksheet.write(row, 10, '', border_style)
                worksheet.write(row, 11, '', border_style)
                worksheet.write(row, 12, '', border_style)
                new_department_total_amount = '%.2f' % department_total_amount
                worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)) , border_style)
                row += 1
            new_department_total_amount1 = '%.2f' % department_total_amount
            department_total = {'total': new_department_total_amount1, 'department_name': 'Total Undefine'}
            department_info = {'Undefine': [department_total]}

            for hr_department in self.env['hr.department'].search([]):
                employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids")),
                                                    ('department_id', '=', hr_department.id),
                                                    ('bank_account_id', '!=', False)
                                                    ])
                department_total_amount = 0.0
                flag = False
                print_header = True
                for employee in employee_ids:
                    payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                      ('date_from', '<=', context.get("date_to")),
                                                      ('employee_id', '=' , employee.id),
                                                      ('pay_by_cheque', '=', False),
                                                      ('state', 'in', ['draft', 'done', 'verify'])
                                                      ])
                    net = 0.0
                    if not payslip_ids:
                        continue
                    for payslip in payslip_ids:
                        flag = True
                        for line in payslip.line_ids:
                            if line.code == 'NET':
                                net += line.total
                    if print_header and payslip_ids:
                        row += 2
                        print_header = False
                        worksheet.write(row, 0, "", border_style1)
                        worksheet.write(row, 1, "Employee Name" , border_style1)
                        worksheet.write(row, 2, "", border_style1)
                        worksheet.write(row, 3, "Employee Login"  , border_style1)
                        worksheet.write(row, 4, "", border_style1)
                        worksheet.write(row, 5, "Amount" , border_style1)
                        worksheet.write(row, 6, "", border_style1)
                        worksheet.write(row, 7, "Name Of Bank", border_style1)
                        worksheet.write(row, 8, "", border_style1)
                        worksheet.write(row, 9, "Bank Code", border_style1)
                        worksheet.write(row, 10, "", border_style1)
                        worksheet.write(row, 11, "Account Number", border_style1)
                        worksheet.write(row, 12, "", border_style1)
                        worksheet.write(row, 13, "Branch Code", border_style1)
                        row += 1
                    new_net = '%.2f' % net
                    bank_rec = employee.bank_account_id or False
                    worksheet.write(row, 1, employee.name or '')
                    worksheet.write(row, 2, "")
                    worksheet.write(row, 3, employee and employee.user_id and employee.user_id.login or '')
                    worksheet.write(row, 4, "")
                    worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_net), grouping=True)))
                    worksheet.write(row, 6, "")
                    worksheet.write(row, 7, bank_rec and bank_rec.bank_id and bank_rec.bank_id.name or '')
                    worksheet.write(row, 8, "")
                    worksheet.write(row, 9, bank_rec and bank_rec.branch_id or '')
                    worksheet.write(row, 10, "")
                    worksheet.write(row, 11, bank_rec and bank_rec.acc_number or '')
                    worksheet.write(row, 12, "")
                    worksheet.write(row, 13, bank_rec and bank_rec.bank_id and bank_rec.bank_id.bic or '')
                    row += 1
                    department_total_amount += net
                    if hr_department.id in result:
                        result.get(hr_department.id).append(payslip_data)
                    else:
                        result.update({hr_department.id: [payslip_data]})
                if flag:
                    worksheet.write(row, 0, tools.ustr('Total ' + hr_department.name), border_style)
                    worksheet.write(row, 1, '', border_style)
                    worksheet.write(row, 2, '', border_style)
                    worksheet.write(row, 3, '', border_style)
                    worksheet.write(row, 4, '', border_style)
                    worksheet.write(row, 5, '', border_style)
                    worksheet.write(row, 6, '', border_style)
                    worksheet.write(row, 7, '', border_style)
                    worksheet.write(row, 8, '', border_style)
                    worksheet.write(row, 9, '', border_style)
                    worksheet.write(row, 10, '', border_style)
                    worksheet.write(row, 11, '', border_style)
                    worksheet.write(row, 12, '', border_style)
                    new_department_total_amount = '%.2f' % department_total_amount
                    worksheet.write(row, 13, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)), border_style)
                    row += 1
                new_department_total_amount1 = '%.2f' % department_total_amount
                department_total = {'total': new_department_total_amount1, 'department_name': "Total " + hr_department.name}
                if hr_department.id in department_info:
                    department_info.get(hr_department.id).append(department_total)
                else:
                    department_info.update({hr_department.id: [department_total]})

            row += 1
            worksheet.write(row, 0, "Overall Total", border_style)
            worksheet.write(row, 1, '', border_style)
            worksheet.write(row, 2, '', border_style)
            row += 2
            for key, val in result.items():
                worksheet.write(row, 0, department_info[key][0].get("department_name"))
                worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(department_info[key][0].get("total")), grouping=True)))
                row += 1

            row += 1
            total_ammount = 0
            total_employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids")),
                                                      ('bank_account_id', '!=', False)])

            payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                              ('date_from', '<=', context.get("date_to")),
                                              ('employee_id', 'in' , total_employee_ids.ids),
                                              ('pay_by_cheque', '=', False),
                                              ('state', 'in', ['draft', 'done', 'verify'])
                                              ])
            if not payslip_ids:
                raise Warning(_("No payslip found!"))
            total_ammount = sum([line.total for payslip in payslip_ids
                     for line in payslip.line_ids if line.code == 'NET'])
            new_total_ammount = '%.2f' % total_ammount
            worksheet.write(row, 0, "All")
            worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_total_ammount), grouping=True)))
            fp = StringIO()
            workbook.save(fp)
            fp.seek(0)
            data = fp.read()
            fp.close()
            res = base64.b64encode(data)
            excel_export_summay_id = self.env['excel.export.summay'].create({'name': 'Bank_summary.xls', 'file': res})
            return {
              'name': _('Binary'),
              'res_id': excel_export_summay_id.id,
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'excel.export.summay',
              'type': 'ir.actions.act_window',
              'target': 'new',
              'context': context,
              }
