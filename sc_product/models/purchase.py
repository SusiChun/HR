from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class Purchase(models.Model):
    _inherit = 'purchase.order'


    # total_qty        = fields.Float(string="Total Qty",compute='_compute_total',store=True)
    # total_volume     = fields.Float(string="Total Volume",compute='_compute_volume',store=True)
    total_qty_volume = fields.Float(string="Total Volume",compute='_compute_total_volume',store=True)
    total_volume_a  = fields.Float(string="Total Volume Gol A",compute='_compute_volume_gol',store=True)
    total_volume_b  = fields.Float(string="Total Volume Gol B",compute='_compute_volume_gol',store=True)
    total_volume_c  = fields.Float(string="Total Volume Gol C",compute='_compute_volume_gol',store=True)


    @api.multi
    @api.depends('order_line.product_id.golongan','order_line.golongan','order_line.total_qty_volume')
    def _compute_volume_gol(self):
        for record in self:
            record.total_volume_a = sum(line.total_qty_volume for line in record.order_line if line.golongan == 'A')
            record.total_volume_b = sum(line.total_qty_volume for line in record.order_line if line.golongan == 'B')
            record.total_volume_c = sum(line.total_qty_volume for line in record.order_line if line.golongan == 'C')

    # @api.multi
    # @api.depends('order_line.product_qty','order_line.golongan')
    # def _compute_total(self):
    #     for record in self:
    #         record.total_qty = sum(line.product_qty for line in record.order_line)

    #
    # @api.multi
    # @api.depends('order_line.product_id.volume')
    # def _compute_volume(self):
    #     for record in self:
    #         record.total_volume = sum(line.product_id.volume for line in record.order_line)

    @api.multi
    @api.depends('order_line.total_qty_volume')
    def _compute_total_volume(self):
        for record in self:
            record.total_qty_volume = sum(line.total_qty_volume for line in record.order_line)




class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'


    qty_karton      = fields.Float(string="Qty Karton")
    golongan        = fields.Selection([('A', 'Golongan A <5%'),('B','Golongan B 5-20%'),('C','Golongan C >20%')],string='Golongan')
    isi_karton      = fields.Float(string="Isi Karton")
    volume          = fields.Float(string="Volume", related="product_id.volume")
    product_qty     = fields.Float(string="Qty")
    total_qty_volume      = fields.Float(string="Total Qty Volume", compute='_compute_qty_volume1', store=True)




    @api.depends('qty_karton','isi_karton')
    @api.onchange('qty_karton', 'isi_karton')
    def onchange_product(self):
        if self.qty_karton or self.isi_karton:
            self.product_qty = self.qty_karton * self.isi_karton

    @api.depends('product_id')
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.golongan = self.product_id.golongan

    @api.multi
    @api.depends('product_qty','volume')
    def _compute_qty_volume1(self):
        for record in self:
            record.total_qty_volume =  record.volume * record.product_qty

