# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class contract_wage(models.Model):
    _inherit = 'hr.contract.wage'

    date_rapel_approve      = fields.Date('Rapel Date')
