# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class attendance_summary(models.TransientModel):
    _name = 'attendance.summary'


    start_date          = fields.Date(default=datetime.today(), string='Start Date')
    end_date            = fields.Date('End Date',default=(datetime.today() + relativedelta(days=30)))
    employee_ids        = fields.Many2many('hr.employee',string="Employee")


    def _get_day(self):
        res = []
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)
        delta = end_date - start_date
        for x in range(delta.days + 1):
            color = '#ababab' if start_date.strftime('%a') == 'Sat' or start_date.strftime('%a') == 'Sun' else ''
            res.append({'day_str': start_date.strftime('%a'), 'day': start_date.day, 'color': color})
            start_date = start_date + relativedelta(days=1)
        return res
        # date_from = fields.Date.from_string(self.start_date)
        # date_to = fields.Date.from_string(self.end_date)
        # delta = date_to - date_from
        # print ("hahahahhahaha",delta)
        # # month_days = delta.days + 1
        # for n in range(delta.days + 1):
        #     res.append({'day_str': date_from.strftime('%a'), 'day': date_from.day})
        #     print("res",res)
        # return res


    def _get_months(self):
        # it works for geting month name between two dates.
        # res = []
        # date_from = fields.Date.from_string(self.start_date)
        # date_to = fields.Date.from_string(self.end_date)
        # delta = date_to - date_from
        # month_days = delta.days + 1
        # for n in range(delta.days + 1):
        #     res.append({'month_name': date_from.strftime('%B'), 'days': month_days})
        # return res

        res = []
        start_date = fields.Date.from_string(self.start_date)
        end_date = fields.Date.from_string(self.end_date)
        while start_date <= end_date:
            last_date = start_date + relativedelta(day=1, months=+1, days=-1)
            if last_date > end_date:
                last_date = end_date
            month_days = (last_date - start_date).days + 1
            res.append({'month_name': start_date.strftime('%B'), 'days': month_days})
            start_date += relativedelta(day=1, months=+1)
        return res

    # def _get_leaves_summary(self, start_date, empid, holiday_type):
    #     res = []
    #     count = 0
    #     start_date = fields.Date.from_string(start_date)
    #     end_date = start_date + relativedelta(days=59)
    #     for index in range(0, 60):
    #         current = start_date + timedelta(index)
    #         res.append({'day': current.day, 'color': ''})
    #         if current.strftime('%a') == 'Sat' or current.strftime('%a') == 'Sun':
    #             res[index]['color'] = '#ababab'
    #     # count and get leave summary details.
    #     # holiday_type = ['confirm','validate'] if holiday_type == 'both' else ['confirm'] if holiday_type == 'Confirmed' else ['validate']
    #     line = self.env['hr.holidays'].search([
    #         ('employee_id', '=', empid), ('state', 'in', holiday_type),
    #         ('type', '=', 'remove'), ('date_from', '<=', str(end_date)),
    #         ('date_to', '>=', str(start_date))
    #     ])
    #     for holiday in holidays:
    #         # Convert date to user timezone, otherwise the report will not be consistent with the
    #         # value displayed in the interface.
    #         date_from = fields.Datetime.from_string(holiday.date_from)
    #         date_from = fields.Datetime.context_timestamp(holiday, date_from).date()
    #         date_to = fields.Datetime.from_string(holiday.date_to)
    #         date_to = fields.Datetime.context_timestamp(holiday, date_to).date()
    #         for index in range(0, ((date_to - date_from).days + 1)):
    #             if date_from >= start_date and date_from <= end_date:
    #                 res[(date_from-start_date).days]['color'] = holiday.holiday_status_id.color_name
    #             date_from += timedelta(1)
    #         count += abs(holiday.number_of_days)
    #     self.sum = count
    #     return res

    # def _get_data_from_report(self):
    #     res = []
    #     Employee = self.env['hr.employee']
    #     # if 'depts' in data:
    #     #for department in self.env['hr.department'].browse(data['depts']):
    #     # res.append({'dept': department.name, 'data': [], 'color': self._get_day(data['date_from'])})
    #     # for emp in Employee.search([('department_id', '=', department.id)]):
    #     #     res[len(res) - 1]['data'].append({
    #     #         'emp': emp.name,
    #     #         'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
    #     #         'sum': self.sum
    #     #     })
    #     # elif 'emp' in data:
    #     res.append({'data': []})
    #     for emp in Employee:
    #         res.append({
    #             'emp': emp.name,
    #             # 'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
    #             # 'sum': self.sum
    #         })
    #         print (res,"dataaaaaaaaaaaaaaaaaaaa")
    #     return res
        # res = []
        # Employee = self.env['hr.employee']
        # if 'depts' in data:
        #     for department in self.env['hr.department'].browse(data['depts']):
        #         res.append({'dept': department.name, 'data': [], 'color': self._get_day(data['date_from'])})
        #         for emp in Employee.search([('department_id', '=', department.id)]):
        #             res[len(res) - 1]['data'].append({
        #                 'emp': emp.name,
        #                 'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
        #                 'sum': self.sum
        #             })
        # elif 'emp' in data:
        #     res.append({'data': []})
        #     for emp in Employee.browse(data['emp']):
        #         res[0]['data'].append({
        #             'emp': emp.name,
        #             'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
        #             'sum': self.sum
        #         })
        # return res

    @api.multi
    def get_employee(self):
        list_data = []
        where_employee = " 1=1 "
        if self.employee_ids:
            where_employee = "emp.id in %s " % str(tuple(self.employee_ids)).replace(',)', ')')

        query = """ 
                select 
                 emp.nik,
                 emp.name_related
                
                from hr_employee emp
                where """ + where_employee + """ 
                  order by emp.name_related asc 
                        
                         """
        self._cr.execute(query)
        ress = self._cr.fetchall()

        for res in ress:
            list_data.append({
                'nik': res[0],
                'name': res[1],

            })

        return list_data

    def _get_attendance(self, start_date, empid):
        res = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(self.end_date)
        delta = end_date - start_date
        for index in range(delta.days + 1):
            current = start_date + timedelta(index)
            res.append({'day': current.day, 'color': ''})
            if current.strftime('%a') == 'Sat' or current.strftime('%a') == 'Sun':
                res[index]['color'] = '#ababab'
        # count and get leave summary details.
        # holiday_type = ['confirm','validate'] if holiday_type == 'both' else ['confirm'] if holiday_type == 'Confirmed' else ['validate']
        # holidays = self.env['hr.holidays'].search([
        #     ('employee_id', '=', empid), ('state', 'in', holiday_type),
        #     ('type', '=', 'remove'), ('date_from', '<=', str(end_date)),
        #     ('date_to', '>=', str(start_date))
        # ])
        attendance = self.env['attendance.correction.line'].search([
            ('employee_id', '=', empid), ('check_in', '<=', str(end_date)),
            ('check_in', '>=', str(start_date))
        ])
        print ('att-----------',attendance)
        for x in attendance:
            # Convert date to user timezone, otherwise the report will not be consistent with the
            # value displayed in the interface.
            date_from = fields.Datetime.from_string(x.check_in)
            date_from = fields.Datetime.context_timestamp(x, date_from).date()
            date_to = fields.Datetime.from_string(x.check_in)
            date_to = fields.Datetime.context_timestamp(x, date_to).date()
            print('wkwkwkwkwkwkwkwk')
            for index in range(0, ((date_to - date_from).days + 1)):

                if date_from >= start_date and date_from <= end_date:
                    res[(date_from-start_date).days]['marks'] = x.marks
                date_from += timedelta(1)
        return res

    # @api.multi
    # def get_data(self, tgl, emp):
    #     list_data = []
    #     where_employee = " 1=1 "
    #     if self.employee_ids:
    #         where_employee = "emp.id in %s " % str(tuple(self.employee_ids)).replace(',)', ')')
    #
    #     query = """
    #               select
    #                emp.name_related,
    #                to_char(att.check_in,'Dd') as tgl,
    #                 to_char(att.check_in,'Mon') as Mon,
    #                CASE WHEN att.marks='Alpha' and att.check_in_correction is NULL THEN 'A'
    #                         WHEN att.marks='Cuti' THEN 'L'
    #                         WHEN att.marks='Libur Nasional' THEN 'PH'
    #                         WHEN att.marks='Telat' THEN 'P'
    #                         WHEN att.marks=' ' and att.check_out is NOT NULL THEN 'P'
    #                         WHEN att.marks=' ' and att.check_in_correction is not NULL THEN 'P'
    #                 END as Kehadiran
    #
    #        from attendance_correction_line att
    #            left join attendance_regular reg on att.atten_id = reg.id
    #            left join hr_employee emp on reg.employee_id = emp.id
    #            where """+where_employee+""" and to_char(att.check_in,'dd') = '""" + tgl + """'
    #             and emp.name_related = '""" + emp + """'
    #             group by emp.name_related,tgl,mon,kehadiran
	# 			order by name_related,tgl,mon asc
    #        """
    #
    #     self._cr.execute(query)
    #     data = self._cr.fetchall()
    #     for res in data:
    #         list_data.append({
    #             'hadir': res[3],
    #         })
    #     return list_data

    def _get_data_from_report(self, data):
        res = []
        Employee = self.env['hr.employee']
        # if 'depts' in data:
        #     for department in self.env['hr.department'].browse(data['depts']):
        #         res.append({'dept': department.name, 'data': [], 'color': self._get_day(data['date_from'])})
        #         for emp in Employee.search([('department_id', '=', department.id)]):
        #             res[len(res) - 1]['data'].append({
        #                 'emp': emp.name,
        #                 'display': self._get_leaves_summary(data['date_from'], emp.id, data['holiday_type']),
        #                 'sum': self.sum
        #             })
        # elif 'emp' in data:
        res.append({'data': []})
        for emp in Employee.browse(data['emp']):
            res[0]['data'].append({
                'emp': emp.name_related,
                'display': self._get_attendance(data['date_from'], emp.id, data['marks']),
            })
        return res

    @api.multi
    def print_report(self):
        return self.env['report'].get_action(self, 'attendance_summary.report_attendance_summary')