# -*- coding: utf-8 -*-

import base64
import locale

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import tools
from openerp.exceptions import Warning
from openerp import api, fields , models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

import xlwt
from cStringIO import StringIO


class ExcelExportPayslip(models.TransientModel):
    _name = "excel.export.payslip"

    file = fields.Binary("Click On Save As Button To Download File", readonly=True)
    name = fields.Char("Name" , size=32, default='payslip_export.xls')


class PayslipExportReportWizard(models.TransientModel):
    _name = 'payslip.export.report.wizard'

    employee_ids = fields.Many2many('hr.employee', 'payslip_wizard_employee_id', 'payslip_id', 'employee_id', string='Employees')
    date_start = fields.Date('Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end = fields.Date('Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))
    export_report = fields.Selection([('excel', 'Excel')], "Export", default='excel')

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
    def print_payslip_export_report(self):
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

        context.update({'employee_ids': data['employee_ids'], 'date_from': start_date, 'date_to': end_date})
        # Create Export report in Excel file.
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Sheet 1', cell_overwrite_ok=True)
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
        # worksheet.col(0).width = 5000
        # worksheet.col(1).width = 5000
        worksheet.row(0).height = 500
        worksheet.row(1).height = 500
        for x in range(0,41):
            worksheet.col(x).width = 6000
        # worksheet.col(9).width = 5000
        # worksheet.col(11).width = 5000
        borders = xlwt.Borders()
        borders.top = xlwt.Borders.MEDIUM
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        border_style1 = xlwt.easyxf('font: bold 1')
        border_style1.borders = borders
        payslip_obj = self.env['hr.payslip']
        employee_obj = self.env['hr.employee']
        employee_ids = employee_obj.search([('id', 'in', context.get("employee_ids"))]) or employee_obj.search([])
        style = xlwt.easyxf('align: wrap yes', style)
        if employee_ids and employee_ids.ids:
            payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                              ('date_from', '<=', context.get("date_to")),
                                              ('employee_id', 'in' , employee_ids.ids),
                                              ('state', 'in', ['draft', 'done', 'verify'])
                                            ])
            if payslip_ids:
                row = 0
                worksheet.write(row, 0, "Periode", border_style1)
                worksheet.write(row, 1, "Rooster", border_style1)
                worksheet.write(row, 2, "Nomor Pegawai", border_style1)
                worksheet.write(row, 3, "BANK", border_style1)
                worksheet.write(row, 4, "Nama Rekening", border_style1)
                worksheet.write(row, 5, "Nomor Rekening", border_style1)
                worksheet.write(row, 6, "Jenis Kelamin", border_style1)
                worksheet.write(row, 7, "Posisi", border_style1)
                worksheet.write(row, 8, "Lokasi", border_style1)
                worksheet.write(row, 9, "Nama Pegawai", border_style1)
                worksheet.write(row, 10, "Status Pernikahan", border_style1)
                worksheet.write(row, 11, "Upah Pokok dan Tunjangan Tetap", border_style1)
                worksheet.write(row, 12, "Upah ON Duty", border_style1)
                worksheet.write(row, 13, "Upah OFF Duty", border_style1)
                worksheet.write(row, 14, "Upah Extend", border_style1)
                worksheet.write(row, 15, "Upah Alarm Center/Induction", border_style1)
                worksheet.write(row, 16, "Upah Pokok", border_style1)
                worksheet.write(row, 17, "Tunjangan Jabatan", border_style1)
                worksheet.write(row, 18, "Tunjangan Profesi", border_style1)
                worksheet.write(row, 19, "Tunjangan Lokasi", border_style1)
                worksheet.write(row, 20, "Uang Makan / Transport", border_style1)
                worksheet.write(row, 21, "SPPD", border_style1)
                worksheet.write(row, 22, "Lembur", border_style1)
                worksheet.write(row, 23, "Jamsostek JHT", border_style1)
                worksheet.write(row, 24, "Jamsostek JP", border_style1)
                worksheet.write(row, 25, "PPh 21", border_style1)
                worksheet.write(row, 26, "BPJS Kesehatan", border_style1)
                worksheet.write(row, 27, "Pinjaman/Kelebihan Bayar", border_style1)
                worksheet.write(row, 28, "Take Home Pay", border_style1)
                row += 1
        result = {}
        payslip_data = {}
        department_total_amount = 0.0
        for employee in employee_ids:
            payslip_ids = payslip_obj.search([('date_from', '>=', context.get("date_from")),
                                              ('date_from', '<=', context.get("date_to")),
                                              ('employee_id', '=' , employee.id),
                                              ('state', 'in', ['draft', 'done', 'verify'])
                                            ])
            if not payslip_ids:
                continue

            for payslip in payslip_ids:
                info1 = on_duty = onl_duty = off_duty = ext = ho = basic = tjb = tpr = tlk = um = ut = sppd = lbr = bpjsjht = bpjsjp = oph21 = pph21 = bpjs = lo = thp = 0.00
                # month_year = datetime.strptime(payslip_date, DEFAULT_SERVER_DATE_FORMAT).strftime('%B %Y')
                for line in payslip.line_ids:
                    if line.code == 'INFO1':
                        info1 += line.total
                    if line.code == 'ON':
                        on_duty += line.total
                    if line.code == 'ONL':
                        onl_duty += line.total
                    if line.code == 'OFF':
                        off_duty += line.total
                    if line.code == 'EXT':
                        ext += line.total
                    if line.code == 'HO':
                        ho += line.total
                    if line.code == 'BASIC':
                        basic += line.total
                    if line.code == 'TJB':
                        tjb += line.total
                    if line.code == 'TPR':
                        tpr += line.total
                    if line.code == 'TLK':
                        tlk += line.total
                    if line.code == 'UM':
                        um += line.total
                    if line.code == 'UT':
                        ut += line.total
                    if line.code == 'SPPD':
                        sppd += line.total
                    if line.code == 'LBR':
                        lbr += line.total
                    if line.code == 'BPJSJHT':
                        bpjsjht += line.total
                    if line.code == 'BPJSJP':
                        bpjsjp += line.total
                    if line.code == 'OPH21':
                        oph21 += line.total
                    if line.code == 'PPH21':
                        pph21 += line.total
                    if line.code == 'BPJS':
                        bpjs += line.total
                    if line.code == 'LO':
                        lo += line.total
                    if line.code == 'THP':
                        thp += line.total

                worksheet.write(row, 0, str(payslip.date_from) + " - " + str(payslip.date_to))
                worksheet.write(row, 1, payslip.contract_id.x_rooster or '')
                worksheet.write(row, 2, payslip.employee_id.otherid or '')
                worksheet.write(row, 3, payslip.employee_id.bank_account_id.bank_name or '')
                worksheet.write(row, 4, payslip.employee_id.bank_account_id.bank_name or '')
                worksheet.write(row, 5, payslip.employee_id.bank_account_id.acc_number or '')
                worksheet.write(row, 6, payslip.employee_id.gender or '')
                worksheet.write(row, 7, payslip.employee_id.job_id.name or '')
                worksheet.write(row, 8, payslip.employee_id.work_location or '')
                worksheet.write(row, 9, payslip.employee_id.name or '')
                worksheet.write(row, 10, payslip.employee_id.marital or '')
                worksheet.write(row, 11, tools.ustr('{0:,.0f}'.format(info1)))
                worksheet.write(row, 12, tools.ustr('{0:,.0f}'.format(on_duty)) or tools.ustr('{0:,.0f}'.format(onl_duty)))
                worksheet.write(row, 13, tools.ustr('{0:,.0f}'.format(off_duty)))
                worksheet.write(row, 14, tools.ustr('{0:,.0f}'.format(ext)))
                worksheet.write(row, 15, tools.ustr('{0:,.0f}'.format(ho)))
                worksheet.write(row, 16, tools.ustr('{0:,.0f}'.format(basic)))
                worksheet.write(row, 17, tools.ustr('{0:,.0f}'.format(tjb)))
                worksheet.write(row, 18, tools.ustr('{0:,.0f}'.format(tpr)))
                worksheet.write(row, 19, tools.ustr('{0:,.0f}'.format(tlk)))
                worksheet.write(row, 20, tools.ustr('{0:,.0f}'.format(um)) + ' / ' + tools.ustr('{0:,.0f}'.format(ut)))
                worksheet.write(row, 21, tools.ustr('{0:,.0f}'.format(sppd)))
                worksheet.write(row, 22, tools.ustr('{0:,.0f}'.format(lbr)))
                worksheet.write(row, 23, tools.ustr('{0:,.0f}'.format(bpjsjht)))
                worksheet.write(row, 24, tools.ustr('{0:,.0f}'.format(bpjsjp)))
                worksheet.write(row, 25, tools.ustr('{0:,.0f}'.format(oph21 or pph21)))
                worksheet.write(row, 26, tools.ustr('{0:,.0f}'.format(bpjs)))
                worksheet.write(row, 27, tools.ustr('{0:,.0f}'.format(lo)))
                worksheet.write(row, 28, tools.ustr('{0:,.0f}'.format(thp)))
                row += 1

        fp = StringIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.b64encode(data)
        excel_export_summary_id = self.env['excel.export.payslip'].create({'name': 'Payslip Export.xls', 'file': res})
        return {
            'name': _('Binary'),
            'res_id': excel_export_summary_id.id,
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'excel.export.payslip',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
