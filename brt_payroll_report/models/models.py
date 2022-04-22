# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import locale

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp import tools
from openerp.exceptions import Warning
from openerp import api, fields , models, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT



import xlwt
from cStringIO import StringIO


class ExcelExportPayslip(models.TransientModel):
    _name = "excel.export.payslip"

    file = fields.Binary("Click On Save As Button To Download File", readonly=True)
    name = fields.Char("Name" , size=32, default='payslip_export.xls')

class ExportPayslip(models.TransientModel):
    _name = 'brt.export.report.wizard'

    # employee_ids    = fields.Many2one('hr.employee', string='Employees')
    # employee_ids 	= fields.Many2many('hr.employee', 'payslip_wizard_employee_id', 'payslip_id', 'employee_id', string='Employees')
    date_start 		= fields.Date('Date Start', default=lambda *a: datetime.today().date() + relativedelta(day=1))
    date_end 		= fields.Date('Date End', default=lambda *a: datetime.today().date() + relativedelta(day=31))
    export_report 	= fields.Selection([('PDF', 'PDF'),('Excell', 'Excell')], "Export", default='PDF')
    company_id      = fields.Many2one('res.company','Company',default=lambda self: self.env.user.company_id)
    company         = fields.Char(string='Company ID',default=lambda self: self.env.user.company_id.id)
    # company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True, compute=_default_company )
    @api.onchange('company_id') 
    def company_change(self):
        self.company = self.company_id.id
    # def _default_company(self):
    #     user = self.pool.get('res.users').browse(self._cr, self._uid, self._uid)
    #     if user.company_id:
    #         return user.company_id.id
    #     return self.pool.get('res.company').search([('parent_id', '=', False)])[0]


    @api.multi
    def print_payslip_export_report(self):
        if self.export_report == 'PDF':
            date_start  = self.date_start
            date_end    = self.date_end
            company    = self.company_id.id
            print '======================================================== company ',company
            data = {}
            data['form'] = self.read(['date_start', 'date_end', 'export_report','company'])[0]
            return self._print_report(data)
        else:
            date_start  = self.date_start
            date_end    = self.date_end
            company    = self.company
            GetCompany = self.env['res.company'].search([('id', '=', company)],limit=1)

            # department  = self.env['brt.tb.department.export'].search([])
            # department  = self.env['brt.tb.department.export'].search([('date_from', '>=', date_start),('date_to', '<=', date_end)])
            department  = self.env['brt.tb.department.export'].search([('date_from', '>=', date_start),('date_to', '<=', date_end),('company', '=', int(GetCompany.id))])

            workbook    = xlwt.Workbook()
            worksheet   = workbook.add_sheet('Employee', cell_overwrite_ok=True)
            sheet2      = workbook.add_sheet('Department')
            font        = xlwt.Font()
            font.bold   = True
            header      = xlwt.easyxf('font: bold 1, height 280')
            style       = xlwt.easyxf('align: wrap yes')
            for x in range(0,41):
                worksheet.col(x).width  = 6000
                sheet2.col(x).width     = 6000
            borders = xlwt.Borders()
            borders.top = xlwt.Borders.MEDIUM
            borders.bottom = xlwt.Borders.MEDIUM
            border_style = xlwt.XFStyle()  # Create Style
            border_style.borders = borders
            border_style1 = xlwt.easyxf('font: bold 1')
            border_style1.borders = borders

            periode = 'Periode : ',date_start,' s/d', date_end
            worksheet.write(1, 0, GetCompany.name)
            worksheet.write(2, 0, periode)
            row        = 6
            for z in department:
                worksheet.write(row, 0, z.name)
                row1        = row + 1
                worksheet.write(row1, 0, "No.", border_style1)
                worksheet.write(row1, 1, "Nama", border_style1)
                worksheet.write(row1, 2, "Jabatan", border_style1)
                worksheet.write(row1, 3, "Status", border_style1)
                worksheet.write(row1, 4, "P=TK=0=K=1", border_style1)
                # worksheet.write(5,    4, "A", border_style1)
                worksheet.write(row1, 5, "Grade", border_style1)
                worksheet.write(row1, 6, "Gaji Pokok", border_style1)
                worksheet.write(row1, 7, "Tunj. Jabatan", border_style1)
                worksheet.write(row1, 8, "Tunj. Transport Makan", border_style1)
                worksheet.write(row1, 9, "Tunj. Lainnya", border_style1)
                worksheet.write(row1, 10, "Tunj. Proyek", border_style1)
                worksheet.write(row1, 11, "Rapel", border_style1)
                worksheet.write(row1, 12, "Lembur", border_style1)
                worksheet.write(row1, 13, "Tunj. HP", border_style1)
                worksheet.write(row1, 14, "Reimb. Medical", border_style1)
                worksheet.write(row1, 15, "Pot. Absen", border_style1)
                worksheet.write(row1, 16, "Total THP", border_style1)
                worksheet.write(row1, 17, "Pinjaman", border_style1)
                worksheet.write(row1, 18, "Pot. Jamsostek", border_style1)
                worksheet.write(row1, 19, "Pot. BPJS", border_style1)
                worksheet.write(row1, 20, "Tot. Dibayarkan", border_style1)
                worksheet.write(row1, 21, "PPh 21", border_style1)
                worksheet.write(row1, 22, "Total Gaji", border_style1)
                
                payroll  = self.env['brt.tb.payroll.export'].search([('id_department_export', '=', z.id)])
                rowpay = row1+ 1
                no = 1
                for a in payroll:
                    # gapok1              = tools.ustr('{0:,.0f}'.format(a.gapok))
                    # t_jabatan1          = tools.ustr('{0:,.0f}'.format(a.t_jabatan))
                    # tunj_transport_makan1          = tools.ustr('{0:,.0f}'.format(a.tunj_transport_makan))
                    # tunj_lain1          = tools.ustr('{0:,.0f}'.format(a.tunj_lain))
                    # rapel1              = tools.ustr('{0:,.0f}'.format(a.rapel))
                    # tunjangan_proyek1   = tools.ustr('{0:,.0f}'.format(a.tunjangan_proyek))
                    # lembur1             = tools.ustr('{0:,.0f}'.format(a.lembur))
                    # t_hp1               = tools.ustr('{0:,.0f}'.format(a.t_hp))
                    # reimb_medical1      = tools.ustr('{0:,.0f}'.format(a.reimb_medical))
                    # pot_absen1          = tools.ustr('{0:,.0f}'.format(a.pot_absen))
                    # thp1                = tools.ustr('{0:,.0f}'.format(a.thp))
                    # reimb_medical1      = tools.ustr('{0:,.0f}'.format(a.reimb_medical))
                    # pot_absen1          = tools.ustr('{0:,.0f}'.format(a.pot_absen))
                    # thp1                = tools.ustr('{0:,.0f}'.format(a.thp))
                    # pinjaman1           = tools.ustr('{0:,.0f}'.format(a.pinjaman))
                    # jamsostek1          = tools.ustr('{0:,.0f}'.format(a.jamsostek))
                    # bpjs1               = tools.ustr('{0:,.0f}'.format(a.bpjs))
                    # tot_dibayarkan1     = tools.ustr('{0:,.0f}'.format(a.tot_dibayarkan))
                    # pph211              = tools.ustr('{0:,.0f}'.format(a.pph21))
                    # tot_gaji1           = tools.ustr('{0:,.0f}'.format(a.tot_gaji))

                    # gapok               = 'Rp. ',gapok1
                    # t_jabatan           = 'Rp. ',t_jabatan1
                    # tunj_transport_makan           = 'Rp. ',tunj_transport_makan1
                    # tunj_lain           = 'Rp. ',tunj_lain1
                    # rapel               = 'Rp. ',rapel1
                    # tunjangan_proyek    = 'Rp. ',tunjangan_proyek1
                    # lembur              = 'Rp. ',lembur1
                    # t_hp                = 'Rp. ',t_hp1
                    # reimb_medical       = 'Rp. ',reimb_medical1
                    # pot_absen           = 'Rp. ',pot_absen1
                    # thp                 = 'Rp. ',thp1
                    # pinjaman            = 'Rp. ',pinjaman1
                    # jamsostek           = 'Rp. ',jamsostek1
                    # bpjs                = 'Rp. ',bpjs1
                    # pph21               = 'Rp. ',pph211
                    # tot_dibayarkan      = 'Rp. ',tot_dibayarkan1
                    # tot_gaji            = 'Rp. ',tot_gaji1

                    if a.employee_id.job_id.name==False:
                        pangkat = '-'
                    else:
                        pangkat = a.employee_id.job_id.name

                    if a.status==False:
                        status = '-'
                    else:
                        status = a.status

                    worksheet.write(rowpay, 0, no)
                    worksheet.write(rowpay, 1, a.name)
                    worksheet.write(rowpay, 2, pangkat)
                    worksheet.write(rowpay, 3, status)
                    kel = a.employee_id.tax_status

                    if a.employee_id.grade==False:
                        grade = '-'
                    else:
                        grade = a.employee_id.grade

                    worksheet.write(rowpay, 4, str(kel))
                    # worksheet.write(rowpay, 5, a.employee_id.children)
                    worksheet.write(rowpay, 5, grade)
                    worksheet.write(rowpay, 6, round(a.gapok))
                    worksheet.write(rowpay, 7, round(a.t_jabatan))
                    worksheet.write(rowpay, 8, round(a.tunj_transport_makan))
                    worksheet.write(rowpay, 9, round(a.tunj_lain))
                    worksheet.write(rowpay, 10, round(a.tunjangan_proyek))
                    worksheet.write(rowpay, 11, round(a.rapel))
                    worksheet.write(rowpay, 12, round(a.lembur))
                    worksheet.write(rowpay, 13, round(a.t_hp))
                    worksheet.write(rowpay, 14, round(a.reimb_medical))
                    worksheet.write(rowpay, 15, round(a.pot_absen))
                    worksheet.write(rowpay, 16, round(a.thp))
                    worksheet.write(rowpay, 17, round(a.pinjaman))
                    worksheet.write(rowpay, 18, round(a.jamsostek))
                    worksheet.write(rowpay, 19, round(a.bpjs))
                    worksheet.write(rowpay, 20, round(a.tot_dibayarkan))
                    worksheet.write(rowpay, 21, round(a.pph21))
                    worksheet.write(rowpay, 22, round(a.tot_gaji))
                    rowpay += 1
                    no += 1

                rowx = rowpay+ 1
                tot_gaji_divisi = 'Total Gaji ', z.name
                KOSONG = ''
                worksheet.write(rowx, 0, tot_gaji_divisi,border_style1)
                worksheet.write(rowx, 1, KOSONG,border_style1)
                worksheet.write(rowx, 2, KOSONG,border_style1)
                worksheet.write(rowx, 3, KOSONG,border_style1)
                worksheet.write(rowx, 4, KOSONG,border_style1)
                worksheet.write(rowx, 5, KOSONG,border_style1)
                self.env.cr.execute("""
                            SELECT
                                COUNT(*) AS tot_pegawai,
                                SUM(round(gapok)) AS gapok, 
                                SUM(round(t_jabatan)) AS t_jabatan, 
                                SUM(round(tunj_transport_makan)) AS tunj_transport_makan, 
                                SUM(round(tunj_lain)) AS tunj_lain, 
                                SUM(round(tunjangan_proyek)) AS tunjangan_proyek, 
                                SUM(round(rapel)) AS rapel, 
                                SUM(round(lembur)) AS lembur, 
                                SUM(round(t_hp)) AS t_hp, 
                                SUM(round(reimb_medical)) AS reimb_medical, 
                                SUM(round(pot_absen)) AS pot_absen, 
                                SUM(round(thp)) AS thp, 
                                SUM(round(pinjaman)) AS pinjaman, 
                                SUM(round(jamsostek)) AS jamsostek, 
                                SUM(round(bpjs)) AS bpjs, 
                                SUM(round(tot_dibayarkan)) AS tot_dibayarkan, 
                                SUM(round(pph21)) AS pph21, 
                                SUM(round(tot_gaji)) AS tot_gaji
                            FROM
                               brt_tb_payroll_export s 
                            WHERE
                                id_department_export = %s
                            """,(z.id,))
                GetTot  = self.env.cr.dictfetchall()
                for data in GetTot :
                    gapok                   = data['gapok']
                    t_jabatan               = data['t_jabatan']
                    tunj_transport_makan    = data['tunj_transport_makan']
                    tunj_lain               = data['tunj_lain']
                    tunjangan_proyek        = data['tunjangan_proyek']
                    rapel                   = data['rapel']
                    lembur                  = data['lembur']
                    t_hp                    = data['t_hp']
                    reimb_medical           = data['reimb_medical']
                    pot_absen               = data['pot_absen']
                    thp                     = data['thp']
                    pinjaman                = data['pinjaman']
                    bpjs                    = data['bpjs']
                    jamsostek               = data['jamsostek']
                    tot_dibayarkan          = data['tot_dibayarkan']
                    pph21                   = data['pph21']
                    tot_gaji                = data['tot_gaji']
                    worksheet.write(rowx, 6, gapok,border_style1)
                    worksheet.write(rowx, 7, t_jabatan,border_style1)
                    worksheet.write(rowx, 8, tunj_transport_makan,border_style1)
                    worksheet.write(rowx, 9, tunj_lain,border_style1)
                    worksheet.write(rowx, 10, tunjangan_proyek,border_style1)
                    worksheet.write(rowx, 11, rapel,border_style1)
                    worksheet.write(rowx, 12, lembur,border_style1)
                    worksheet.write(rowx, 13, t_hp,border_style1)
                    worksheet.write(rowx, 14, reimb_medical,border_style1)
                    worksheet.write(rowx, 15, pot_absen,border_style1)
                    worksheet.write(rowx, 16, thp,border_style1)
                    worksheet.write(rowx, 17, pinjaman,border_style1)
                    worksheet.write(rowx, 18, jamsostek,border_style1)
                    worksheet.write(rowx, 19, bpjs,border_style1)
                    worksheet.write(rowx, 20, tot_dibayarkan,border_style1)
                    worksheet.write(rowx, 21, pph21,border_style1)
                    worksheet.write(rowx, 22, tot_gaji,border_style1)
                row = rowpay+ 4
            result = {}
            # row     = 1
            periode = 'Periode : ',date_start,' s/d', date_end
            sheet2.write(1, 0, periode, border_style1)
            
            row1     = 2
            sheet2.write(row1, 0, "No.", border_style1)
            sheet2.write(row1, 1, "Divisi", border_style1)
            sheet2.write(row1, 2, "", border_style1)
            sheet2.write(row1, 3, "Gaji Pokok", border_style1)
            sheet2.write(row1, 4, "Tunj. Jabatan", border_style1)
            sheet2.write(row1, 5, "Tunj. Transport Makan", border_style1)
            sheet2.write(row1, 6, "Tunj. Lainnya", border_style1)
            sheet2.write(row1, 7, "Tunj. Proyek", border_style1)
            sheet2.write(row1, 8, "Rapel", border_style1)
            sheet2.write(row1, 9, "Lembur", border_style1)
            sheet2.write(row1, 10, "Tunj. HP", border_style1)
            sheet2.write(row1, 11, "Reimb. Medical", border_style1)
            sheet2.write(row1, 12, "Pot. Absen", border_style1)
            sheet2.write(row1, 13, "Total THP", border_style1)
            sheet2.write(row1, 14, "Pinjaman/Kasbon", border_style1)
            sheet2.write(row1, 15, "Pot. Asuransi", border_style1)
            sheet2.write(row1, 16, "Pot. Asuransi", border_style1)
            sheet2.write(row1, 17, "Tot. Dibayarkan", border_style1)
            sheet2.write(row1, 18, "PPh 21", border_style1)
            sheet2.write(row1, 19, "Total Gaji + PPH21", border_style1)
            
            department_detail  = self.env['brt.tb.department.export'].search([('date_from', '>=', date_start),('date_to', '<=', date_end),('company', '=', GetCompany.id)])
            rowA    = row1+1
            nom     = 1
            for x in department_detail:
                sheet2.write(rowA, 0, nom)
                sheet2.write(rowA, 1, x.name)
                self.env.cr.execute("""
                            SELECT 
                                    COUNT(*) AS tot_pegawai,
                                    SUM(round(gapok)) AS gapok, 
                                    SUM(round(t_jabatan)) AS t_jabatan, 
                                    SUM(round(tunj_transport_makan)) AS tunj_transport_makan, 
                                    SUM(round(tunj_lain)) AS tunj_lain, 
                                    SUM(round(tunjangan_proyek)) AS tunjangan_proyek, 
                                    SUM(round(rapel)) AS rapel, 
                                    SUM(round(lembur)) AS lembur, 
                                    SUM(round(t_hp)) AS t_hp, 
                                    SUM(round(reimb_medical)) AS reimb_medical, 
                                    SUM(round(pot_absen)) AS pot_absen, 
                                    SUM(round(thp)) AS thp, 
                                    SUM(round(pinjaman)) AS pinjaman, 
                                    SUM(round(jamsostek)) AS jamsostek, 
                                    SUM(round(bpjs)) AS bpjs, 
                                    SUM(round(tot_dibayarkan)) AS tot_dibayarkan, 
                                    SUM(round(pph21)) AS pph21, 
                                    SUM(round(tot_gaji)) AS tot_gaji
                            FROM brt_tb_payroll_export 
                            WHERE id_department_export = %s 
                            GROUP BY id_department_export
                            """,(x.id,))
                payroll  = self.env.cr.dictfetchall()
                for data in payroll :
                    print '========', data['tunj_transport_makan']
                    # makan_transport = int(data['tunj_transport_makan'])
                    # gapok1                  = tools.ustr('{0:,.0f}'.format(int(data['gapok'])))
                    # t_jabatan1              = tools.ustr('{0:,.0f}'.format(int(data['t_jabatan'])))
                    # tunj_transport_makan1   = tools.ustr('{0:,.0f}'.format(makan_transport))
                    # tunj_lain1              = tools.ustr('{0:,.0f}'.format(int(data['tunj_lain'])))
                    # tunjangan_proyek1       = tools.ustr('{0:,.0f}'.format(int(data['tunjangan_proyek'])))
                    # lembur1                 = tools.ustr('{0:,.0f}'.format(int(data['lembur'])))
                    # t_hp1                   = tools.ustr('{0:,.0f}'.format(int(data['t_hp'])))
                    # reimb_medical1          = tools.ustr('{0:,.0f}'.format(int(data['reimb_medical'])))
                    # pot_absen1              = tools.ustr('{0:,.0f}'.format(int(data['pot_absen'])))
                    # thp1                    = tools.ustr('{0:,.0f}'.format(int(data['thp'])))
                    # pinjaman1               = tools.ustr('{0:,.0f}'.format(int(data['pinjaman'])))
                    # jamsostek1              = tools.ustr('{0:,.0f}'.format(int(data['jamsostek'])))
                    # bpjs1                   = tools.ustr('{0:,.0f}'.format(int(data['bpjs'])))
                    # tot_dibayarkan1         = tools.ustr('{0:,.0f}'.format(int(data['tot_dibayarkan'])))
                    # pph211                  = tools.ustr('{0:,.0f}'.format(int(data['pph21'])))
                    # tot_gaji1               = tools.ustr('{0:,.0f}'.format(int(data['tot_gaji'])))

                    # gapok                   = 'Rp. ',gapok1
                    # t_jabatan               = 'Rp. ',t_jabatan1
                    # tunj_transport_makan    = 'Rp. ',tunj_transport_makan1
                    # tunj_lain               = 'Rp. ',tunj_lain1
                    # tunjangan_proyek        = 'Rp. ',tunjangan_proyek1
                    # lembur                  = 'Rp. ',lembur1
                    # t_hp                    = 'Rp. ',t_hp1
                    # reimb_medical           = 'Rp. ',reimb_medical1
                    # pot_absen               = 'Rp. ',pot_absen1
                    # thp                     = 'Rp. ',thp1
                    # pinjaman                = 'Rp. ',pinjaman1
                    # jamsostek               = 'Rp. ',jamsostek1
                    # bpjs                    = 'Rp. ',bpjs1
                    # tot_dibayarkan          = 'Rp. ',tot_dibayarkan1
                    # pph21                   = 'Rp. ',pph211
                    # tot_gaji                = 'Rp. ',tot_gaji1
                    tot_pegawai             = int(data['tot_pegawai'])
                    makan_transport        = int(data['tunj_transport_makan'])
                    gapok                  = int(data['gapok'])
                    t_jabatan              = int(data['t_jabatan'])
                    tunj_transport_makan   = makan_transport
                    tunj_lain              = int(data['tunj_lain'])
                    tunjangan_proyek       = int(data['tunjangan_proyek'])
                    rapel                  = int(data['rapel'])
                    lembur                 = int(data['lembur'])
                    t_hp                   = int(data['t_hp'])
                    reimb_medical          = int(data['reimb_medical'])
                    pot_absen              = int(data['pot_absen'])
                    thp                    = int(data['thp'])
                    pinjaman               = int(data['pinjaman'])
                    jamsostek              = int(data['jamsostek'])
                    bpjs                   = int(data['bpjs'])
                    tot_dibayarkan         = int(data['tot_dibayarkan'])
                    pph21                  = int(data['pph21'])
                    tot_gaji               = int(data['tot_gaji'])

                    sheet2.write(rowA, 2, tot_pegawai)
                    sheet2.write(rowA, 3, gapok)
                    sheet2.write(rowA, 4, t_jabatan)
                    sheet2.write(rowA, 5, tunj_transport_makan)
                    sheet2.write(rowA, 6, tunj_lain)
                    sheet2.write(rowA, 7, tunjangan_proyek)
                    sheet2.write(rowA, 8, rapel)
                    sheet2.write(rowA, 9, lembur)
                    sheet2.write(rowA, 10, t_hp)
                    sheet2.write(rowA, 11, reimb_medical)
                    sheet2.write(rowA, 12, pot_absen)
                    sheet2.write(rowA, 13, thp)
                    sheet2.write(rowA, 14, pinjaman)
                    sheet2.write(rowA, 15, jamsostek)
                    sheet2.write(rowA, 16, bpjs)
                    sheet2.write(rowA, 17, tot_dibayarkan)
                    sheet2.write(rowA, 18, pph21)
                    sheet2.write(rowA, 19, tot_gaji)
                nom  +=1
                rowA += 1
            rowB = rowA + 3
            rowD = rowA + 2
            rowF = rowA + 1

            sheet2.write(rowF, 0, 'TOTAL PPH21 PEGAWAI',border_style1)
            sheet2.write(rowF, 1, '',border_style1)
            sheet2.write(rowF, 2, '',border_style1)
            sheet2.write(rowF, 3, '',border_style1)
            sheet2.write(rowF, 4, '',border_style1)
            sheet2.write(rowF, 5, '',border_style1)
            sheet2.write(rowF, 6, '',border_style1)
            sheet2.write(rowF, 7, '',border_style1)
            sheet2.write(rowF, 8, '',border_style1)
            sheet2.write(rowF, 9, '',border_style1)
            sheet2.write(rowF, 10, '',border_style1)
            sheet2.write(rowF, 11, '',border_style1)
            sheet2.write(rowF, 12, '',border_style1)
            sheet2.write(rowF, 13, '',border_style1)
            sheet2.write(rowF, 14, '',border_style1)
            sheet2.write(rowF, 15, '',border_style1)
            sheet2.write(rowF, 16, '',border_style1)
            sheet2.write(rowF, 17, '',border_style1)
            sheet2.write(rowF, 18, '',border_style1)
            sheet2.write(rowF, 19, '',border_style1)

            sheet2.write(rowD, 0, 'TOTAL PPH21 BOD',border_style1)
            sheet2.write(rowD, 1, '',border_style1)
            sheet2.write(rowD, 2, '',border_style1)
            sheet2.write(rowD, 3, '',border_style1)
            sheet2.write(rowD, 4, '',border_style1)
            sheet2.write(rowD, 5, '',border_style1)
            sheet2.write(rowD, 6, '',border_style1)
            sheet2.write(rowD, 7, '',border_style1)
            sheet2.write(rowD, 8, '',border_style1)
            sheet2.write(rowD, 9, '',border_style1)
            sheet2.write(rowD, 10, '',border_style1)
            sheet2.write(rowD, 11, '',border_style1)
            sheet2.write(rowD, 12, '',border_style1)
            sheet2.write(rowD, 13, '',border_style1)
            sheet2.write(rowD, 14, '',border_style1)
            sheet2.write(rowD, 15, '',border_style1)
            sheet2.write(rowD, 16, '',border_style1)
            sheet2.write(rowD, 17, '',border_style1)
            sheet2.write(rowD, 18, '',border_style1)
            sheet2.write(rowD, 19, '',border_style1)

            self.env.cr.execute("""
                            SELECT 
                             COUNT(*) AS tot_pegawai,
                                SUM(round(gapok)) AS gapok, 
                                SUM(round(t_jabatan)) AS t_jabatan, 
                                SUM(round(tunj_transport_makan)) AS tunj_transport_makan, 
                                SUM(round(tunj_lain)) AS tunj_lain, 
                                SUM(round(tunjangan_proyek)) AS tunjangan_proyek, 
                                SUM(round(rapel)) AS rapel, 
                                SUM(round(lembur)) AS lembur, 
                                SUM(round(t_hp)) AS t_hp, 
                                SUM(round(reimb_medical)) AS reimb_medical, 
                                SUM(round(pot_absen)) AS pot_absen, 
                                SUM(round(thp)) AS thp, 
                                SUM(round(pinjaman)) AS pinjaman, 
                                SUM(round(jamsostek)) AS jamsostek, 
                                SUM(round(bpjs)) AS bpjs, 
                                SUM(round(tot_dibayarkan)) AS tot_dibayarkan, 
                                SUM(round(pph21)) AS pph21, 
                                SUM(round(tot_gaji)) AS tot_gaji
                                -- COUNT(*) AS tot_pegawai,
                                -- SUM(gapok) AS gapok, 
                                -- SUM(t_jabatan) AS t_jabatan, 
                                -- SUM(tunj_transport_makan) AS tunj_transport_makan, 
                                -- SUM(tunj_lain) AS tunj_lain, 
                                -- SUM(tunjangan_proyek) AS tunjangan_proyek, 
                                -- SUM(rapel) AS rapel, 
                                -- SUM(lembur) AS lembur, 
                                -- SUM(t_hp) AS t_hp, 
                                -- SUM(reimb_medical) AS reimb_medical, 
                                -- SUM(pot_absen) AS pot_absen, 
                                -- SUM(thp) AS thp, 
                                -- SUM(pinjaman) AS pinjaman, 
                                -- SUM(jamsostek) AS jamsostek, 
                                -- SUM(bpjs) AS bpjs, 
                                -- SUM(tot_dibayarkan) AS tot_dibayarkan, 
                                -- SUM(pph21) AS pph21, 
                                -- SUM(tot_gaji) AS tot_gaji
                            FROM brt_tb_payroll_export 
                            WHERE date_from >= %s 
                            AND date_to <= %s
                            AND company = '%s'
                            """,(date_start,date_end,int(GetCompany.id),))
            tot_dep  = self.env.cr.dictfetchall()

            sheet2.write(rowB, 0, 'TOTAL',border_style1)
            sheet2.write(rowB, 1, '',border_style1)
            for dt in tot_dep :
                sheet2.write(rowB, 2, dt['tot_pegawai'],border_style1)
                sheet2.write(rowB, 3, dt['gapok'],border_style1)
                sheet2.write(rowB, 4, dt['t_jabatan'],border_style1)
                sheet2.write(rowB, 5, dt['tunj_transport_makan'],border_style1)
                sheet2.write(rowB, 6, dt['tunj_lain'],border_style1)
                sheet2.write(rowB, 7, dt['tunjangan_proyek'],border_style1)
                sheet2.write(rowB, 8, dt['rapel'],border_style1)
                sheet2.write(rowB, 9, dt['lembur'],border_style1)
                sheet2.write(rowB, 10, dt['t_hp'],border_style1)
                sheet2.write(rowB, 11, dt['reimb_medical'],border_style1)
                sheet2.write(rowB, 12, dt['pot_absen'],border_style1)
                sheet2.write(rowB, 13, dt['thp'],border_style1)
                sheet2.write(rowB, 14, dt['pinjaman'],border_style1)
                sheet2.write(rowB, 15, dt['jamsostek'],border_style1)
                sheet2.write(rowB, 16, dt['bpjs'],border_style1)
                sheet2.write(rowB, 17, dt['tot_dibayarkan'],border_style1)
                sheet2.write(rowB, 18, dt['pph21'],border_style1)
                sheet2.write(rowB, 19, dt['tot_gaji'],border_style1)

            result = {}


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
                # 'context': context,
            }



    def _print_report(self, data):
        data['form'].update(self.read(['date_start', 'date_end','company','company_id', 'export_report'])[0])
        return self.env['report'].with_context(landscape=True).get_action(self, 'brt_payroll_report.export_pdf', data=data)


