# -*- coding:utf-8 -*-

from odoo import models, fields


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    date_start = fields.Date('Date From')
    date_end = fields.Date('Date To')
