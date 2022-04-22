# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
try:
    import xlwt
except ImportError:
    xlwt = None
from cStringIO import StringIO
from odoo import tools
from odoo.exceptions import ValidationError
import time

@api.model
def intcomma(self, n, thousands_sep):
    sign = '-' if n < 0 else ''
    n = tools.ustr(abs(n)).split('.')
    dec = '' if len(n) == 1 else '.' + n[1]
    n = n[0]
    m = len(n)
    return sign + (tools.ustr(thousands_sep[1]).join([n[0:m % 3]] +
                                                     [n[i:i + 3]
                                                      for i in
                                                      range(m % 3, m, 3)])
                   ).lstrip(tools.ustr(thousands_sep[1])) + dec


class PayrollExcelBankTransferRequest(models.TransientModel):
    _name = "payroll.excel.bank.transfer.request"

    file = fields.Binary("Click On Save As Button To Download File",
                         readonly=True)
    name = fields.Char("Name" , size=32, default='Bank Transfer Request.xls')


class BankTransferRequest(models.TransientModel):

    _name = 'bank.transfer.request'

    employee_ids = fields.Many2many('hr.employee',
                                    'bank_transfer_hr_employee_payroll_rel',
                                    'emp_id4', 'employee_id', 'Employee Name')
    date_start = fields.Date('Date Start')
    date_end = fields.Date('Date End')
    select_emp_manually = fields.Boolean(string='Select Employees Manually', default=False)

    @api.onchange('date_start', 'date_end')
    def onchange_check_date(self):
        """
        This onchange method used to end date should be greater than start date.
        """
        if self.date_end and self.date_start and \
        self.date_end < self.date_start:
            raise ValidationError("End date should be greater than start date!")

    @api.multi
    def print_bank_transfer_request_xls(self):
        cr, uid, context = self.env.args
        if context is None:
            context = {}
        data = self.read([])[0]
        if self.date_end and self.date_start and \
        self.date_end < self.date_start:
            raise ValidationError("End date should be greater than start date!")
        context = dict(context)
        context.update({'employee_ids': data['employee_ids'],
                        'date_from': data['date_start'],
                        'date_to': data['date_end']})

        HrEmployee = self.env['hr.employee']
        if self.select_emp_manually == False:
            employee_ids = HrEmployee.search([])
            employee_ids = [emp.id for emp in employee_ids]
        else:
            employee_ids = context.get('employee_ids')
        date_start = context.get('date_from')
        date_end = context.get('date_to')
        res_user = self.env["res.users"].browse(uid)
        res_lang_ids = self.env['res.lang'].search([('code', '=', res_user.lang)], limit=1)
        payslip_ids = self.env['hr.payslip'].search([('employee_id', 'in',
                                              employee_ids),
                                             ('date_from', '>=',
                                              date_start),
                                             ('date_from', '<=',
                                              date_end),
                                             ('state', 'in',
                                              ['done', 'verify',
                                               'draft'])])

        company_ids = payslip_ids.mapped('employee_id.company_id').ids
        bank_ids = payslip_ids.mapped('employee_id.bank_account_id.bank_id').ids

        bank_temp_ids = []
        for bank in bank_ids:
            bank_id = self.env['res.bank'].browse(bank)
            if bank_id.is_loan_bank == True:
                bank_temp_ids.append(bank_id.id)

        workbook = xlwt.Workbook()

        company_id = self.env['res.company']._company_default_get('hr.payroll')

        # WRITE REPORT
        if company_id:
            worksheet = workbook.add_sheet('LOAN - %s' % company_id.name)
            # Export bank transfer request in Excel file.
            font = xlwt.Font()
            font.bold = True
            alignment = xlwt.Alignment()  # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_RIGHT
            style = xlwt.easyxf('align: wrap no')
            style.num_format_str = '0.00'
            borders = xlwt.Borders()
            borders.left = xlwt.Borders.THIN
            borders.right = xlwt.Borders.THIN
            borders.top = xlwt.Borders.THIN
            borders.bottom = xlwt.Borders.THIN

            border_style = xlwt.XFStyle()  # Create Style
            border_style.borders = borders

            border_header_style = xlwt.easyxf('font: name Arial, bold on, height 180; align: wrap no, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;')

            worksheet.col(0).width = 2300
            worksheet.col(1).width = 12000
            worksheet.col(2).width = 7500
            worksheet.col(3).width = 7500
            worksheet.col(4).width = 7500
            worksheet.col(5).width = 7500
            worksheet.row(12).height = 500

            thousands_sep = ","
            if res_lang_ids and res_lang_ids.ids:
                monetary = False
                thousands_sep = res_lang_ids._data_get()

            row_no = 0
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Tanggal Cetak:', style)
            row_no +=1
            worksheet.write(row_no, 1, 'No Surat:', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Kepada:', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Yth. Pimpinan Bank', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Di Tempat', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)

            # HEADER
            row_no += 1
            worksheet.write(row_no, 0, 'No.', border_header_style)
            worksheet.write(row_no, 1, 'NAMA KARYAWAN', border_header_style)
            worksheet.write(row_no, 2, 'NAMA BANK', border_header_style)
            worksheet.write(row_no, 3, 'No.REKENING', border_header_style)
            worksheet.write(row_no, 4, 'NAMA ACCOUNT', border_header_style)
            worksheet.write(row_no, 5, 'JUMLAH', border_header_style)
            no = 1
            final_total = 0.00

            for data in bank_temp_ids:
                bank_id = self.env['res.bank'].browse(data)
                for payslip in payslip_ids:
                    if payslip.employee_id.bank_account_id.bank_id.id == data and payslip.employee_id.is_apply_credit == True and payslip.employee_id.company_id.id == company_id.id:
                        status = False
                        row_no += 1
                        worksheet.write(row_no, 0, tools.ustr(str(no)), border_style)
                        worksheet.write(row_no, 1, tools.ustr(payslip.employee_id.name or ''), border_style)
                        worksheet.write(row_no, 2, tools.ustr(payslip.employee_id.bank_account_id.bank_id.name or ''), border_style)
                        worksheet.write(row_no, 3, tools.ustr(payslip.employee_id.bank_account_id.acc_number or '') , border_style)
                        worksheet.write(row_no, 4, tools.ustr(payslip.employee_id.bank_account_id.partner_id.name or ''), border_style)
                        net_amount = 0.00
                        for line in payslip.line_ids:
                            if line.code == 'TAKEHOMEPAY':
                                final_total += line.amount
                                net_amount = line.amount
                        net_amount = round(net_amount)
                        worksheet.write(row_no, 5, net_amount, border_style)
                        # net_amount = intcomma(self, float(net_amount), thousands_sep)
                        # worksheet.write(row_no, 5, tools.ustr(net_amount).ljust(len(tools.ustr(net_amount).split('.')[0]) + 3, '0'), border_style)
                        no += 1
 
            row_no += 1
            worksheet.write(row_no, 0, '', border_header_style)
            worksheet.write(row_no, 1, 'TOTAL', border_header_style)
            worksheet.write(row_no, 2, '', border_header_style)
            worksheet.write(row_no, 3, '', border_header_style)
            worksheet.write(row_no, 4, '', border_header_style)

            final_total = round(final_total)
            worksheet.write(row_no, 5, final_total, border_style)
            # final_total = intcomma(self, float(final_total), thousands_sep)
            # worksheet.write(row_no, 5, tools.ustr(final_total).ljust(len(tools.ustr(final_total).split('.')[0]) + 3, '0'), border_header_style)

            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Roberto Blasius Sangka', style)
            row_no += 1
            worksheet.write(row_no, 1, 'COO', style)
 
# --------------------------------------------------------------------

        # Add new sheet (sheet for data that does not have a loan)
        if company_id:
            worksheet = workbook.add_sheet('%s' % company_id.name)
            # Export bank transfer request in Excel file.
            font = xlwt.Font()
            font.bold = True
            alignment = xlwt.Alignment()  # Create Alignment
            alignment.horz = xlwt.Alignment.HORZ_RIGHT
            style = xlwt.easyxf('align: wrap no')
            style.num_format_str = '0.00'
            worksheet.col(0).width = 2300
            worksheet.col(1).width = 12000
            worksheet.col(2).width = 7500
            worksheet.col(3).width = 7500
            worksheet.col(4).width = 7500
            worksheet.col(5).width = 7500
            worksheet.row(12).height = 500

            thousands_sep = ","
            if res_lang_ids and res_lang_ids.ids:
                monetary = False
                thousands_sep = res_lang_ids._data_get()                    
            
            row_no = 0
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Tanggal Cetak:', style)
            row_no += 1
            worksheet.write(row_no, 1, 'No Surat:', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Kepada:', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Yth. Pimpinan Bank', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Di Tempat', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)

            # HEADER
            row_no += 1
            worksheet.write(row_no, 0, 'No.', border_header_style)
            worksheet.write(row_no, 1, 'NAMA KARYAWAN', border_header_style)
            worksheet.write(row_no, 2, 'NAMA BANK', border_header_style)
            worksheet.write(row_no, 3, 'No.REKENING', border_header_style)
            worksheet.write(row_no, 4, 'NAMA ACCOUNT', border_header_style)
            worksheet.write(row_no, 5, 'JUMLAH', border_header_style)
            no = 1
            final_total = 0.00
            for payslip in payslip_ids:
                if not payslip.employee_id.bank_account_id.bank_id or payslip.employee_id.bank_account_id.bank_id.id not in bank_temp_ids or payslip.employee_id.bank_account_id.bank_id.id in bank_temp_ids and payslip.employee_id.is_apply_credit == False:
                    if payslip.employee_id.company_id.id == company_id.id:
                        row_no += 1
                        worksheet.write(row_no, 0, tools.ustr(no), border_style)
                        worksheet.write(row_no, 1, tools.ustr(payslip.employee_id.name or ''), border_style)
                        worksheet.write(row_no, 2, tools.ustr(payslip.employee_id.bank_account_id.bank_id.name or ''), border_style)
                        worksheet.write(row_no, 3, tools.ustr(payslip.employee_id.bank_account_id.acc_number or '') , border_style)
                        worksheet.write(row_no, 4, tools.ustr(payslip.employee_id.bank_account_id.partner_id.name or ''), border_style)
                        net_amount = 0.00
                        for line in payslip.line_ids:
                            if line.code == 'TAKEHOMEPAY':
                                final_total += line.amount
                                net_amount = line.amount

                        net_amount = round(net_amount)
                        worksheet.write(row_no, 5, net_amount, border_style)
                        # net_amount = intcomma(self, float(net_amount), thousands_sep)
                        # worksheet.write(row_no, 5, tools.ustr(net_amount).ljust(len(tools.ustr(net_amount).split('.')[0]) + 3, '0'), border_style)
                        no += 1

            row_no += 1
            worksheet.write(row_no, 0, '', border_header_style)
            worksheet.write(row_no, 1, 'TOTAL', border_header_style)
            worksheet.write(row_no, 2, '', border_header_style)
            worksheet.write(row_no, 3, '', border_header_style)
            worksheet.write(row_no, 4, '', border_header_style)
            final_total = round(final_total)
            worksheet.write(row_no, 5, final_total, border_style)
            # final_total = intcomma(self, float(final_total), thousands_sep)
            # worksheet.write(row_no, 5, tools.ustr(final_total).ljust(len(tools.ustr(final_total).split('.')[0]) + 3, '0'), border_header_style)


            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, '', style)
            row_no += 1
            worksheet.write(row_no, 1, 'Roberto Blasius Sangka', style)
            row_no += 1
            worksheet.write(row_no, 1, 'COO', style)

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        file_res = base64.b64encode(data)

        module_rec = self.env['payroll.excel.bank.transfer.request'].create({'file':file_res, 'name':'bank transfer request.xls'})
        return {
          'name': _('Bank Transfer Request Xls Reports'),
          'res_id': module_rec.id,
          'view_type': 'form',
          "view_mode": 'form',
          'res_model': 'payroll.excel.bank.transfer.request',
          'type': 'ir.actions.act_window',
          'target': 'new',
        }

