# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
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


class ComputConfirmPayslipWiz(models.TransientModel):

    _name = 'comput.confirm.payslip.wiz'

    @api.model
    def default_get(self, fields_list):
        res = super(ComputConfirmPayslipWiz, self).default_get(fields_list)
        cr , uid , context = self.env.args
        if 'emp_net_amt_info' in res:
            res['emp_net_amt_info'] = False
        payslip_obj = self.env['hr.payslip']
        payslip_ids = context.get('active_ids')
        user_data = self.env['res.users'].browse(uid)
        lang_ids = self.env['res.lang'].search([('code', '=', user_data.lang)])
        net_amount = 0.0
        for payslip in payslip_obj.browse(payslip_ids):
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_amount += line.amount
        if lang_ids and lang_ids.ids:
            net_amount = lang_ids.format("%.2f", net_amount, True)
        foramte_string = "Total Amount Before Compute is %s" % net_amount
        for payslip in payslip_obj.browse(payslip_ids):
            payslip.compute_sheet()
        net_amount = 0.0
        for payslip in payslip_obj.browse(payslip_ids):
            for line in payslip.line_ids:
                if line.code == 'NET':
                    net_amount += line.amount
        if lang_ids and lang_ids.ids:
            net_amount = lang_ids.format("%.2f", net_amount, True)
        foramte_string += "\nTotal Amount After Compute is %s" % net_amount
        res['name'] = foramte_string
        return res

    @api.multi
    def confirm_selected_payslip(self):
        cr, uid, context = self.env.args
        if context is None:
            context = {}
        if not context.get('active_ids'):
            return {}
        payslip_ids = context.get('active_ids')
        for payslip in self.env['hr.payslip'].browse(payslip_ids):

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
            payslip.write({'state': 'done'})
        return {}

    name = fields.Text('Employee Net Amount Information', readonly=True)
