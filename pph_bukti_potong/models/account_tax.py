# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta


class account_tax(models.Model):
    _inherit= 'account.tax'

    is_pph23 = fields.Boolean('PPH 23')
    is_pphfinal = fields.Boolean('PPH Final')
    pph23_type = fields.Selection([
                                    ('01', 'Dividen'),
                                    ('02', 'Bunga'),
                                    ('03', 'Royalti'),
                                    ('04', 'Hadiah dan Penghargaan'),
                                    ('05', 'Sewa dan penghasilan lain'),
                                    ('06', 'Jasa Teknik'),
                                    ('07', 'Jasa Manajemen'),
                                    ('08', 'Jasa Konsultan'),
                                    ('09', 'Jasa Lainnya'),
                                ], 'Jenis PPH 23')
