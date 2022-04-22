
import time
import fungsi_terbilang
from odoo import models, fields, api, _


class account_invoice(models.Model):
    _inherit = "account.invoice"

    def terbilang(self, amount_total):
        hasil = fungsi_terbilang.terbilang(amount_total, "idr", 'id')
        return hasil