class ReportPdf(models.AbstractModel):
    _name = 'report.brt_payroll_report.export_pdf'
    
    @api.model
    def render_html(self, docids, data=None):
        date_start  = data['form']['date_start']
        date_end    = data['form']['date_end']
        company     = data['form']['company']
        company_id  = data['form']['company_id']
        GetCompany = self.env['res.company'].search([('id', '=', company)],limit=1)

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        payslip_record = []
        # self.env.cr.execute("""
        #                     SELECT
        #                         s.*
        #                     FROM
        #                         brt_tb_department_export s 
        #                     WHERE s.date_from >= %s
        #                     AND s.date_to <= %s
        #                     AND s.company = %s
        #                     """,(date_start,date_end,int(GetCompany.id)))
        # orders  = self.env.cr.dictfetchall()

        orders = self.env['brt.tb.department.export'].search([('date_from', '>=', date_start),('date_to', '<=', date_end),('company', '=', int(GetCompany.id))])
        print '========= ',orders
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'company_dt': GetCompany.name,
            # 'date_end': date_end,
            # 'date_start': time,
            # 'date_start': time,
            'orders': orders
        }
        return self.env['report'].render('brt_payroll_report.export_pdf', docargs)

        # self.model = self.env.context.get('active_model')
        # docs = self.env[self.model].browse(self.env.context.get('active_id'))
        # sales_records = []
        # orders = self.env['sale.order'].search([('user_id', '=', docs.salesperson_id.id)])
        # if docs.date_from and docs.date_to:
        #    for order in orders:
        #      if parse(docs.date_from) <= parse(order.date_order) and parse(docs.date_to) >= parse(order.date_order):
        #          sales_records.append(order);
        #      else:
        #          raise UserError("Please enter duration")

        # docargs = {
        #    'doc_ids': self.ids,
        #    'doc_model': self.model,
        #    'docs': docs,
        #    'time': time,
        #    'orders': sales_records
        # }
        # return self.env['report'].render('sales_report.report_salesperson', docargs)


