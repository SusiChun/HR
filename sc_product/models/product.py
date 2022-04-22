from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class Product(models.Model):
    _inherit = 'product.template'



    new_code        = fields.Char(string="New COde")
    golongan        = fields.Selection([('A', 'Golongan A <5%'),('B','Golongan B 5-20%'),('C','Golongan C >20%')],string='Golongan')
    hs_code         = fields.Selection([('Rp 14.000', 'Rp 14.000'),('90% CIF','90% CIF'),('150% CIF','150% CIF')],string='HS Code')


