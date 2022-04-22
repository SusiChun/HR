# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

class ResBank(models.Model):
    _inherit = 'res.bank'

    is_loan_bank = fields.Boolean(string="Loan Bank")
