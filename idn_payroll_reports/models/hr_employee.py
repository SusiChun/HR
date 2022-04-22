 # -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError



class HrEmployeeExtended(models.Model):
    _inherit = 'hr.employee'

    is_apply_credit = fields.Boolean(string='Apply Credit ?')
