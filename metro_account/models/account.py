# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    tgl_inv = fields.Date(string='Invoice Date', readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False, default=lambda self: fields.datetime.now())
    date_invoice = fields.Date(string='Received Date')