class TbBantuDepartment(models.Model):
    _name = 'brt.tb.department.export'

    name            = fields.Char(string="Departmen")
    department_id   = fields.Char(string="department ID")
    bln             = fields.Char(string="bln")
    thn             = fields.Char(string="thn")
    date_from       = fields.Date('Date From')
    date_to         = fields.Date('Date To')
    company         = fields.Char('company')


class TbBantuExportPayrol(models.Model):
    _name = 'brt.tb.payroll.export'

    name            = fields.Char(string='Nama Employees')
    id_payslip      = fields.Char(string='ID Payslip')
    employee_id     = fields.Many2one('hr.employee', string='Employees')
    id_department_export   = fields.Many2one('brt.tb.department.export', string="Departmen")
    status           = fields.Char(string="Status Karyawan")
    grade           = fields.Char(string="Grade")
    gapok           = fields.Float(string="Gaji Pokok")
    t_jabatan       = fields.Float(string="Tunjangan Jabatan")
    thp             = fields.Float(string="THP")
    rapel           = fields.Float(string="Rapel")
    tot_gaji        = fields.Float(string="Total Gaji")
    pot_absen       = fields.Float(string="Potongan Absen")
    reimb_medical   = fields.Float(string="Medical Reiburse")
    jamsostek       = fields.Float(string="Jamsostek")
    tunj_transport_makan       = fields.Float(string="Tunjangan Transport Makan")
    tunj_lain       = fields.Float(string="Tunjangan Lainnya")
    pph21           = fields.Float(string="PPH21")
    bpjs            = fields.Float(string="BPJS")
    t_hp            = fields.Float(string="Tunjangan HP")
    tunjangan_proyek  = fields.Float(string="Tunjangan Proyek")
    tot_dibayarkan  = fields.Float(string="Total Dibayarkan")
    lembur          = fields.Float(string="Lembur")
    pinjaman        = fields.Float(string="Pinjaman")
    date_from       = fields.Date('Date From')
    date_to         = fields.Date('Date To')
    date_to         = fields.Date('Date To')
    company         = fields.Char('company')
    tot_kar         = fields.Float('tot')
    nm_department         = fields.Char('Nama Department')


