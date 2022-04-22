# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    disc_move_id = fields.Many2one('account.move', string='Disc Journal Entry',
        readonly=True, index=True, ondelete='restrict', copy=False,
        help="Link to the automatically generated Journal Items.")
        
    @api.multi
    def action_cancel(self):
        result = super(account_invoice, self).action_cancel()
        moves = self.env['account.move']
        for inv in self:
            if inv.disc_move_id:
                moves += inv.disc_move_id
        # First, set the invoices as cancelled and detach the move ids
        self.write({'disc_move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return True
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        result = super(account_invoice, self).action_move_create()
        self.move_id.write({'state':'draft'})
        disc_move_id = self.env['account.move'].create({'name':self.move_id.name+':Disc', 'journal_id': self.move_id.journal_id.id, 'date': self.move_id.date ,'invoice_id':self.id or False})
        disc_vals = []
        for line in self.invoice_line_ids:
            if line.discount == 0.0:
                continue
            if (not line.product_id.property_account_income_discount) and (not line.product_id.property_account_expense_discount):
                raise except_orm(_('Discount Account Missing !'),
                    _("You have to configure discount income/expense account for '%s'!") % (line.product_id.name,))
            line_discount = (line.discount / 100) * line.price_unit * line.quantity
            for x in self.move_id.line_ids:
                ml = x.filtered(lambda l: (l.debit == line.price_subtotal) or (l.credit == line.price_subtotal))
                if ml.credit > 0.0:
                    cr_line_dict = {"name": ml.name,
                                    "account_id": ml.account_id.id,
                                    "date":ml.date,
                                    "journal_id":self.journal_id.id,
                                    "partner_id": self.partner_id.id,
                                    'credit': line_discount,
                                    'move_id': disc_move_id.id}
                    disc_vals.append((0, 0, cr_line_dict))
                    dr_line_dict = {"name": "Sale Disc",
                                    "account_id": line.product_id.property_account_expense_discount.id,
                                    "debit": line_discount,
                                    "date": ml.date,
                                    "journal_id": self.journal_id.id,
                                    "partner_id": self.partner_id.id,
                                    "move_id": disc_move_id.id}
                    disc_vals.append((0, 0, dr_line_dict))
                if ml.debit > 0.0:
                    dr_line_dict = {"name": ml.name,
                                    "account_id": ml.account_id.id,
                                    "date":ml.date,
                                    "journal_id":self.journal_id.id,
                                    "partner_id": self.partner_id.id,
                                    'debit': line_discount,
                                    'move_id': disc_move_id.id}
                    disc_vals.append((0, 0, dr_line_dict))
                    cr_line_dict = {"name": "Purchase Disc",
                                    "account_id": line.product_id.property_account_income_discount.id,
                                    "credit": line_discount,
                                    "date": ml.date,
                                    "journal_id": self.journal_id.id,
                                    "partner_id": self.partner_id.id,
                                    "move_id": disc_move_id.id}
                    disc_vals.append((0, 0, cr_line_dict))
            disc_move_id.write({'line_ids': disc_vals})
            if disc_move_id.line_ids:
                self.write({'disc_move_id':disc_move_id.id})
            else:
                disc_move_id.unlink()
            self.move_id.post()
        return result
