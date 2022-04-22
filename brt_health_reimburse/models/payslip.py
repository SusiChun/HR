# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class brt_hr_payslip(models.Model):
    _inherit= 'hr.payslip'

    # employee_id 	= fields.Many2one('hr.employee', compute='compute_reimburse', string='Employee', required=True)
    total_reimburse = fields.Float('Total Reimburse', compute='compute_reimburse', store=True)

    @api.multi
    @api.depends('contract_id', 'date_from', 'date_to')
    def compute_reimburse(self):
 		total_reimburse = 0
 		for x in self:
 			total_reimburse = 0
        	attends = x.env[('brt_health.reimburse')].search([('employee_id', '=', x.employee_id.id), ('date', '>', x.date_from), ('date', '<', x.date_to), ('state', '=', 'done')])
        	print '=============================', attends
         	for y in attends:
         		print 'ARRAY =============================', y.total_amount
         		total_reimburse += y.total_amount
        	print '=============================', x.total_reimburse
         	x.total_reimburse = total_reimburse
