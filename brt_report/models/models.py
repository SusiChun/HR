# -*- coding: utf-8 -*-

from odoo import models, fields, api

class template_report(models.Model):
    _name 			= 'brt_report.template_report'

    name 			= fields.Char(string="Nama Template")
    kode 			= fields.Char(string="Kode Template")
    template        = fields.Html(string='Template Surat') 
