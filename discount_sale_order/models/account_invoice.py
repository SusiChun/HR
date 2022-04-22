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

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'global_discount_type', 'global_order_discount')
    def _compute_amount(self):
        totalAmount, totalDiscount = 0, 0
        amountUntaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        amountTax = sum(line.amount for line in self.tax_line_ids)
        totalAmount = amountUntaxed + amountTax
        lineTotalDiscount = sum((line.quantity*(line.price_unit) - line.price_subtotal) if line.discount_type == 'percent' else line.discount for line in self.invoice_line_ids)
        totalDiscount = lineTotalDiscount
        print (totalDiscount),"totalDiscount"
        # Modify by Baim
        # IrConfigPrmtrSudo = self.env['ir.config_parameter'].sudo() # For Odoo 12
        ir_values_obj = self.env['ir.values']
        orderObj = False
        discTax = 'untax'
        moduleObj = self.env['ir.module.module'].sudo().search(
            [("name","=","discount_purchase_order"),("state","=","installed")])
        if self.type and self.type == 'in_invoice' and moduleObj:
            orderObj = self.env['purchase.order'].sudo().search([('name', '=', self.origin)])
            # Modify by Baim
            # discTax = IrConfigPrmtrSudo.get_param('purchase.global_discount_tax') # For Odoo 12
            discTax = ir_values_obj.sudo().get_default('purchase.config.settings', 'global_discount_tax')
        if self.type and self.type == 'out_invoice':
            orderObj = self.env['sale.order'].sudo().search([('name', '=', self.origin)])
            # Modify by Baim
            # discTax = IrConfigPrmtrSudo.get_param('sale.global_discount_tax') # For Odoo 12
            discTax = ir_values_obj.sudo().get_default('sale.config.settings', 'global_discount_tax')
        totalGlobalDiscount = 0
        if discTax == 'untax':
            totalAmount = amountUntaxed
        else:
            totalAmount = amountUntaxed + amountTax
        if self.global_discount_type == 'percent':
            beforeGlobal = totalAmount
            totalAmount = totalAmount * (1 - (self.global_order_discount or 0.0)/100)
            totalGlobalDiscount = beforeGlobal - totalAmount
            totalDiscount += totalGlobalDiscount
        else:
            totalGlobalDiscount = self.global_order_discount or 0.0
            totalAmount = totalAmount - totalGlobalDiscount
            totalDiscount += totalGlobalDiscount
        if discTax == 'untax':
            totalAmount = totalAmount + amountTax
        self.total_discount = totalDiscount
        self.amount_untaxed = amountUntaxed
        self.amount_tax = amountTax
        self.amount_total = totalAmount
        self.total_global_discount = totalGlobalDiscount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            quantity = 1.0
            if line.discount_type == 'fixed':
                price_unit = line.price_unit * line.quantity - (line.discount or 0.0)
            else:
                quantity = line.quantity
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped

    total_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    total_global_discount = fields.Monetary(string='Total Global Discount', store=True, readonly=True, compute='_compute_amount')
    global_discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent', 'Percent')
        ], string="Discount Type")
    global_order_discount = fields.Float(string='Global Discount', store=True)

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        inv_obj = self[0]
        if inv_obj.total_discount > 0.0 and self.type in ('out_invoice', 'in_refund'):
            # Modify by Baim
            # IrConfigPrmtr = self.env['ir.config_parameter'].sudo() # For Odoo 12
            ir_values_obj = self.env['ir.values']
            # global_account = IrConfigPrmtr.get_param('sale.discount_account_so') # For Odoo 12
            global_account = ir_values_obj.sudo().get_default('sale.config.settings', 'discount_account_so')
            if not global_account:
                raise UserError(_("Global Discount!\nPlease first set account for global discount in sales setting"))
            if global_account and int(global_account):
                global_account = self.env['account.account'].browse(int(global_account))
                for _, _ , line in move_lines:
                    if line.get('debit') and not line.get('product_id'):
                        line['debit'] -= inv_obj.total_discount
                        break
                amount_currency = 0.0
                currency = inv_obj.currency_id
                company_currency = inv_obj.company_id.currency_id
                diff_currency = currency != company_currency
                if diff_currency:
                    # Modify by Baim
                    # date = self._get_currency_rate_date() or fields.Date.context_today(self)
                    date = self.date_invoice or fields.Date.context_today(self)
                    amount_currency = currency._convert(inv_obj.total_global_discount, company_currency, inv_obj.company_id, date)
                else:
                    currency = False
                global_line =  {
                    'type': 'dest',
                    'name': global_account.name,
                    'price': inv_obj.total_discount,
                    'account_id': global_account.id,
                    'date_maturity': inv_obj.date_due,
                    'amount_currency': diff_currency and amount_currency,
                    'currency_id': currency and currency.id,
                    'invoice_id': inv_obj.id
                }
                part = self.env['res.partner']._find_accounting_partner(inv_obj.partner_id)
                global_line = [(0, 0, self.line_get_convert(global_line, part.id))]
                move_lines += global_line
        return move_lines

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        values = super()._prepare_refund(
            invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
        values.update({
            'global_discount_type' : invoice.global_discount_type,
            'global_order_discount' : invoice.global_order_discount,
        })
        return values


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount = fields.Float(string='Discount', digits=dp.get_precision('Discount'), default=0.0)
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percent', 'Percent')
        ], string="Discount Type")


    @api.one
    @api.depends('price_unit', 'discount', 'discount_type', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        quantity = 1.0
        subTotalAmount = 0.0
        if self.discount_type == 'fixed':
            price = self.price_unit * self.quantity - self.discount or 0.0
            subTotalAmount = price
        else:
            quantity = self.quantity
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
            subTotalAmount = self.quantity * price
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(
                price, currency, quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else subTotalAmount
        self.price_total = taxes['total_included'] if taxes else self.price_subtotal
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            currency = self.invoice_id.currency_id
            # Modify by Baim
            # date = self.invoice_id._get_currency_rate_date() # For Odoo 12
            # price_subtotal_signed = currency._convert(
                # price_subtotal_signed, self.invoice_id.company_id.currency_id,
                # self.company_id or self.env.user.company_id,  date or fields.Date.today()) # For Odoo 12
            price_subtotal_signed = self.invoice_id.currency_id.with_context(
                date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
