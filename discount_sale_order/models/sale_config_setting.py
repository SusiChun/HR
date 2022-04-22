# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_order_global_discount = fields.Boolean("A global discount on sales order",
        implied_group='discount_sale_order.group_order_global_discount',
        help="""Allows to give a global discount on sales order. """)
    global_discount_tax = fields.Selection([
        ('untax', 'Untaxed amount'),
        ('taxed', 'Tax added amount'),
        ], "Global Discount Calculation",
        help="Global disount calculation will be ( \
                'untax' : Global discount will be applied before applying tax, \
                'taxed : Global disount will be applied after applying tax)")
    discount_account_so = fields.Many2one(
        'account.account',
        string="Discount Account",
        help="""Account for Global discount on sales order.""")

    @api.multi
    def set_default_fields(self):
        ir_values_obj = self.env['ir.values']
        ir_values_obj.sudo().set_default('sale.config.settings', 'global_discount_tax', self.global_discount_tax or 0)
        ir_values_obj.sudo().set_default('sale.config.settings', 'discount_account_so', self.discount_account_so.id or 0)

    @api.model
    def get_default_fields(self, fields):
        ir_values_obj = self.env['ir.values']
        global_discount_tax = ir_values_obj.sudo().get_default('sale.config.settings', 'global_discount_tax')
        discount_account_so = ir_values_obj.sudo().get_default('sale.config.settings', 'discount_account_so')

        return {
            'global_discount_tax': global_discount_tax,
            'discount_account_so': discount_account_so,
        }
