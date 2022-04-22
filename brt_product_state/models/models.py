from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
import time
from Tkconstants import LEFT
from datetime import date
from time import gmtime, strftime

class brt_product_state(models.Model):
    _inherit = 'product.template'

    state = fields.Selection(selection=[('Draft', 'Draft'), ('Confirmed', 'Confirmed')], string='Status', default='Draft')

    def confirm_produk(self):
        self.state = 'Confirmed'
