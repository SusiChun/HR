# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError, ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta


class hr_contract(models.Model):
    _inherit= 'hr.contract'

    tunjangan_jabatan = fields.Float('Tunjangan Jabatan',compute='compute_current_wage',store=True)
    tunjangan_makan = fields.Float('Tunjangan Transport & Makan',compute='compute_current_wage',store=True)
    tunjangan_proyek = fields.Float('Tunjangan Proyek',compute='compute_current_wage',store=True)
    tunjangan_hp        = fields.Float('Tunjangan HP',compute='compute_current_wage',store=True)
    tunjangan_sertifikasi = fields.Float('Tunjangan Sertifikasi',compute='compute_current_wage',store=True)
    tunjangan_lainnya = fields.Float('Tunjangan Lain-lain',compute='compute_current_wage',store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Proccess'),
        ('pending', 'Running'),
        ('close', 'Expired'),
    ], string='Status', track_visibility='onchange', help='Status of the contract', default='draft')
    wage_ids        = fields.One2many(comodel_name='hr.contract.wage',inverse_name='contract_id')
    wage            = fields.Float(digits=(16, 2), readonly=False, required=False, compute='compute_current_wage', store=True)

    @api.depends('wage_ids.wage','wage_ids.tunjangan_jabatan',
                 'wage_ids.tunjangan_makan','wage_ids.tunjangan_proyek',
                 'wage_ids.tunjangan_hp','wage_ids.tunjangan_sertifikasi',
                 'wage_ids.tunjangan_lainnya')
    @api.multi
    def compute_current_wage(self):
        for x in self:
            data = self.env[('hr.contract.wage')].search([('contract_id','=',x.id)],order='id desc', limit=1)
            for y in data:
                # search([], order='start asc', limit=1)
                if y:
                    x.wage = y.wage
                    self.limit_reimbers_year = y.wage
                    x.tunjangan_jabatan = y.tunjangan_jabatan
                    x.tunjangan_makan = y.tunjangan_makan
                    x.tunjangan_proyek = y.tunjangan_proyek
                    x.tunjangan_hp = y.tunjangan_hp
                    x.tunjangan_sertifikasi = y.tunjangan_sertifikasi
                    x.tunjangan_lainnya = y.tunjangan_lainnya

    @api.multi
    def submit(self):
        self.state = 'open'

    @api.multi
    def process(self):
        self.state = 'pending'

    @api.multi
    def expired(self):
        self.state = 'close'


class contract_detail(models.Model):
    _name= 'hr.contract.wage'
    _order= 'id asc'

    contract_id             = fields.Many2one(comodel_name='hr.contract')
    # employee_id             = fields.Many2one('hr.employee', string="Employee", required=True, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),readonly=True, states={'draft': [('readonly', False)], 'refused': [('readonly', False)]})
    # employee                = fields.Many2one('res.user','Company',default=lambda self: self.env.user.id)
    start_periode           = fields.Date('Start Date')
    end_periode             = fields.Date('End Date')
    wage                    = fields.Float(string="Wage",required=True)
    tunjangan_jabatan       = fields.Float('Tunjangan Jabatan')
    tunjangan_makan         = fields.Float('Tunjangan Transport & Makan')
    tunjangan_proyek        = fields.Float('Tunjangan Proyek')
    tunjangan_hp            = fields.Float('Tunjangan HP')
    tunjangan_sertifikasi   = fields.Float('Tunjangan Sertifikasi')
    tunjangan_lainnya       = fields.Float('Tunjangan Lain-lain')
    total                   = fields.Float('Total', compute='_compute_total')

    @api.depends('wage','tunjangan_jabatan','tunjangan_makan','tunjangan_proyek',
                 'tunjangan_hp','tunjangan_sertifikasi','tunjangan_lainnya')
    def _compute_total(self):
        for y in self:
            y.total = y.wage + y.tunjangan_jabatan + y.tunjangan_makan + y.tunjangan_proyek + y.tunjangan_hp + y.tunjangan_sertifikasi + y.tunjangan_lainnya
