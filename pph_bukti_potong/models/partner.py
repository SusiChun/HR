from odoo import api, fields, models, _

class partner(models.Model):
    _inherit = 'res.partner'

    npwp = fields.Char(string="NPWP", required=False)
