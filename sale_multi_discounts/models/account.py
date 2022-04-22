# -*- coding: utf-8 -*-

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _total_discount(self):
        for rec in self:
            discount_amount = 0
            for line in rec.invoice_line_ids:
                discount_amount += line.discount_amount
            rec.discount_amount = discount_amount
            print (rec.discount_amount,"rec.discount_amount = discount_amount")
            rec.avg_discount = (discount_amount*100)/rec.amount_untaxed if rec.amount_untaxed else 0

    discount_amount = fields.Float('Total Disocunt', compute="_total_discount", digits=dp.get_precision('Discount'))
    avg_discount = fields.Float('Avg Disocunt', compute="_total_discount", digits=dp.get_precision('Discount'))
    print_discount = fields.Boolean('Print Discount')
    print_discount_amount = fields.Boolean('Print Discount Amount')

class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def _total_discount(self):
        for rec in self:
            discount = ((rec.discount*rec.price_unit)/100)
            print ("diskon",discount)
            rec.discount_per_unit = discount
            rec.discount_amount = discount*rec.quantity
            rec.discounted_unit_price = rec.price_unit - discount

    discount_amount = fields.Float('Disocunt Amount', compute="_total_discount", digits=dp.get_precision('Discount'))
    discount_per_unit = fields.Float('Discount Per Unit', compute="_total_discount", digits=dp.get_precision('Discount'))
    discounted_unit_price = fields.Float('Discounted Unit Price', compute="_total_discount", digits=dp.get_precision('Discount'))
