# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import timedelta
import time
from odoo.exceptions import UserError, ValidationError

class Shift(models.Model):
    _name = 'hr.shift'
    _description = 'Shift'
    _inherit = ['mail.thread']
    _rec_name = 'rule_shift'

    color = fields.Integer(string='Color Index')
    from_date       = fields.Date(string='From Date', required=True,default=time.strftime('%Y-01-01'))
    to_date         = fields.Date(string='To Date', required=True,default=time.strftime('%Y-12-31'))
    date_ids        = fields.One2many('hr.shift.line', 'shift_id')
    rule_shift      = fields.Selection([('MLLML', 'MLLML'),
                                        ('LLMLM','LLMLM'),
                                        ('LMLML','LMLML'),
                                        ('MLMLL','MLMLL'),
                                        ('LMLLM','LMLLM')], string='Rule Shift')

    @api.constrains('from_date', 'to_date')
    def _check_date(self):
        for att in self:
            domain = [
                ('from_date', '<=', att.to_date),
                ('to_date', '>=', att.from_date),
                ('rule_shift', '=', att.rule_shift),
                ('id', '!=', att.id),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 attendance correction that overlaps on same day!'))

    @api.onchange('from_date', 'to_date')
    def attendance_change(self):
        if self.from_date and self.to_date:
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
                self.date_ids = None
                return None
            for n in range(delta.days + 1):
                data.append((0, 0, {
                    'date': (date_from + timedelta (days=n)),
                }))
            self.date_ids = data

    @api.multi
    def generate_shift(self):
        if self.date_ids and self.rule_shift:
            n = 0
            for line in self.date_ids:
                if n == 0:
                    digit = self.rule_shift[:1]
                elif n == 1:
                    digit = self.rule_shift[1::4]
                elif n == 2:
                    digit = self.rule_shift[2::3]
                elif n == 3:
                    digit = self.rule_shift[3::2]
                elif n == 4:
                    digit = self.rule_shift[4::1]

                print("tanggal", line.date, " n ke-", n, "digit shift-", digit)
                line.write({'marks': digit})

                n = n + 1
                if n == 5:
                    n = 0

                # for x in attendance:
                #     date = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S').date()
                #     datetime1 = datetime.strptime(x.check_in, '%Y-%m-%d %H:%M:%S') + timedelta(hours=7)
                #     datetime2 = datetime.strftime(datetime1, '%Y-%m-%d')
                #     time = datetime.strftime(datetime1, "%H:%M:%S")
                #     jam = '08:30:00'
                #     if check == datetime2:
                #         print (check,"-",date)
                #         line.write({'check_in': x.check_in,
                #                     'check_out': x.check_out,
                #                     'hr_attendance_id': x.id,
                #                     'marks': ' '
                #                     })
                #         if time > jam:
                #             line.write({'marks': 'Telat'})
                # if not line.hr_attendance_id and not line.check_out:
                #     line.write({'marks': 'Alpha'})
                # day = datetime.strptime(line.check_in, '%Y-%m-%d %H:%M:%S').strftime("%A")
                # public_holiday = self.env['hr.holiday.lines'].search(
                #     [('holiday_date', '=', check)
                #      ], limit=1, order='holiday_date desc')
                # if day == 'Saturday' or day == 'Sunday':
                #     line.write({'marks': 'Hari Libur'})
                # if public_holiday:
                #     line.write({'marks': 'Libur Nasional'})
                # if line.check_in:
                #     line.write({'hari': day})
                # cuti = self.env['hr.holidays'].search(
                #     [('start_date', '<=', check),
                #      ('end_date', '>=', check), ('employee_id', '=', line.employee_id.id),
                #      ('state', '=', 'validate'), ('type', '=', 'remove')
                #      ])
                # if cuti:
                #     line.write({'marks': 'Cuti'})

    @api.multi
    def unlink(self):
        for x in self:
            if x.date_ids:
                x.date_ids.unlink()
        return super(Shift, self).unlink()

class ShiftLine(models.Model):
    _name = 'hr.shift.line'
    _description='Shift Line'


    shift_id            = fields.Many2one(comodel_name='hr.shift')
    date                = fields.Date(string='Date',required=True)
    marks               = fields.Char(string='Marks')
    rule_shift          = fields.Selection([('MLLML', 'MLLML'),
                                        ('LLMLM','LLMLM'),
                                        ('LMLML','LMLML'),
                                        ('MLLML','MLLML'),
                                        ('LMLLM','LMLLM')], string='Rule Shift')

