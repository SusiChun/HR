# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.depends('advance_expense_id', 'advance_expense_id.total_amount')
    def _compute_advance_expense_id(self):
        for rec in self:
            amount = 0.0
            amount = rec.advance_expense_id.total_amount
            rec.advance_amount = amount

    # Added by Baim
    @api.onchange('product_id')
    def onchange_product_id_advance(self):
        for rec in self:
            rec.advance_expense_id = False

    advance_expense_id = fields.Many2one(
        'advance.expense.line', 
        string='Expense Advance', 
        copy=False
    )
    advance_amount = fields.Float(
        string='Advance Amount', 
        compute='_compute_advance_expense_id', 
        store=True
    )
    advance_currency_id = fields.Many2one(
        'res.currency', 
        string='Expense Advance Currency', 
        related='advance_expense_id.currency_id',
        store=True,
    )
    
    @api.multi
    def submit_expenses(self): # Override Odoo method.
        result = super(HrExpense, self).submit_expenses()
        for rec in self:
            if rec.advance_expense_id:
                rec.advance_expense_id.reambursment = True
        return result
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
