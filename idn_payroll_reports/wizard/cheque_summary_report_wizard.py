# -*- coding: utf-8 -*-

import locale
import base64

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import tools
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import Warning

import xlwt
from cStringIO import StringIO


class ExcelExportChequeSummay(models.TransientModel):
    _name = "excel.export.cheque.summay"

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name" , size=32, default='Cheque_summary.xls')


class ViewChequeSummaryReportWizard(models.TransientModel):
    _name = 'view.cheque.summary.report.wizard'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_cheque_rel',
                                    'emp_id', 'employee_id', 'Employee Name',
                                    required=False)
    date_start = fields.Date('Date Start',
                             default=lambda *a: datetime.today().date() +
                             relativedelta(day=1))
    date_end = fields.Date('Date End',
                           default=lambda *a: datetime.today().date() +
                           relativedelta(day=31))
    export_report = fields.Selection([('pdf', 'PDF'), ('excel', 'Excel')] ,
                                     "Export", default='pdf')

    @api.onchange('date_start', 'date_end')
    def onchange_dates(self):
        if self.date_end and self.date_start and \
        self.date_end < self.date_start:
            raise Warning("End date should be greater than start date!")

    @api.multi
    def print_cheque_summary_report(self):
        cr, uid, context = self.env.args
        if context is None:
            context = {}
        context = dict(context)
        data = self.read()[0]
        start_date = data.get('date_start', False)
        end_date = data.get('date_end', False)
        res_user = self.env["res.users"].browse(uid)
        if start_date and end_date and end_date < start_date:
            raise Warning("End date should be greater than start day!")
        if data.get("export_report") == "pdf":
            data.update({'currency': " " + tools.ustr(res_user.company_id.currency_id.symbol), 'company': res_user.company_id.name})
            datas = {
                'ids': [],
                'form': data,
                'model':'hr.payslip',
                'date_from':start_date,
                'date_to':end_date
            }
            return self.env['report'].get_action(self, 'idn_payroll_reports.cheque_summary_report_tmp', data=datas)
        else:
            context.update({'employee_ids': data['employee_ids'], 'date_from': start_date, 'date_to': end_date})

            # Create cheque summary report in xls file.
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            font = xlwt.Font()
            font.bold = True
            header = xlwt.easyxf('font: bold 1, height 240;')
            start_date = datetime.strptime(context.get("date_from"), DEFAULT_SERVER_DATE_FORMAT)
            start_date_formate = start_date.strftime('%d/%m/%Y')
            end_date = datetime.strptime(context.get("date_to"), DEFAULT_SERVER_DATE_FORMAT)
            end_date_formate = end_date.strftime('%d/%m/%Y')
            start_date_to_end_date = tools.ustr(start_date_formate) + ' To ' + tools.ustr(end_date_formate)

            borders = xlwt.Borders()
            borders.top = xlwt.Borders.MEDIUM
            borders.bottom = xlwt.Borders.MEDIUM
            alignment = xlwt.Alignment()
            alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
            alignment.vert = xlwt.Alignment.VERT_CENTER
            border_style = xlwt.XFStyle()  # Create Style
            border_style.alignment = alignment
            border_style.borders = borders
            border_style1 = xlwt.easyxf('font: bold 1')
            border_style1.borders = borders
            alignment_style = xlwt.XFStyle()  # Create Style
            alignment_style.alignment = alignment
            flag = False

            style = xlwt.easyxf('align: wrap yes')
            worksheet.col(0).width = 5000
            worksheet.col(1).width = 5000
            worksheet.col(3).width = 5000
            worksheet.col(5).width = 5000
            worksheet.row(0).height = 500
            worksheet.row(1).height = 500
            worksheet.write(0, 0, "Company Name" , header)
            worksheet.write(0, 1, res_user.company_id.name, header)
            worksheet.write(0, 7, "By Cheque", header)
            worksheet.write(1, 0, "Period", header)
            worksheet.write(1, 1, start_date_to_end_date, header)

            payslip_obj = self.env['hr.payslip']
            employee_obj = self.env['hr.employee']
            result = {}
            payslip_data = {}
            department_info = {}
            employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids")), ('department_id', '=', False)])
            row = 2
            if employee_ids and employee_ids.ids:
                payslip_ids = []
                for emp in employee_ids:
                    if emp.bank_account_id:
                        payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                         ('date_from', '<=', context.get("date_to")),
                                                         ('employee_id', '=' , emp.id),
                                                         ('pay_by_cheque', '=', True),
                                                         ('state', 'in', ['draft', 'done', 'verify'])
                                                         ])
                        if payslip_id and payslip_id.ids:
                            payslip_id = payslip_id.ids
                            payslip_ids.append(payslip_id[0])
                    else:
                        payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                         ('date_from', '<=', context.get("date_to")),
                                                         ('employee_id', '=' , emp.id),
                                                         ('state', 'in', ['draft', 'done', 'verify'])
                                                         ])
                        if payslip_id:
                            payslip_id = payslip_id.ids
                            payslip_ids.append(payslip_id[0])
                if payslip_ids:
                    worksheet.write(2, 0, "", border_style1)
                    worksheet.write(2, 1, "Employee Name" , border_style1)
                    worksheet.write(2, 2, "", border_style1)
                    worksheet.write(2, 3, "Employee Login", border_style1)
                    worksheet.write(2, 4, "", border_style1)
                    worksheet.write(2, 5, "Amount", border_style1)
                    worksheet.write(2, 6, "", border_style1)
                    worksheet.write(2, 7, "Cheque Number", border_style1)
                    row += 1
            department_total_amount = 0.0
            flag = False
            for employee in employee_ids:
                payslip_ids = []
                if employee.bank_account_id:
                    payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                     ('date_from', '<=', context.get("date_to")),
                                                     ('employee_id', '=' , employee.id),
                                                     ('pay_by_cheque', '=', True),
                                                     ('state', 'in', ['draft', 'done', 'verify'])
                                                     ])
                    if payslip_id:
                        payslip_id = payslip_id.ids
                        payslip_ids.append(payslip_id[0])
                else:
                    payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                     ('date_from', '<=', context.get("date_to")),
                                                     ('employee_id', '=' , employee.id),
                                                     ('state', 'in', ['draft', 'done', 'verify'])
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
                    flag = True
                    if not payslip.employee_id.department_id.id:
                        for line in payslip.line_ids:
                            if line.code == 'NET':
                                net += line.total
                worksheet.write(row, 0, "")
                worksheet.write(row, 1, employee.name or '', alignment_style)
                worksheet.write(row, 2, "")
                worksheet.write(row, 3, employee.user_id and employee.user_id.login or '', alignment_style)
                worksheet.write(row, 4, "")
                net_total = '%.2f' % net
                worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(net_total), grouping=True)), alignment_style)
                worksheet.write(row, 6, "")
                worksheet.write(row, 7, cheque_number or '', alignment_style)
                row += 1
                department_total_amount += net
                if 'Undefine' in result:
                    result.get('Undefine').append(payslip_data)
                else:
                    result.update({'Undefine': [payslip_data]})
            if flag:
                worksheet.write(row, 0, 'Total Undefine', border_style)
                worksheet.write(row, 1, '', border_style)
                worksheet.write(row, 2, '', border_style)
                worksheet.write(row, 3, '', border_style)
                worksheet.write(row, 4, '', border_style)
                worksheet.write(row, 5, '', border_style)
                worksheet.write(row, 6, '', border_style)
                new_department_total_amount = '%.2f' % department_total_amount
                worksheet.write(row, 7, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)), border_style)
                row += 1
            new_department_total_amount1 = '%.2f' % department_total_amount
            department_total = {'total': new_department_total_amount1, 'department_name': "Total Undefine"}
            if 'Undefine' in department_info:
                department_info.get('Undefine').append(department_total)
            else:
                department_info.update({'Undefine': [department_total]})

            for hr_department in self.env['hr.department'].search([]):
                employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids")), ('department_id', '=', hr_department.id)])
                department_total_amount = 0.0
                flag = False
                print_header = True
                for employee in employee_ids:
                    payslip_ids = []
                    if employee.bank_account_id:
                        payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                         ('date_from', '<=', context.get("date_to")),
                                                         ('employee_id', '=' , employee.id),
                                                         ('pay_by_cheque', '=', True),
                                                         ('state', 'in', ['draft', 'done', 'verify'])
                                                         ])
                        if payslip_id:
                            payslip_id = payslip_id.ids
                            payslip_ids.append(payslip_id[0])
                    else:
                        payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                         ('date_from', '<=', context.get("date_to")),
                                                         ('employee_id', '=' , employee.id),
                                                         ('state', 'in', ['draft', 'done', 'verify'])
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
                        flag = True
                        for line in payslip.line_ids:
                            if line.code == 'NET':
                                net += line.total
                    if print_header:
                        row += 2
                        print_header = False
                        worksheet.write(row, 0, "", border_style1)
                        worksheet.write(row, 1, "Employee Name", border_style1)
                        worksheet.write(row, 2, "", border_style1)
                        worksheet.write(row, 3, "Employee Login", border_style1)
                        worksheet.write(row, 4, "", border_style1)
                        worksheet.write(row, 5, "Amount", border_style1)
                        worksheet.write(row, 6, "", border_style1)
                        worksheet.write(row, 7, "Cheque Number", border_style1)
                        row += 1
                    worksheet.write(row, 0, "")
                    worksheet.write(row, 1, employee.name or ' ' , alignment_style)
                    worksheet.write(row, 2, "")
                    worksheet.write(row, 3, employee.user_id and employee.user_id.login or '', alignment_style)
                    worksheet.write(row, 4, "")
                    new_net = '%.2f' % net
                    worksheet.write(row, 5, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_net), grouping=True)), alignment_style)
                    worksheet.write(row, 6, "")
                    worksheet.write(row, 7, cheque_number or '', alignment_style)
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
                    new_department_total_amount = '%.2f' % department_total_amount
                    worksheet.write(row, 7, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_department_total_amount), grouping=True)), border_style)
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
                worksheet.write(row, 0, department_info[key][0].get("department_name"), alignment_style)
                worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(department_info[key][0].get("total")), grouping=True)), alignment_style)
                row += 1
            row += 1
            total_ammount = 0
            employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids"))])
            payslip_ids = []
            for employee in employee_ids:
                if employee.bank_account_id:
                    payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                     ('date_from', '<=', context.get("date_to")),
                                                     ('employee_id', '=' , employee.id), ('pay_by_cheque', '=', True),
                                                     ('state', 'in', ['draft', 'done', 'verify'])
                                                     ])
                    if payslip_id:
