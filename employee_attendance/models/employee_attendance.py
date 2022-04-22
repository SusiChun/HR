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

from openerp import tools
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import xlwt


class employee_attendance(models.TransientModel):
    _name = 'employee.attendance'

    @api.depends('print_by', 'start_date')
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

    s_date = fields.Date(default=datetime.today().date(), string='Date')
    start_date = fields.Datetime(default=datetime.today(), string='Date')
    end_date = fields.Datetime('End Date', compute='change_print_by_to_end_date')
    print_by = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], 'Print By')
    all_employee = fields.Boolean(string="All Employee")
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    attendance_details = fields.Html('Attendance Details', readonly=True)
    attendance_details_duplicate = fields.Html(string='Attendance Details')

    @api.onchange('s_date')
    def change_start_date(self):
        self.start_date = self.s_date

    @api.onchange('s_date', 'start_date', 'all_employee', 'employee_ids', 'print_by')
    def change_employee_attendances(self):
        if self.start_date and self.print_by:
            if self.all_employee or self.employee_ids:
                self.change_start_date_to_attendance()
            else:
                self.attendance_details = ''

    #     @api.onchange('view_details')
    def change_start_date_to_attendance(self):
        details = []
        res = {}
        all_detail = []
        employee_obj = self.env['hr.employee']
        attandance_obj = self.env['hr.attendance']
        leave_obj = self.env['hr.holidays']
        date_range_list = []
        main_header = []
        summary_header_list = [' ']
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
            summary_header_list.append('Present')
            summary_header_list.append('Absent')
            summary_header_list.append('Leave')
            summary_header_list.append('Public Holiday')
            summary_header_list.append('OT Amount    ')
            all_detail.append(summary_header_list)
            employee_ids = ''
            if self.employee_ids:
                employee_ids = self.employee_ids
            if self.all_employee:
                employee_ids = employee_obj.search([])
            all_employee_detail = []
            for employee in employee_ids:
                employee_detail = {}
                employee_list_stats = []
                employee_detail.update({'name': employee.name or ''})
                total_present = 0
                total_ph = 0
                total_absent = 0
                total_leave = 0
                ot_amount = 0.0

                for chk_date in date_range_list:
                    day_name = datetime.strptime(chk_date, '%Y-%m-%d %H:%M:%S')
                    hari = (day_name.strftime("%A"))
                    date = ''
                    reservline_ids = False
                    ph = False

                    attandance_ids = self.env['hr.attendance'].search([])
                    holiday_ids = self.env['hr.holidays'].search([('type', '=', 'remove'),
                                                                  ('state', '=', 'validate'),
                                                                  ('start_date', '<=', chk_date.split(' ')[0]),
                                                                  ('end_date', '>=', chk_date.split(' ')[0]),
                                                                  ('employee_id', '=', employee.id),

                                                                  ])
                    public_holiday = self.env['hr.holiday.lines'].search(
                        [('holiday_date', '=', chk_date.split(' ')[0])
                         ], limit=1, order='holiday_date desc')
                    cek_holiday = False
                    for att in attandance_ids:
                        datetime1 = datetime.strptime(att.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                        date = datetime1.strftime('%Y-%m-%d')
                        if date == chk_date.split(' ')[0]:
                            if att.employee_id.id == employee.id:
                                reservline_ids = True
                                cek_holiday = False
                                ph = False

                    if holiday_ids:
                        no = int(holiday_ids.number_of_days_temp)
                        for n in range(no):
                            reservline_ids = True
                            cek_holiday = True
                            ph = False
                    if public_holiday:
                        ph = True

                    if ph == True:
                        total_ph += 1
                        employee_list_stats.append({'state': "H",
                                                    'date': chk_date,
                                                    'employee_id': employee.id})

                    if reservline_ids == True and cek_holiday == True:
                        total_leave += 1
                        employee_list_stats.append({'state': "L",
                                                    'date': chk_date,
                                                    'employee_id': employee.id})

                    if reservline_ids and not cek_holiday:
                        total_present += 1
                        employee_list_stats.append({'state': "P",
                                                    'date': chk_date,
                                                    'employee_id': employee.id})

                    if not reservline_ids and not cek_holiday and not public_holiday:
                        if hari == 'Saturday' or hari == 'Sunday':
                            print("kklkslalsklakslkl")
                            print(hari)
                            employee_list_stats.append({'state': "-",
                                                        'date': chk_date,
                                                        'employee_id': employee.id})
                        else:
                            print ("hshshhs")
                            print(hari)
                            total_absent += 1
                            employee_list_stats.append({'state': "A",
                                                        'date': chk_date,
                                                        'employee_id': employee.id})

                    correction_ids = self.env['attendance.correction.line'].search([
                        ('employee_id', '=', employee.id)
                    ])

                    ot_total = 0.0
                    if correction_ids:
                        for x in correction_ids:
                            datetime1 = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                            date = datetime1.strftime('%Y-%m-%d')
                            if date == chk_date.split(' ')[0]:
                                jumlah = (x.overtime_amount + x.meal_allowance)
                                ot_amount += jumlah
                            ot_total1 = tools.ustr('{0:,.0f}'.format(int(ot_amount)))
                            ot_totala = 'Rp. ' + ot_total1
                            ot_total = ot_totala.replace("'", " ", 2)
                            # ot_total = "%.2f" % (ot_amount)

                employee_list_stats.append(
                    {'present': total_present, 'absent': total_absent, 'leave': total_leave, 'public_holiday': total_ph,'amount': ot_total})
                employee_detail.update({'value': employee_list_stats})
                all_employee_detail.append(employee_detail)
            main_header.append({'header': summary_header_list})
            details.append({'header': summary_header_list, 'data': all_employee_detail})
        body = """<table border="1"><tr>"""
        for each in summary_header_list:
            if each[:3] =='Sat' or each[:3] =='Sun':
                body += """
                       <td class="table_header"
                        style="text-align:center;border:1px solid black;background-color:#ababab;color:white;">""" + each + """</td>"""
            else:
                body += """
                        <td class="table_header"
                                        style="text-align:center;border:1px solid black;">""" + each + """</td>"""
        body += """</tr>"""
        for each in details:
            for rec in each.get('data'):
                body += """<tr>
               <td style="text-align:center;border:1px solid black;">""" + rec['name'] + """</td>"""
                for val in rec['value']:
                    if val.get('state'):
                        for le in val['state']:
                            if val['state'] == 'P':
                                body += """<td style="text-align:center;border:1px solid black;color: green;">""" + le + """</td>"""
                            if val['state'] == 'A':
                                body += """<td style="text-align:center;border:1px solid black;color:red;">""" + le + """</td>"""
                            if val['state'] == 'L':
                                body += """<td style="text-align:center;border:1px solid black;color: blue;">""" + le + """</td>"""
                            if val['state'] == 'H':
                                body += """<td style="text-align:center;border:1px solid black;color: blue;">""" + le + """</td>"""
                            if val['state'] == '-':
                                body += """<td style="text-align:center;border:1px solid black;color: red;">""" + le + """</td>"""


                body += """<td style="text-align:center;border:1px solid black;">""" + str(val['present']) + """</td>"""
                body += """<td style="text-align:center;border:1px solid black;">""" + str(val['absent']) + """</td>"""
                body += """<td style="text-align:center;border:1px solid black;">""" + str(val['leave']) + """</td>"""
                body += """<td style="text-align:center;border:1px solid black;">""" + str(val['public_holiday']) + """</td>"""
                body += """<td style="text-align:center;border:1px solid black;">""" + str(val['amount']) + """</td>"""

                body += """</tr>"""
        body += "</table>"
        self.attendance_details = body
        self.attendance_details_duplicate = body

    @api.multi
    def print_report(self):
        datas = {}
        data = self.read()[0]
        datas = {
            'ids': [self.id],
            'model': 'employee.attendance',
            'form': data
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'employee_attendance.employee_attendance_report',
                'datas': datas}




