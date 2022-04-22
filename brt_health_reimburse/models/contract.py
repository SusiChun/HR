# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class BrtContract(models.Model):
    _inherit = "hr.contract"

    limit_reimbers_year = fields.Float(string="Limit",compute='compute_limit_for_wage')
    berobat 			= fields.Float(string="Berobat")
    kacamata 			= fields.Float(string="Kacamata")
    sisa 				= fields.Float(string="Sisa",compute='compute_limit_for_wage')
    # sisa 				= fields.Float(string="Sisa",compute='compute_limit_for_wage')
    year 				= fields.Char(string='Year', readonly=True)
    history_ids        	= fields.One2many(comodel_name='brt_health.histroy', string="History", inverse_name='Contract', ondelete='cascade')

    @api.multi
    def compute_limit_for_wage(self):
        for x in self:
            data = self.env[('hr.contract')].search([('id','=',self.id)],order='id desc', limit=1)
            for y in data:
                # search([], order='start asc', limit=1)
                if y:
                    total_limit = float(y.wage) + float(y.tunjangan_jabatan)+ float(y.tunjangan_makan)+ float(y.tunjangan_proyek)+ float(y.tunjangan_hp)+ float(y.tunjangan_sertifikasi)+ float(y.tunjangan_lainnya)
                    self.limit_reimbers_year = total_limit
                    hitung1 = self.limit_reimbers_year - self.sisa
                    hitung2 = hitung1 - self.kacamata - self.berobat
                    self.sisa = hitung2
                    
    # @api.multi
    # def compute_sisa(self):
    #    self.sisa = self.limit_reimbers_year - self.berobat - self.kacamata

class brt_history_reimburse(models.Model):
    _name 			= 'brt_health.histroy'
    _description 	= "History Health Reimburse"

    name 			= fields.Char(string='Descripstion', required=True, readonly=True)
    date 			= fields.Date(string="Date",readonly=True)
    amount 			= fields.Char(string='Amount', readonly=True)
    year 			= fields.Char(string='Year', readonly=True)
    id_reimberse	= fields.Char(string='Reimburse', readonly=True)
    employee_id 	= fields.Many2one('hr.employee', string='Employee', required=True)
    Contract        = fields.Many2one(comodel_name='hr.contract', string="Contract", required=False)


