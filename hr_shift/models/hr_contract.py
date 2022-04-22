# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
import time


class Job(models.Model):
    _inherit = 'hr.job'


    security = fields.Boolean(string='is Security?')

class Employee(models.Model):
    _inherit = 'hr.employee'

    security = fields.Boolean(string='is Security?',compute='_compute_security',store=True)


    @api.multi
    @api.depends('job_id.security')
    def _compute_security(self):
        for x in self:
            if x.job_id:
                x.security = x.job_id.security

class Contract(models.Model):
    _inherit = 'hr.contract'

    security_shift_id            = fields.Many2one(comodel_name='hr.shift', string='Security Shift')

