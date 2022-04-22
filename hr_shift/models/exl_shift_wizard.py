# -*- coding: utf-8 -*-
##############################################################################
#
#    Spellbound soft solution.
#    Copyright (C) 2017-TODAY Spellbound soft solution(<http://www.spellboundss.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import xlwt
import cStringIO
import base64
from decimal import Context
from operator import itemgetter
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class ShiftWizardReport(models.TransientModel):

    _inherit = 'hr.shift.wizard'

    @api.multi
    def print_report_excel(self):
        workbook = xlwt.Workbook()
        title_style1_table_head = xlwt.easyxf('font: name Times New Roman,bold on, italic off, height 200; borders: top double, bottom double, left double, right double;')
        title_style1_table_head_bold = xlwt.easyxf('borders: left medium, right medium, top medium, bottom medium;align: horiz center ;font: name Times New Roman,bold on, italic off,height 200')
        title_style1_table_head_bold_absent = xlwt.easyxf('borders: left medium, right medium, top medium, bottom medium;align: horiz center ;font: name Times New Roman,bold on, italic off,height 200,color red;')
        title_style1_table_head_bold_present = xlwt.easyxf('borders: left medium, right medium, top medium, bottom medium;align: horiz center ;font: name Times New Roman,bold on, italic off,height 200,color green;')
        title_style1_table_head1 = xlwt.easyxf('font: name Times New Roman,bold on, italic off, height 230')
 
        sheet_name = 'Security Shift Report'
        sheet = workbook.add_sheet(sheet_name)
        comp_id = self.env.user.company_id
         
#         if self.location_id:
        if self.print_by == 'daily':
            sheet.write(3,1, 'Security Shift By Daily :' + self.s_date, title_style1_table_head1)
        if self.print_by == 'weekly':
            sheet.write_merge(3, 3,3,8, 'Security Shift By Weekly : '+ self.s_date + ' To ' + self.end_date.split(' ')[0], title_style1_table_head1)
        if self.print_by == 'monthly':
            sheet.write_merge(3, 3,3,8,'Security Shift By Monthly : '+ self.s_date + ' To ' + self.end_date.split(' ')[0], title_style1_table_head1)
        
        details=[]
        res = {}
        all_detail = []
        employee_obj = self.env['hr.employee'].search([('security','=',True)])
        attandance_obj=self.env['hr.attendance']
        date_range_list = []
        main_header = []
        summary_header_list = ['Employee Name']
        if self.start_date:
            d_frm_obj = (datetime.strptime
                         (self.start_date, DEFAULT_SERVER_DATETIME_FORMAT))
            d_to_obj = (datetime.strptime
                        (self.end_date, DEFAULT_SERVER_DATETIME_FORMAT))
            temp_date = d_frm_obj
            while (temp_date <= d_to_obj):
                val = ''
                val = (str(temp_date.strftime("%a")) + ' ' +
                       str(temp_date.strftime("%b")) + ' ' +
                       str(temp_date.strftime("%d")))
                summary_header_list.append(val)
                date_range_list.append(temp_date.strftime
                                       (DEFAULT_SERVER_DATETIME_FORMAT))
                temp_date = temp_date + timedelta(days=1)
            all_detail.append(summary_header_list)
            employee_ids = ''
            if self.employee_ids:
                employee_ids = self.employee_ids
            if self.all_employee:
                employee_ids = employee_obj
            all_employee_detail = []
            for employee in employee_ids:
                employee_detail = {}
                employee_list_stats = []
                employee_detail.update({'name': employee.name or ''})
                total_masuk = 0
                total_libur = 0
                for chk_date in date_range_list:
                    date = ''
                    reservline_ids = False
                    shift_ids = self.env['hr.shift.line'].search([])
                    contract_ids = self.env['hr.contract'].search([
                        ('employee_id', '=', employee.id),
                        ('security_shift_id', '!=', False),
                        ('state', '!=', 'close')
                    ])

                    for sh in shift_ids:
                        datetime1 = datetime.strptime(sh.date, '%Y-%m-%d')
                        date = datetime1.strftime('%Y-%m-%d')
                        if date == chk_date.split(' ')[0]:
                            if contract_ids.security_shift_id.id == sh.shift_id.id:
                                if sh.marks == 'M':
                                    marks = 'M'
                                if sh.marks == 'L':
                                    marks = 'L'
                                reservline_ids = True
                    if reservline_ids:
                        employee_list_stats.append({'state': marks,
                                                    'date': chk_date,
                                                    'employee_id': employee.id})

                employee_detail.update({'value': employee_list_stats})
                all_employee_detail.append(employee_detail)
            main_header.append({'header': summary_header_list})
            details.append({'header': summary_header_list, 'data': all_employee_detail})
        if self.shift_details_duplicate:
            hader=1
            for each in summary_header_list:
                sheet.write(5, hader, each,title_style1_table_head)
                hader+=1
            row_data = 6
            cl_data = 2
            for each in details:
               for rec in each.get('data'):
                   row_data+=1
                   cl_data=2
                   sheet.write(row_data,1,rec['name'],title_style1_table_head_bold)
                   sheet.col(1).width = 7000
                   for val in rec['value']:
                       if val.get('state'):
                           for le in val['state']:
                               if val['state'] == 'M':
                                    sheet.write(row_data,cl_data,le,title_style1_table_head_bold_present)
                               if val['state'] == 'L':
                                    sheet.write(row_data,cl_data,le,title_style1_table_head_bold_absent)
                               cl_data+=1
        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['shift.report.output.wizard'].create({'name':'Security Shift.xls', 'xls_output': base64.encodestring(stream.getvalue())})
        attachment_id = self.env['ir.attachment'].create({
                'name': 'Shifts',
                'datas_fname':'Shifts',
                'type': 'binary',
                'datas': base64.encodestring(stream.getvalue()),
                'res_model': 'hr.shift.wizard',
                'public':True,
            })
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'shift.report.output.wizard',
            'res_id':attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
    
class shiftReportOutputWizard(models.Model):
    _name = 'shift.report.output.wizard'
    _description = 'Wizard to Attendance the Excel output'

    xls_output = fields.Binary(string='Excel Output',readonly=True)
    name = fields.Char(string='File Name', help='Save report as .xls format', default='Employee Attendance.xls')