#                        payslip_id = payslip_id.ids
                        payslip_ids.append(payslip_id[0])
                else:
                    payslip_id = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                                     ('date_from', '<=', context.get("date_to")),
                                                     ('employee_id', '=' , employee.id),
                                                     ('state', 'in', ['draft', 'done', 'verify'])
                                                     ])
                    if payslip_id:
#                        payslip_id = payslip_id.ids
                        payslip_ids.append(payslip_id[0])
            if not payslip_ids:
                raise Warning("No payslip found!")
            total_ammount = sum([line.total for payslip in payslip_ids
                                 for line in payslip.line_ids
                                 if line.code == 'NET'])
            new_total_ammount = '%.2f' % total_ammount
            worksheet.write(row, 0, "All", border_style)
            worksheet.write(row, 1, "", border_style)
            worksheet.write(row, 2, res_user.company_id.currency_id.symbol + ' ' + tools.ustr(locale.format("%.2f", float(new_total_ammount), grouping=True)), border_style)

            fp = StringIO()
            workbook.save(fp)
            fp.seek(0)
            data = fp.read()
            fp.close()
            res = base64.b64encode(data)

            cheque_summary_id = self.env['excel.export.cheque.summay'].create({'name':'Cheque Summary.xls', 'file': res})
            return {
                  'name': _('Binary'),
                  'res_id': cheque_summary_id.id,
                  'view_type': 'form',
                  "view_mode": 'form',
                  'res_model': 'excel.export.cheque.summay',
                  'type': 'ir.actions.act_window',
                  'target': 'new',
                  'context': context,
                }
