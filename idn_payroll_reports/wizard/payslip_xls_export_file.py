# -*- coding: utf-8 -*-

import base64
import locale

from datetime import datetime

from odoo import tools
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError

import xlwt
from cStringIO import StringIO


class PayslipXlsExportReport(models.TransientModel):

    _name = "payslip.xls.export.report"

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name", default='payslip export.xls')


class PayslipXlsExportFile(models.TransientModel):

    _name = 'payslip.xls.export.file'

    employee_ids = fields.Many2many('hr.employee',
                                    'payslip_export_hr_employee_payroll_rel',
                                    'emp_id4', 'employee_id', 'Employee Name')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')

    @api.onchange('date_start', 'date_end')
    def onchange_dates(self):
        """
        This onchange method is used to check end date should be greater than 
        start date.
        """
        if self.date_start and self.date_end and \
        self.date_end < self.date_start:
            raise ValidationError("End date should be greater than start date!")

    @api.multi
    def print_payslip_xls_export(self):

        context = self._context
        context = dict(context)
        data = self.read([])[0]
        context.update({'employee_ids': data['employee_ids'],
                        'date_start': data['date_start'],
                        'date_end': data['date_end']})
        # check start date sould less then end date.
        if self.date_start and self.date_end and \
        self.date_end < self.date_start:
            raise ValidationError("End date should be greater than start date!")

        # Export payslip report in xls fiel.
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap no')
        style2 = xlwt.easyxf('align: wrap no, vert centre, horiz right')
        style.num_format_str = '0.00'
        style2.num_format_str = '0.00'
        bprder_bottom_style2 = xlwt.easyxf('borders: bottom thin; align: wrap no, vert centre, horiz right')
        bprder_bottom_style2.num_format_str = '0.00'
        worksheet.col(0).width = 2950
        worksheet.col(1).width = 5190
        worksheet.col(2).width = 12590
        worksheet.col(3).width = 6480
        worksheet.col(4).width = 9090

        employee_ids = context.get('employee_ids')

        date_month_year = datetime.strptime(context.get('date_start'), DEFAULT_SERVER_DATE_FORMAT).strftime('%d %b %Y')
        row_no = 0

        header = xlwt.easyxf('font: name Arial, bold on, height 180;')
        header_table = xlwt.easyxf('font: name Arial, bold on, height 180;align: wrap no, vert centre, horiz center')
        header2 = xlwt.easyxf('font: name Arial, bold on, height 180; align: wrap no, vert centre, horiz right')
        style_black1 = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: bold on, height 180; borders: top thin, bottom thin, top_color black, bottom_color black; align: wrap off , vert centre, horiz right')
        border_left_double = xlwt.easyxf('borders: left double; align: wrap no, vert centre, horiz right')
        border_left_top_bottom_double = xlwt.easyxf('borders: left double, top thin, bottom thin; align: wrap no, vert centre, horiz right')
        border_left_bottom_thin = xlwt.easyxf('borders: left double, bottom thin; align: wrap no, vert centre, horiz right')
        border_right_thin = xlwt.easyxf('borders: right thin; align: wrap no, vert centre, horiz right')
        border_right_thin1 = xlwt.easyxf('borders: right thin; align: wrap no')
        border_top_thin = xlwt.easyxf('borders: top thin; align: wrap no')
        border_top_thin_right = xlwt.easyxf('borders: top thin; align: wrap no, horiz right')
        border_top_thin_right.num_format_str = '0.00'
        border_right_top_thin = xlwt.easyxf('borders: right thin, top thin; align: wrap no, vert centre, horiz right')
        border_left_thin = xlwt.easyxf('borders: left thin; align: wrap no, vert centre, horiz right')
        border_left_thin1 = xlwt.easyxf('borders: left thin; align: wrap no')
        border_bottom_thin = xlwt.easyxf('borders: bottom thin; align: wrap no, vert centre, horiz right')
        border_bottom_thin1 = xlwt.easyxf('borders: bottom thin; align: wrap no')

        style_total = xlwt.easyxf('pattern: pattern solid, fore_colour white; borders: top double, bottom thin, top_color black, bottom_color black; font: bold on, height 180, color black; align: wrap no, vert centre, horiz right')

        payslip_ids = self.env['hr.payslip'].search([('employee_id', 'in', employee_ids),
                                                   ('date_from', '>=', context.get('date_start')),
                                                   ('date_from', '<=', context.get('date_end')),
                                                   ('state', 'in', ['done', 'verify', 'draft'])])
        for payslip in payslip_ids:
            jhtee_name = pph_name = ''
            addition_amount = sub_total = catjht_amt = catjkm_amt = ded_amt = catjkk_amt = catbenifittot_amt = new_sub_total = basic_amt = gross_amt = jhtee = pph = otherdeduction = net_amt = 0.00
            addition_list = []
            deduction_list = []
            payslip_date = payslip.date_from
            month_year = datetime.strptime(payslip_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%B %Y')
            for line in payslip.line_ids:
                if line.code == 'BASIC':
                    basic_amt = line.total
                    sub_total += basic_amt
                    new_sub_total += basic_amt

                if line.category_id.code == 'ALW':
                    addition_dict = {'name': line.name, 'amount': line.total}
                    addition_amount += line.total
                    addition_list.append(addition_dict)
                if line.category_id.code == 'DED':
                    deduction_dict = {'name': line.name, 'amount': line.total}
                    deduction_list.append(deduction_dict)
                    ded_amt += line.total

                if line.category_id.code == 'JHTER':
                    catjht_amt += line.total
                    catbenifittot_amt += line.total
                if line.category_id.code == 'JKMER':
                    catjkm_amt += line.total
                    catbenifittot_amt += line.total
                if line.category_id.code == 'JKKER':
                    catjkk_amt += line.total
                    catbenifittot_amt += line.total
                if line.code == 'GROSS':
                    gross_amt = line.total
                if line.category_id.code == 'PPH21PERMONTH':
                    catbenifittot_amt += line.total
                    pph = line.total
                    pph_name = line.name
                if line.category_id.code == 'JHTEE':
                    jhtee = line.total
                    jhtee_name = line.name
                    ded_amt += line.total
                if line.code == 'OTHERDEDUCTIONS':
                    otherdeduction = line.total
                if line.code == 'NET':
                    net_amt = line.total
            worksheet.write(row_no, 0, '', header_table)
            worksheet.write(row_no, 1, '', header_table)
            worksheet.write(row_no, 2, 'PRODUCTS', header_table)
            worksheet.write(row_no, 3, '', header_table)
            worksheet.write(row_no, 4, '', header_table)
            worksheet.write(row_no, 5, '', header_table)

            row_no += 1
            worksheet.write(row_no, 0, '', header_table)
            worksheet.write(row_no, 1, '', header_table)
            worksheet.write(row_no, 2, 'SALARY RECEIPT DETAILS', header_table)
            worksheet.write(row_no, 3, '', header_table)
            worksheet.write(row_no, 4, '', header_table)
            worksheet.write(row_no, 5, '', header_table)
            row_no = row_no + 1
            nama = dept = ''
            worksheet.write(row_no, 0, '', style_total)
            worksheet.write(row_no, 1, 'Month : ' + tools.ustr(month_year or ''), style_total)
            worksheet.write(row_no, 2, '', style_total)
            worksheet.write(row_no, 3, '', style_total)
            worksheet.write(row_no, 4, '', style_total)
            worksheet.write(row_no, 5, '', border_left_double)
            nama = payslip.employee_id and payslip.employee_id.name or ''
            dept = payslip.employee_id and payslip.employee_id.department_id and payslip.employee_id.department_id.name or ''
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Name', style)
            worksheet.write(row_no, 2, tools.ustr(nama), style)
            worksheet.write(row_no, 3, 'Division', border_right_thin1)
            worksheet.write(row_no, 4, tools.ustr(dept), style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_bottom_thin)
            worksheet.write(row_no, 1, 'Transfer by', border_bottom_thin1)
            worksheet.write(row_no, 2, 'BCA', border_bottom_thin1)
            worksheet.write(row_no, 3, 'Position', border_bottom_thin1)
            worksheet.write(row_no, 4, tools.ustr(payslip.employee_id and payslip.employee_id.job_id and payslip.employee_id.job_id.name or ''), border_left_thin1)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Basic Salary', style)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, '', border_right_thin)
            worksheet.write(row_no, 4, tools.ustr(locale.format("%.2f", float(basic_amt), grouping=True)), style2)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Addition', style)
            worksheet.write(row_no, 4, '', border_left_thin)
            worksheet.write(row_no, 5, '', border_left_double)
            gross_row_no = row_no + 1
            worksheet.write(gross_row_no, 0, '', border_left_double)
            worksheet.write(gross_row_no, 4, '', border_left_thin)
            worksheet.write(gross_row_no, 5, '', border_left_double)
            gross_row_no += 1
            worksheet.write(gross_row_no, 0, '', border_left_double)
            worksheet.write(gross_row_no, 4, '', border_left_thin)
            worksheet.write(gross_row_no, 5, '', border_left_double)
            gross_row_no += 1
            worksheet.write(gross_row_no, 0, '', border_left_double)
            worksheet.write(gross_row_no, 4, '', border_left_thin)
            worksheet.write(gross_row_no, 5, '', border_left_double)
            gross_row_no += 1

            if addition_list:
                for addition in addition_list[:4]:
                    worksheet.write(row_no, 2, addition['name'], style)
                    worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(addition['amount']), grouping=True)), style2)
                    row_no += 1

            worksheet.write(gross_row_no, 0, '', border_left_double)
            worksheet.write(gross_row_no, 1, '', style)
            worksheet.write(gross_row_no, 2, '', style)
            worksheet.write(gross_row_no, 3, '', border_right_top_thin)
            worksheet.write(gross_row_no, 4, tools.ustr(locale.format("%.2f", float(addition_amount), grouping=True)), style2)
            worksheet.write(gross_row_no, 5, '', border_left_double)

            row_no = gross_row_no + 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 3, '', border_right_thin)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Deduction', style)
            worksheet.write(row_no, 4, '', border_left_thin)
            worksheet.write(row_no, 5, '', border_left_double)

            deduction_row_no = row_no + 1
            worksheet.write(deduction_row_no, 0, '', border_left_double)
            worksheet.write(deduction_row_no, 4, '', border_left_thin)
            worksheet.write(deduction_row_no, 5, '', border_left_double)
            deduction_row_no += 1
            worksheet.write(deduction_row_no, 0, '', border_left_double)
            worksheet.write(deduction_row_no, 4, '', border_left_thin)
            worksheet.write(deduction_row_no, 5, '', border_left_double)
            deduction_row_no += 1
            worksheet.write(deduction_row_no, 0, '', border_left_double)
            worksheet.write(deduction_row_no, 4, '', border_left_thin)
            worksheet.write(deduction_row_no, 5, '', border_left_double)
            deduction_row_no += 1
            if deduction_list:
                for deduction in deduction_list[:2]:
                    worksheet.write(row_no, 2, deduction['name'], style)
                    worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(deduction['amount']), grouping=True)), style2)
                    row_no += 1
            else:
                row_no += 2

            if jhtee_name and jhtee:
                worksheet.write(row_no, 2, jhtee_name, style)
                worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(jhtee), grouping=True)), style2)
                row_no += 1

            worksheet.write(deduction_row_no, 0, '', border_left_double)
            worksheet.write(deduction_row_no, 1, '', style)
            worksheet.write(deduction_row_no, 2, 'Total Deduction', style)
            worksheet.write(deduction_row_no, 3, '', border_right_top_thin)
            worksheet.write(deduction_row_no, 4, tools.ustr(locale.format("%.2f", float(ded_amt), grouping=True)), border_bottom_thin)
            worksheet.write(deduction_row_no, 5, '', border_left_double)
            row_no = deduction_row_no + 1
            worksheet.write(row_no, 0, '', border_left_bottom_thin)
            worksheet.write(row_no, 1, 'Total Paid/Transfer to Employee ', header)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, '', border_right_thin)
            worksheet.write(row_no, 4, tools.ustr(locale.format("%.2f", float(net_amt), grouping=True)), header2)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Benefit from Company:', border_top_thin)
            worksheet.write(row_no, 2, ' - PPh Psl. 21', border_top_thin)
            worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(pph), grouping=True)), border_top_thin_right)
            worksheet.write(row_no, 4, '', border_top_thin)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, '', style)
            worksheet.write(row_no, 2, ' - Medical Insurance', style)
            worksheet.write(row_no, 3, 0.0, style2)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1

            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, '', style)
            worksheet.write(row_no, 2, ' - JHT', style)
            worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(catjht_amt), grouping=True)), style2)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1

            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, '', style)
            worksheet.write(row_no, 2, ' - JKM', style)
            worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(catjkm_amt), grouping=True)), style2)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1

            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, '', style)
            worksheet.write(row_no, 2, ' - JKK', style)
            worksheet.write(row_no, 3, tools.ustr(locale.format("%.2f", float(catjkk_amt), grouping=True)), style2)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1

            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, '', style)
            worksheet.write(row_no, 2, 'Total Benefits', style)
            worksheet.write(row_no, 3, '', border_top_thin)
            worksheet.write(row_no, 4, tools.ustr(locale.format("%.2f", float(catbenifittot_amt), grouping=True)), bprder_bottom_style2)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1

            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Total Paid + Benefits by Company', header)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, '', style)
            worksheet.write(row_no, 4, tools.ustr(locale.format("%.2f", float(catbenifittot_amt + net_amt), grouping=True)), header2)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, date_month_year, style)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, '', style)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Issued by,', style)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, 'Received By,', style)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 1, 'Finance & Account Dept', style)
            worksheet.write(row_no, 2, '', style)
            worksheet.write(row_no, 3, '', style)
            worksheet.write(row_no, 4, '', style)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_double)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 1
            worksheet.write(row_no, 0, '', border_left_top_bottom_double)
            worksheet.write(row_no, 1, '', style_black1)
            worksheet.write(row_no, 2, 'PRIVATE & CONFIDENTIAL', style_black1)
            worksheet.write(row_no, 3, '', style_black1)
            worksheet.write(row_no, 4, '', style_black1)
            worksheet.write(row_no, 5, '', border_left_double)
            row_no += 3
        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        file_res = base64.b64encode(data)
        module_rec = self.env['payslip.xls.export.report'].create({'file':file_res, 'name':'Payslip Export.xls'})
        return {
          'name': _('Payroll Export Xls Reports'),
          'res_id': module_rec.id,
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'payslip.xls.export.report',
          'type': 'ir.actions.act_window',
          'target': 'new',
#          'context': context,
        }
