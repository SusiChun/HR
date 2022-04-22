# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DSDF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DSDTF
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from dateutil import relativedelta
from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
import base64
from cStringIO import StringIO

class RegularCheck(models.Model):
    _name = 'attendance.regular.check'
    _description = 'Approval Check'
    _inherit = ['mail.thread']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(compute="_compute_name")
    company_id      = fields.Many2one(comodel_name='res.company', string='Company',
                        default = lambda self: self.env['res.company']._company_default_get('attendance.regular')
                        )
    employee_id = fields.Many2one(comodel_name='hr.employee', required=True, string='Employee',
                                  default=_default_employee)
    security = fields.Boolean(related='employee_id.job_id.security')
    from_date = fields.Datetime(string='From Date', required=True,default=datetime.utcnow().strftime('%Y-%m-01 00:00:00'))
    to_date = fields.Datetime(string='To Date', required=True,
                              default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1,hours=14,minutes=59,seconds=00)))
    state_select = fields.Selection([('To Submit', 'To Submit'), ('requested', 'Requested'),
                                     ('Confirm Manager', 'Confirm Manager'),
                                     ('Confirm HRD', 'Confirm HRD')
                                     ], default='To Submit', track_visibility='onchange', string='State', copy=False)
    attendance_ids = fields.One2many('attendance.correction.check', 'atten_id')
    overtime_total = fields.Float(string='OT Total', compute='compute_ot_total', store=True)
    grade = fields.Selection([('1', '1'),
                              ('2', '2'),
                              ('3', '3'),
                              ('4', '4'),
                              ('5', '5'),
                              ('6', '6'),
                              ('7', '7'),
                              ('8', '8')], related='employee_id.grade', string='Grade')
    min_hour_overtime = fields.Float(string='Min Hour Overtime')
    basic_salary = fields.Float(string='Basic Salary', compute='compute_salary')

    @api.depends('employee_id', 'from_date', 'to_date')
    @api.multi
    def _compute_name(self):
        for x in self:
            if x.employee_id and x.from_date and x.to_date:
                x.name = "%s/%s/%s" % (x.employee_id.name, x.from_date, x.to_date)

    @api.multi
    @api.depends('employee_id')
    def compute_salary(self):
        for x in self:
            kontrak = self.env['hr.contract'].search(
                [('employee_id', '=', x.employee_id.id),
                 ('state', '=', 'pending'),
                 ], limit=1)
            if kontrak:
                x.basic_salary = kontrak.wage

    @api.multi
    @api.depends('attendance_ids.meal_allowance', 'attendance_ids.overtime_amount')
    def compute_ot_total(self):
        for record in self:
            meal_allow = sum(line.meal_allowance for line in record.attendance_ids)
            ot_amount = sum(line.overtime_amount for line in record.attendance_ids)
            record.overtime_total = ot_amount + meal_allow

    @api.multi
    def unlink(self):
        for x in self:
            if x.attendance_ids:
                x.attendance_ids.unlink()
        return super(RegularCheck, self).unlink()

    @api.onchange('employee_id')
    def compute_salary(self):
        for x in self:
            kontrak = self.env['hr.contract'].search(
                [('employee_id', '=', x.employee_id.id),
                 ('state', '=', 'pending'),
                 ], limit=1)
            if kontrak:
                x.basic_salary = kontrak.wage

    @api.onchange('employee_id', 'from_date', 'to_date')
    def attendance_change(self):
        if self.employee_id and self.from_date and self.to_date:
            if self.employee_id.grade == '1' or self.employee_id.grade == '2':
                self.min_hour_overtime = 17.30
            elif self.employee_id.grade == '3':
                self.min_hour_overtime = 19.00
            elif self.employee_id.grade == '4' or self.employee_id.grade == '5':
                self.min_hour_overtime = 21.00
            else:
                self.min_hour_overtime = 0.0
            data = []
            # date_from1 = datetime.strptime(self.from_date, '%Y-%m-%d %H:%M:%S').date()
            # print (date_from1,'date_from1')
            # tgl = datetime.strftime(date_from1, '%Y-%m-%d')
            # print (tgl, 'tgl')
            # time = '00:00:00'
            # date_check_form= tgl +time
            # print(date_check_form, 'date_check_form')

            date_from = fields.Date.from_string(self.from_date)
            date_to = fields.Date.from_string(self.to_date)
            delta = date_to - date_from
            if delta.days < 0:
                self.attendance_ids = None
                return None
            for n in range(delta.days + 1):
                data.append((0, 0, {
                    'employee_id': self.employee_id.id,
                    'date_check': (date_from + timedelta(days=n)),
                    'check_in': (date_from + timedelta(days=n)),
                    'state': self.state_select,
                }))
            self.attendance_ids = data

    @api.multi
    def generate_attendance(self):
        attendance = self.env['hr.attendance'].search(
            [('check_in', '>=', self.from_date),
             ('check_in', '<=', self.to_date), ('employee_id', '=', self.employee_id.id),
             ])
        if self.employee_id.grade == '1' or self.employee_id.grade == '2':
            self.min_hour_overtime = 17.30
        elif self.employee_id.grade == '3':
            self.min_hour_overtime = 19.00
        elif self.employee_id.grade == '4' or self.employee_id.grade == '5':
            self.min_hour_overtime = 21.00
        else:
            self.min_hour_overtime = 0.0
            # attendance = self.env['hr.attendance'].search(
            #     [('check_in', '>=', self.from_date),
            #      ('check_out', '<=', self.to_date), ('employee_id', '=', self.employee_id.id),
            #      ])
        if self.attendance_ids:
            for line in self.attendance_ids:
                if line.check_in:
                    check1 = datetime.strptime(line.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                else:
                    raise UserError('Data already checked, please re-select the "From Date"')
                check = datetime.strftime(check1, '%Y-%m-%d')
                for x in attendance:
                    date = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S').date()
                    datetime1 = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                    datetime2 = datetime.strftime(datetime1, '%Y-%m-%d')
                    time = datetime.strftime(datetime1, "%H:%M:%S")
                    jam = '08:30:00'
                    if check == datetime2:
                        line.write({'check_in': x.check_in,
                                    'check_out': x.check_out,
                                    'hr_attendance_id': x.id,
                                    'marks': ' ',
                                    'reg_reason': x.note,
                                    })
                        if time > jam:
                            line.write({'marks': 'Telat'})
                if not line.hr_attendance_id and not line.check_out:
                    line.write({'marks': 'Alpha'})
                day = datetime.strptime(line.check_in, '%Y-%m-%d %H:%M:%S').strftime("%A")
                public_holiday = self.env['hr.holiday.lines'].search(
                    [('holiday_date', '=', check)
                     ], limit=1, order='holiday_date desc')
                if day == 'Saturday' or day == 'Sunday':
                    line.write({'marks': 'Hari Libur'})
                if public_holiday:
                    line.write({'marks': 'Libur Nasional'})
                if line.check_in:
                    line.write({'hari': day})
                cuti = self.env['hr.holidays'].search(
                    [('start_date', '<=', check),
                     ('end_date', '>=', check), ('employee_id', '=', line.employee_id.id),
                     ('state', '=', 'validate'), ('type', '=', 'remove')
                     ])
                if cuti:
                    line.write({'marks': 'Cuti'})
                
                for att in self.attendance_ids:
                    if att.marks in ["Alpha", "Hari Libur", "Libur Nasional"]:
                        att.write({
                            "check_in" : False,
                        })


    @api.multi
    def generate_excel(self):
        file_name = _('RecapReport.xlsx')
        fp = BytesIO()

        workbook = xlsxwriter.Workbook(fp)
        heading_format = workbook.add_format({'align': 'left',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 14})
        heading_format_2 = workbook.add_format({'align': 'left',
                                              'valign': 'vcenter',
                                              'bold': False, 'size': 9})
        cell_text_format_n = workbook.add_format({'align': 'center',
                                                  'bold': True, 'size': 9,
                                                  })
        cell_text_format_h = workbook.add_format({'align': 'center',
                                                  'bold': True, 'size': 9,
                                                  })
        cell_text_format_n.set_border()
        cell_text_format = workbook.add_format({'align': 'center',
                                                'bold': True, 'size': 9,
                                                })

        cell_text_format.set_border()
        cell_text_format_new = workbook.add_format({'align': 'center',
                                                    'size': 9,
                                                    })
        cell_text_format_new.set_border()
        cell_text_format_new_h = workbook.add_format({'align': 'center',
                                                    'size': 9,
                                                    })
        cell_number_format = workbook.add_format({'align': 'right',
                                                  'bold': False, 'size': 9,
                                                  'num_format': '#,###0.00'})
        cell_number_format.set_border()
        worksheet = workbook.add_worksheet('RecapReport')
        normal_num_bold = workbook.add_format({'bold': True, 'num_format': '#,###0.00', 'size': 9, })
        normal_num_bold.set_border()
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)

        if self.from_date and self.to_date:

            date_2 = datetime.strptime(self.to_date, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
            date_1 = datetime.strptime(self.from_date, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')

            # worksheet.merge_range('A1:F1', 'Metrocom Global Solusi', heading_format)
            # worksheet.merge_range('A2:F2', 'JL LETJEN HARYONO MT. KAV. 8', heading_format_2)
            # worksheet.merge_range('A3:F3', 'JAKARTA, Postal Code : 13340', heading_format_2)
            # worksheet.merge_range('A4:F4', 'Phone : 021-8193708, Fax : 021-8196107 ', heading_format_2)
            # worksheet.merge_range('B4:D4', '%s' % (self.company.name), cell_text_format_n)
            row = 0
            column = 0
            worksheet.merge_range('A1:F1', 'Laporan Kehadiran Karyawan per Periode', heading_format)
            row += 1
            if self.employee_id:
                employee = self.employee_id
            else: 
                raise UserError("Employee not set, please select one")
            worksheet.write(row, column, 'Nama Karyawan', cell_text_format_h)
            worksheet.write(row + 1, column, 'NIK', cell_text_format_h)
            worksheet.write(row + 2, column, 'Grade', cell_text_format_h)

            worksheet.write(row, column + 1, employee.name, cell_text_format_new_h)
            worksheet.write(row + 1, column + 1, employee.nik, cell_text_format_new_h)
            worksheet.write(row + 2, column + 1, employee.grade, cell_text_format_new_h)
            column += 3
            worksheet.write(row, column, 'Department', cell_text_format_h)
            worksheet.write(row + 1, column, 'Job Level', cell_text_format_h)
            worksheet.write(row + 2, column, 'Jabatan', cell_text_format_h)

            worksheet.write(row, column + 1, employee.department_id.name, cell_text_format_new_h)
            worksheet.write(row + 1, column + 1, employee.job_level_id.name, cell_text_format_new_h)
            worksheet.write(row + 2, column + 1, employee.job_id.name, cell_text_format_new_h)
            row += 4

            worksheet.write(row, 0, 'PERIODE', cell_text_format_h)
            worksheet.write(row, 1, date_1 + ' to ' + date_2, cell_text_format_new_h)

            row += 2

            worksheet.merge_range('A8:A9', 'Day', cell_text_format_n)
            worksheet.merge_range('B8:B9', 'Check In', cell_text_format_n)
            worksheet.merge_range('C8:C9', 'Check Out', cell_text_format_n)
            worksheet.merge_range('D8:D9', 'Marks', cell_text_format_n)
            worksheet.merge_range('E8:E9', 'Reason', cell_text_format_n)
            
            row_set = row
            column = 2
            row += 2
            col = 0
            ro = row

            res = []
            docs = []
            # employees = self.env['hr.attendance'].search([('create_date', '>=' , self.from_date),('create_date', '<=' , self.date_end), ('employee_id.id', '=', self.employee_id.id)], order='employee_id asc')
            if self.attendance_ids:
                for attend in self.attendance_ids:
                    hari = attend.hari
                    check_in = attend.check_in
                    check_out = attend.check_out
                    marks = attend.marks
                    reason = attend.reg_reason

                    res.append({
                        'hari': hari,
                        'check_in': check_in,
                        'check_out': check_out,
                        'marks': marks,
                        'reason': reason,
                    })

                for emp in res:
                    hari = emp['hari']
                    check_in = emp['check_in']
                    check_out = emp['check_out']
                    marks = emp['marks']
                    reason = emp['reason']

                    worksheet.write(ro, col, hari or '', cell_text_format_new)
                    worksheet.write(ro, col + 1, check_in or '', cell_text_format_new)
                    worksheet.write(ro, col + 2, check_out or '', cell_text_format_new)
                    worksheet.write(ro, col + 3, marks, cell_text_format_new)
                    worksheet.write(ro, col + 4, reason if reason else '', cell_text_format_new)
                    ro = ro + 1
        roww = row
        columnn = 2

        workbook.close()
        file_download = base64.b64encode(fp.getvalue())
        fp.close()
        self = self.with_context(default_name=file_name, default_file_download=file_download)

        excel_export_summary_id = self.env['report.excel'].create({'name': file_name, 'file_download': file_download})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': excel_export_summary_id.id,
            'res_model': 'report.excel',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class ReportExcel(models.TransientModel):
    _name = 'report.excel'

    name = fields.Char('File Name', size=256)
    file_download = fields.Binary('Download Report')
