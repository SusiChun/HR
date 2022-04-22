from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_qty_volume = fields.Float(string="Total Volume",compute='_compute_total_volume',store=True)
    total_volume_a  = fields.Float(string="Total Volume Gol A",compute='_compute_volume_gol',store=True)
    total_volume_b  = fields.Float(string="Total Volume Gol B",compute='_compute_volume_gol',store=True)
    total_volume_c  = fields.Float(string="Total Volume Gol C",compute='_compute_volume_gol',store=True)


    @api.multi
    @api.depends('move_lines.product_id.golongan','move_lines.total_qty_volume')
    def _compute_volume_gol(self):
        for record in self:
            record.total_volume_a = sum(line.total_qty_volume for line in record.move_lines if line.golongan == 'A')
            record.total_volume_b = sum(line.total_qty_volume for line in record.move_lines if line.golongan == 'B')
            record.total_volume_c = sum(line.total_qty_volume for line in record.move_lines if line.golongan == 'C')

    @api.multi
    @api.depends('move_lines.total_qty_volume')
    def _compute_total_volume(self):
        for record in self:
            record.total_qty_volume = sum(line.total_qty_volume for line in record.move_lines)




class StockPack(models.Model):
    _inherit = 'stock.pack.operation'

    golongan        = fields.Selection([('A', 'Golongan A <5%'),('B','Golongan B 5-20%'),('C','Golongan C >20%')],related='product_id.golongan',string='Golongan')
    volume          = fields.Float(string="Volume", related="product_id.volume")
    total_qty_volume = fields.Float(string="Total Qty Volume", compute='_compute_qty_volume1', store=True)


    @api.multi
    @api.depends('product_qty','volume')
    def _compute_qty_volume1(self):
        for record in self:
            record.total_qty_volume =  record.volume * record.product_qty


class StockMove(models.Model):
    _inherit = 'stock.move'

    golongan        = fields.Selection([('A', 'Golongan A <5%'),('B','Golongan B 5-20%'),('C','Golongan C >20%')],related='product_id.golongan',string='Golongan')
    volume          = fields.Float(string="Volume", related="product_id.volume")
    total_qty_volume = fields.Float(string="Total Qty Volume", compute='_compute_qty_volume1', store=True)


    @api.multi
    @api.depends('product_uom_qty','volume')
    def _compute_qty_volume1(self):
        for record in self:
            record.total_qty_volume =  record.volume * record.product_uom_qty