class hr_payslip(models.Model):
    _inherit        = 'hr.payslip'

    @api.multi
    def act_payslip_done(self):
        for payslip in self:
            print ' CONFIRM ALL ============== Date From', payslip.date_from
            print ' CONFIRM ALL ============== Date To', payslip.date_to

            get_bln_now     = int(datetime.now().strftime("%m")) 
            get_thn_now     = int(datetime.now().strftime("%Y")) 

            date_from       = payslip.date_from
            date_to         = payslip.date_to

            nm_department   = payslip.employee_id.department_id.name
            department_id   = payslip.employee_id.department_id
            id_department   = str(department_id)

            thn             = date_from[0:4]
            bln             = date_from[5:7]

            kontrak         = self.env['hr.contract'].search([('employee_id', '=', payslip.employee_id.id)])
            # kontrak         = self.env['hr.contract'].search([('employee_id', '=', payslip.employee_id.id),('state', '=', 'pending')])

            employee        = self.env['hr.employee'].search([('id', '=', payslip.employee_id.id)])
            lembur          = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'OVERTIME')])
            potAbsen        = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'DEDUNDERTIME')])
            totthp          = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'GROSS')])
            pinjaman1       = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'INSTALL')])
            pinjaman2       = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'OTHERDEDUCTIONS')])
            pinjaman        = float(pinjaman1.total) + float(pinjaman2.total)

            jpe             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'JPE')])
            reimber             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'MR')])
            JHTE            = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'JHTE')])
            jamsostek       = float(jpe.total) + float(JHTE.total)

            BPJSE           = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'BPJSE')])
            BPJSC           = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'BPJSC')])
            pot_bpjs        = float(BPJSE.total)

            tot_dibayarkan  = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TAKEHOMEPAY')])
            pph21           = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'PPH21PERMONTH')])
            gapok           = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'BASIC')])
            tmk             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TMK')])
            tll             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TLL')])
            tpy             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TPY')])
            tjb             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TJB')])
            tsf             = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TSF')])
            th              = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),('code', '=', 'TH')])
            rapel           = self.env['hr.payslip.input'].search([('payslip_id', '=', payslip.id),('code', '=', 'rapel')])

            tot_gaji        = float(pph21.total) + float(tot_dibayarkan.total)

            tot_kar = '1'
            # cek data departmn ditabel bantu apakah sudah ada dengan period yg dipilih
            TBDepartment = self.env['brt.tb.department.export'].search([('date_from', '>=', payslip.date_from),('date_to', '<=', payslip.date_to),('department_id', '=', kontrak.department_id.id)])
            if TBDepartment:
                print ' department ============ ======== ======= ============== ======= ============== ======= ====== Data Ada',TBDepartment
                print ' CONFIRM ALL ============ ======== ======= ============== ======= ============== ======= ======Data  Company ',employee.company_id.id
                print ' CONFIRM ALL ============ ======== ======= ============== ======= ============== ======= ====== Data Ada',TBDepartment.id
                self.env['brt.tb.payroll.export'].create({'grade':employee.grade ,'status':kontrak.type_id.name,'date_from':date_from,'date_to':date_to,'gapok':gapok.total,'t_jabatan':tjb.total,'rapel':rapel.amount,'tot_gaji':tot_gaji,'pot_absen':potAbsen.total,'id_department_export':TBDepartment.id,'reimb_medical':reimber.total,'jamsostek':jamsostek,'pph21':pph21.total,'bpjs':pot_bpjs,'t_hp':th.total,'name':payslip.employee_id.name,'tot_dibayarkan':tot_dibayarkan.total,'thp':totthp.total,'lembur':lembur.total,'pinjaman':pinjaman,'tunjangan_proyek':tpy.total,'tunj_lain':tll.total,'tunj_transport_makan':tmk.total,'employee_id':payslip.employee_id.id,'id_payslip':payslip.id,'company':kontrak.department_id.company_id.id,'nm_department':kontrak.department_id.name,'tot_kar':tot_kar})
            else :
                self.env['brt.tb.department.export'].create({'name':kontrak.department_id.name,'department_id':kontrak.department_id.id,'bln':bln,'thn':thn,'date_from':date_from,'date_to':date_to,'company':kontrak.department_id.company_id.id})
                print ' CONFIRM ALL ============ ======== ======= ============== ======= ============== ======= ======Data  Company ',payslip.company_id.id
                CEKUlang = self.env['brt.tb.department.export'].search([('date_from', '>=', payslip.date_from),('date_to', '<=', payslip.date_to),('department_id', '=', kontrak.department_id.id)])
                self.env['brt.tb.payroll.export'].create({'grade':employee.grade ,'date_from':date_from,'status':kontrak.type_id.name,'date_to':date_to,'gapok':gapok.total,'t_jabatan':tjb.total,'rapel':rapel.amount,'tot_gaji':tot_gaji,'pot_absen':potAbsen.total,'id_department_export':CEKUlang.id,'reimb_medical':reimber.total,'jamsostek':jamsostek,'pph21':pph21.total,'bpjs':pot_bpjs,'t_hp':th.total,'name':payslip.employee_id.name,'tot_dibayarkan':tot_dibayarkan.total,'thp':totthp.total,'lembur':lembur.total,'pinjaman':pinjaman,'tunjangan_proyek':tpy.total,'tunj_lain':tll.total,'tunj_transport_makan':tmk.total,'employee_id':payslip.employee_id.id,'id_payslip':payslip.id,'company':kontrak.department_id.company_id.id,'nm_department':kontrak.department_id.name,'tot_kar':tot_kar})

            payslip.compute_sheet()
            # payslip.write({'state': 'draft'})
            payslip.write({'state': 'done'})
        return 
        # get_bln_now     = int(datetime.now().strftime("%m")) 
        # get_thn_now     = int(datetime.now().strftime("%Y")) 

        # date_from       = self.date_from
        # date_to         = self.date_to

        # nm_department   = self.employee_id.department_id.name
        # department_id   = self.employee_id.department_id
        # id_department   = str(department_id)

        # thn             = date_from[0:4]
        # bln             = date_from[5:7]

        # kontrak         = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        # # kontrak         = self.env['hr.contract'].search([('employee_id', '=', payslip.employee_id.id),('state', '=', 'pending')])

        # employee        = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        # lembur          = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'OVERTIME')])
        # potAbsen        = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'DEDUNDERTIME')])
        # totthp          = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'GROSS')])
        # pinjaman1       = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'INSTALL')])
        # pinjaman2       = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'OTHERDEDUCTIONS')])
        # pinjaman        = float(pinjaman1.total) + float(pinjaman2.total)

        # jpe             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'JPE')])
        # JHTE            = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'JHTE')])
        # jamsostek       = float(jpe.total) + float(JHTE.total)

        # BPJSE           = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'BPJSE')])
        # BPJSC           = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'BPJSC')])
        # pot_bpjs        = float(BPJSE.total) + float(BPJSC.total)

        # tot_dibayarkan  = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TAKEHOMEPAY')])
        # pph21           = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'PPH21PERMONTH')])
        # gapok           = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'BASIC')])
        # tmk             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TMK')])
        # tll             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TLL')])
        # tpy             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TPY')])
        # tjb             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TJB')])
        # tsf             = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TSF')])
        # th              = self.env['hr.payslip.line'].search([('slip_id', '=', self.id),('code', '=', 'TH')])

        # tot_gaji        = float(pph21.total) + float(tot_dibayarkan.total)


        # # cek data departmn ditabel bantu apakah sudah ada dengan period yg dipilih
        # TBDepartment = self.env['brt.tb.department.export'].search([('date_from', '>=', self.date_from),('date_to', '<=', self.date_to),('department_id', '=', kontrak.department_id.id)])
        # if TBDepartment:
        #     print ' department ============ ======== ======= ============== ======= ============== ======= ====== Data Ada',TBDepartment
        #     print ' CONFIRM ALL ============ ======== ======= ============== ======= ============== ======= ====== Data Ada',TBDepartment.id
        #     self.env['brt.tb.payroll.export'].create({'grade':employee.grade ,'date_from':date_from,'date_to':date_to,'gapok':float(gapok.total),'t_jabatan':float(tjb.total),'rapel':self.rapel_amount,'tot_gaji':tot_gaji,'pot_absen':potAbsen.total,'id_department_export':TBDepartment.id,'reimb_medical':self.total_reimburse,'jamsostek':jamsostek,'pph21':pph21.total,'bpjs':pot_bpjs,'t_hp':th.total,'name':self.employee_id.name,'tot_dibayarkan':tot_dibayarkan.total,'thp':totthp.total,'lembur':lembur.total,'pinjaman':pinjaman.total,'tunjangan_proyek':tpy.total,'tunj_lain':tll.total,'tunj_transport_makan':tmk.total,'employee_id':self.employee_id.id,'id_payslip':self.id})
        # else :
        #     self.env['brt.tb.department.export'].create({'name':kontrak.department_id.name,'department_id':kontrak.department_id.id,'bln':bln,'thn':thn,'date_from':date_from,'date_to':date_to,'company_id':employee.company_id.id})
        #     # self.env['brt.tb.department.export'].create({'name':kontrak.department_id.name,'department_id':kontrak.department_id.id,'bln':bln,'thn':thn,'date_from':date_from,'date_to':date_to})
        #     print ' CONFIRM ALL ============ ======== ======= ============== ======= ============== ======= ======Data  Company ',employee.company_id.id
        #     CEKUlang = self.env['brt.tb.department.export'].search([('date_from', '>=', self.date_from),('date_to', '<=', self.date_to),('department_id', '=', kontrak.department_id.id)])
        #     self.env['brt.tb.payroll.export'].create({'grade':employee.grade ,'date_from':date_from,'date_to':date_to,'gapok':float(gapok.total),'t_jabatan':float(tjb.total),'rapel':self.rapel_amount,'tot_gaji':tot_gaji,'pot_absen':potAbsen.total,'id_department_export':CEKUlang.id,'reimb_medical':self.total_reimburse,'jamsostek':jamsostek,'pph21':float(pph21.total),'bpjs':pot_bpjs,'t_hp':float(th.total),'name':self.employee_id.name,'tot_dibayarkan':float(tot_dibayarkan.total),'thp':float(totthp.total),'lembur':float(lembur.total),'pinjaman':float(pinjaman.total),'tunjangan_proyek':float(tpy.total),'tunj_lain':float(tll.total),'tunj_transport_makan':float(tmk.total),'employee_id':self.employee_id.id,'id_payslip':self.id})

        # self.compute_sheet()
        # return self.write({'state': 'done'})
    # return

   
    @api.multi
    def unlink(self):
        for payslip in self:
            payslip.line_ids.unlink()
            # payslip.unlink()
            # payslip.unlink(cr, uid, payslip.id, context=context)
            print "================ id payslip", payslip.id
            print "================ id employee", payslip.employee_id
            print "================ date_from", payslip.date_from
            print "================ date_to", payslip.date_to
            self.env.cr.execute(""" DELETE FROM hr_payslip WHERE id = %s """, (payslip.id,))
            self.env.cr.execute(""" DELETE FROM brt_tb_payroll_export WHERE id_payslip = '%s' """, (int(payslip.id),))
            self.env.cr.commit()
        return True
        # return super(hr_payslip, self).unlink()

    # @api.multi
    # def delete_select(self):
    #     for payslip in self:
    #         payslip.line_ids.unlink()
    #         # payslip.unlink()
    #         # payslip.unlink(cr, uid, payslip.id, context=context)
    #         print "================ id payslip", payslip.id
    #         print "================ id employee", payslip.employee_id
    #         print "================ date_from", payslip.date_from
    #         print "================ date_to", payslip.date_to
    #         self.env.cr.execute(""" DELETE FROM hr_payslip WHERE id = %s """, (payslip.id,))
    #         self.env.cr.execute(""" DELETE FROM brt_tb_payroll_export WHERE id_payslip = '%s' """, (int(payslip.id),))
    #         self.env.cr.commit()

    #     return True

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            #delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self.get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
        return True

