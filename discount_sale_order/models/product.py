# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"


    income_dsicount     = fields.Many2one(comodel_name='account.account',string='Income Discount')
    expense_dsicount     = fields.Many2one(comodel_name='account.account',string='Expense Discount')

class ProductProduct(models.Model):
    _inherit = "product.product"


    income_dsicount     = fields.Many2one(related='product_tmpl_id.income_dsicount',string='Income Discount')
    expense_dsicount     = fields.Many2one(related='product_tmpl_id.expense_dsicount',string='Expense Discount')


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    discount_journal_id     = fields.Many2one(comodel_name='account.move',string='Discount Journal')

    @api.multi
    def discount_journal_create(self,move_lines):
        for x in self:
            print ("hahahahahhaha",move_lines)
            for inv in x.invoice_line_ids:
                for _, _ , line in move_lines:
                    if line.get('debit') and not line.get('product_id'):
                        line['debit'] -= inv.discount
                        break
                        print ("hahahahahahh")
                        global_line = {
                            'type': 'dest',
                            'name': inv.product_id.income_discount.name,
                            'price': inv.discount,
                            'account_id': inv.product_id.income_discount.id,
                            'date_maturity': inv.date_due,
                            # 'amount_currency': diff_currency and amount_currency,
                            # 'currency_id': currency and currency.id,
                            'invoice_id': inv.invoice_id.id
                        }
                    part = self.env['res.partner']._find_accounting_partner(x.partner_id)
                    global_line = [(0, 0, self.line_get_convert(global_line, part.id))]
                    move_lines += global_line
        return move_lines
