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


from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import xlwt

class employee_attendance(models.TransientModel):
    _name = 'employee.attendance'

    @api.depends('print_by','start_date')
    def change_print_by_to_end_date(self):
        if self.print_by == 'daily':
            self.end_date = self.start_date
        if self.print_by == 'weekly':
            s_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S").date()
            e_date = s_date + timedelta(days=7)
            self.end_date = e_date
        if self.print_by == 'monthly':
            s_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S").date()
            e_date = s_date + timedelta(days=31)
            self.end_date = e_date
            
    s_date = fields.Date(default=datetime.today().date(),string='Date')
    start_date = fields.Datetime(default=datetime.today(),string='Date')
    end_date = fields.Datetime('End Date',compute='change_print_by_to_end_date')
    print_by = fields.Selection([('daily','Daily'),('weekly','Weekly'),('monthly','Monthly')],'Print By')
    all_employee = fields.Boolean(string="All Employee")
    employee_ids = fields.Many2many('hr.employee',string="Employee")
    attendance_details = fields.Html('Attendance Details',readonly=True )
    attendance_details_duplicate = fields.Html(string='Attendance Details')

    @api.onchange('s_date')
    def chnage_start_date(self):
        self.start_date=self.s_date

    @api.onchange('s_date','start_date','all_employee','employee_ids','print_by')
    def change_employee_attendances(self):
        if self.start_date and self.print_by:
            if self.all_employee or self.employee_ids:
                self.change_start_date_to_attendance()
            else:
                self.attendance_details=''
            

#     @api.onchange('view_details')
    def change_start_date_to_attendance(self):
       details=[]
       res = {}
       all_detail = []
       employee_obj = self.env['hr.employee']
       attandance_obj=self.env['hr.attendance']
       date_range_list = []
       main_header = []
       summary_header_list = [' ']
       if self.start_date:
           d_frm_obj = (datetime.strptime
                        (self.start_date, DEFAULT_SERVER_DATETIME_FORMAT))
           d_to_obj = (datetime.strptime
                       (self.end_date, DEFAULT_SERVER_DATETIME_FORMAT))
           temp_date = d_frm_obj
           while(temp_date <= d_to_obj):
               val = ''
               val = (str(temp_date.strftime("%a")) + ' ' + 
                      str(temp_date.strftime("%b")) + ' ' + 
                      str(temp_date.strftime("%d")))
               summary_header_list.append(val)
               date_range_list.append(temp_date.strftime
                                      (DEFAULT_SERVER_DATETIME_FORMAT))
               temp_date = temp_date + timedelta(days=1)
           summary_header_list.append('Present')
           summary_header_list.append('Absent')
           all_detail.append(summary_header_list)
           employee_ids=''
           if self.employee_ids:
               employee_ids = self.employee_ids
           if self.all_employee:
               employee_ids = employee_obj.search([])
           all_employee_detail = []
           for employee in employee_ids:
               employee_detail = {}
               employee_list_stats = []
               employee_detail.update({'name': employee.name or ''})
               total_present=0
               total_absent=0
               for chk_date in date_range_list:
                        date=''
                        reservline_ids=False
                        attandance_ids=self.env['hr.attendance'].search([])
                        for att in attandance_ids:
                            date=datetime.strptime(att.check_in, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                            if date == chk_date.split(' ')[0]:
                                if att.employee_id.id == employee.id:
                                    reservline_ids=True
                        if not reservline_ids:
                            total_absent+=1
                            employee_list_stats.append({'state':"A" ,
                                                    'date':chk_date,
                                                    'employee_id': employee.id})
                        if reservline_ids:  
                            total_present+=1
                            employee_list_stats.append({'state': "P",
                                                 'date':chk_date,
                                                    'employee_id': employee.id})
               employee_list_stats.append({'present':total_present,'absent':total_absent})
               employee_detail.update({'value': employee_list_stats})
               all_employee_detail.append(employee_detail)
           main_header.append({'header': summary_header_list})
           details.append({'header': summary_header_list, 'data':all_employee_detail})
       body= """<table border="1"><tr>"""
       for each in summary_header_list:
          body+="""
                   <td class="table_header"
                    style="text-align:center;border:1px solid black;">"""+each+"""</td>"""
       body+= """</tr>"""
       for each in details:
           for rec in each.get('data'):
               body+="""<tr>
               <td style="text-align:center;border:1px solid black;">"""+rec['name']+"""</td>"""
               for val in rec['value']:
                   if val.get('state'):
                       for le in val['state']:
                            if val['state'] == 'P':
                                body+= """<td style="text-align:center;border:1px solid black;color: green;">""" + le + """</td>"""
                            if val['state'] == 'A':
                                body+= """<td style="text-align:center;border:1px solid black;color:red;">""" + le + """</td>"""
               
               body+= """<td style="text-align:center;border:1px solid black;">""" + str(val['present']) + """</td>"""
               body+= """<td style="text-align:center;border:1px solid black;">""" + str(val['absent']) + """</td>""" 
                             
               body+="""</tr>"""
       body+="</table>"
       self.attendance_details=body
       self.attendance_details_duplicate=body
       
    @api.multi
    def print_report(self):
        datas = {}
        data = self.read()[0]
        datas = {
                 'ids': [self.id],
                 'model': 'employee.attendance',
                 'form': data
                 }
        return {'type': 'ir.actions.report.xml', 'report_name': 'employee_attendance.employee_attendance_report', 'datas': datas}
    



