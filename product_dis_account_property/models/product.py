# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    property_account_income_discount = fields.Many2one('account.account', company_dependent=True,
        string="Discount Income Account", 
        domain=[('deprecated', '=', False)],
        help="This account will be used for expenses discount accounting entry.")
    property_account_expense_discount = fields.Many2one('account.account', company_dependent=True,
        string="Discount Expense Account", 
        domain=[('deprecated', '=', False)],
        help="This account will be used for incomes discount accounting entry.")


    