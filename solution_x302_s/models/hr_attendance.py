# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
import requests
import re
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    """ Add user id machine in employee """
    _inherit = 'hr.employee'

    x302_s_user_id = fields.Integer('User ID in machine', help="Solution type X302-S User ID.")

class HrAttendance(models.Model):
    """ Cron to read and update attendance in odoo """
    _inherit = 'hr.attendance'

    x302_s_user_id = fields.Integer('User ID in machine', help="Solution type X302-S User ID.")

    def get_data_from_x302_s(self, date, x302_user_id):
        r = requests.session()
        datas = {
            'sdate': date, 'edate': date, 
            'uid': x302_user_id}
        block = []
        try:
            response = r.post('http://192.168.72.195/form/Download', data=datas, stream=True)
            block = response.text.split('\n')
        except:
            pass
        return block

    @api.model
    def syncs_attendance(self):
        today = fields.date.today()
        emp_obj = self.env['hr.employee']
        attendance_obj = self.env['hr.attendance']

        sql_employees = """ select id from hr_employee where x302_s_user_id > 0 """
        self.env.cr.execute(sql_employees)
        result_employees = [emp_obj.browse(x['id']) for x in self.env.cr.dictfetchall()]

        nilai1= (datetime.datetime.strptime(str(today)+ " 00:00:00", '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        nilai2 = str(today) + " 23:59:59"
        regex = re.compile(r'[\n\r\t]') # remove 3 character
        for employee in result_employees:
            block = self.get_data_from_x302_s(date=today, x302_user_id=employee.x302_s_user_id)
            for x in block:
                _logger.info("Isi Block : "+ str(x))
            _logger.info("Employee : "+ str(employee.name))
            _logger.info("Nilai1 : "+ str(nilai1))
            _logger.info("Nilai2 : "+ str(nilai2))
            _logger.info("Today : "+ str(today))

            sql_filter_absen = """ select id from hr_attendance WHERE employee_id = %s AND check_in >= '%s' AND check_in <= '%s' """ % (employee.id,nilai1,nilai2)
            self.env.cr.execute(sql_filter_absen)
            # print sql_filter_absen
            attendance_today = [attendance_obj.browse(x['id']) for x in self.env.cr.dictfetchall()]

            if attendance_today:
                for attendance in attendance_today:
                    # if not attendance.check_out:
                    block = self.get_data_from_x302_s(date=today, x302_user_id=attendance.employee_id.x302_s_user_id)
                    if not len(block) == 0:
                        for b in block[::-1]:
                            row = regex.sub(' ', b)
                            if len(row) != 0:
                                row = row
                                break
                        if len(row) > 10:
                            # if row[-2] == '0' or row[-2] == "1":               
                            final = (datetime.datetime.strptime(row[-24:-6], '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                            if attendance.check_in < final:
                                _logger.info("Update Absen : "+ str(final))
                                attendance.write({
                                    'check_out': final,
                                })                
            else:
                block = self.get_data_from_x302_s(date=today, x302_user_id=employee.x302_s_user_id)
                if not len(block) == 0:
                    for b in block:
                        row = regex.sub(' ', b)
                        break
                    for x in block:
                        _logger.info("Isi Block Untuk Create : "+ str(x))
                    if len(row) > 10:                    
                        # if row[-2] == '0' or row[-2] == "1":
                        final = (datetime.datetime.strptime(row[-24:-6], '%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                        data_absen = {
                            'employee_id': employee.id,
                            'check_in': final,
                        }
                        _logger.info("Membuat Absen Baru ")
                        _logger.info("Data : "+ str(data_absen))
                        self.env['hr.attendance'].create(data_absen)
                elif len(block) == 0:
                    _logger.info("absen kosong ")
                else:
                    _logger.info("gagal membuat absen baru ")


    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        # for attendance in self:
        #     # we take the latest attendance before our check_in time and check it doesn't overlap with ours
        #     last_attendance_before_check_in = self.env['hr.attendance'].search([
        #         ('employee_id', '=', attendance.employee_id.id),
        #         ('check_in', '<=', attendance.check_in),
        #         ('id', '!=', attendance.id),
        #     ], order='check_in desc', limit=1)
        #     if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out >= attendance.check_in:
        #         raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
        #             'empl_name': attendance.employee_id.name_related,
        #             'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
        #         })

            # if not attendance.check_out:
            #     # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
            #     no_check_out_attendances = self.env['hr.attendance'].search([
            #         ('employee_id', '=', attendance.employee_id.id),
            #         ('check_out', '=', False),
            #         ('id', '!=', attendance.id),
            #     ])
            #     if no_check_out_attendances:
            #         raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
            #             'empl_name': attendance.employee_id.name_related,
            #             'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(no_check_out_attendances.check_in))),
            #         })
            # else:
            #     # we verify that the latest attendance with check_in time before our check_out time
            #     # is the same as the one before our check_in time computed before, otherwise it overlaps
            #     last_attendance_before_check_out = self.env['hr.attendance'].search([
            #         ('employee_id', '=', attendance.employee_id.id),
            #         ('check_in', '<=', attendance.check_out),
            #         ('id', '!=', attendance.id),
            #     ], order='check_in desc', limit=1)
            #     if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
            #         raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
            #             'empl_name': attendance.employee_id.name_related,
            #             'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(last_attendance_before_check_out.check_in))),
            #         })
