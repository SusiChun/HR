# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BrtProductTemplate(models.Model):
    _inherit = "product.template"

    can_be_reimburse = fields.Boolean(string="Can be Reimburse Helath")

    @api.model
    def create(self, vals):
        # When creating an expense product on the fly, you don't expect to
        # have taxes on it
        if vals.get('can_be_expensed', False):
            vals.update({'supplier_taxes_id': False})
        return super(BrtProductTemplate, self).create(vals)