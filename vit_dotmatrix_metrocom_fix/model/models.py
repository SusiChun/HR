from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class invoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    printer_data = fields.Text(string="Printer Data", required=False, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix Invoice')])
        data = tpl.render_template(tpl.body_html, 'account.invoice', self.id, post_process=False)
        self.printer_data = data

    @api.multi
    def action_invoice_cancel(self):
        self.printer_data=''
        return super(invoice, self).action_cancel()

    @api.multi
    def action_invoice_open(self):
        res=super(invoice, self).action_invoice_open()
        self.generate_printer_data()
        return res


class purchase(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    printer_data = fields.Text(string="Printer Data", required=False, )

    @api.multi
    def generate_printer_data(self):
        tpl = self.env['mail.template'].search([('name', '=', 'Dot Matrix PO')])
        data = tpl.render_template(tpl.body_html, 'purchase.order', self.id, post_process=False)
        self.printer_data = data


    @api.multi
    def button_confirm(self):
        res = super(purchase, self).button_confirm()
        self.generate_printer_data()
        return res
