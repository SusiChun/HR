# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.tools.float_utils import float_is_zero, float_compare
import openerp.addons.decimal_precision as dp
from odoo.exceptions import RedirectWarning

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # def _bom_qty(self):
    #     qty = 0.0
    #     for i in self:
    #         bom_line = self.env['mrp.bom.line'].sudo().search([('bom_id.type','=','phantom'),('bom_id.product_tmpl_id','=',i.id),('bom_id.active','=',True)])
    #         if bom_line :
    #             product_ids = bom_line.mapped('product_qty')
    #             qty = sum(product_ids)
    #         i.bom_qty_function = round(qty,2)
    #         i.write({'bom_qty':round(qty,2)})

    # class_id = fields.Many2one('product.class','Class')
    # group_id = fields.Many2one('product.group','Group')
    # jenis_id = fields.Many2one('product.jenis','Jenis',domain="[('group_id','=',group_id)]")
    # season_id = fields.Many2one('product.season',string='Season')
    # tahun = fields.Integer(string='Tahun')
    # caracuci_id = fields.Many2one('product.caracuci',string='Cara Cuci')
   # product_type = fields.Selection([('raw','Raw Material'),('finish','Finish Good'),('asset','Asset'),('other','Other'),('operational','Operational')],string='Product Category')
#     raw_material_bom = fields.Selection([('fabric','Fabric'),('support','Support')],string='Raw Material Type',)
#     brand_id = fields.Many2one('master.brand', 'Brand')
#     tags_ids = fields.Many2many('product.tag','product_template_product_tag_rel', column1='product_tmpl_id',column2='product_tag_id',string='Tags')
#     image2 = fields.Binary("Second Image ", attachment=True,)
#     image3 = fields.Binary("Third Image", attachment=True,)
#     image4 = fields.Binary("Fourth Image ", attachment=True,)
#     image5 = fields.Binary("Fifth Image", attachment=True,)
#     kodebulantahun = fields.Char('Kode Bulan tahun', size=25)
#     incoming_date = fields.Date('Incoming Date')
#     display_on_android_sales = fields.Boolean('Display on Android Sales')
#     uom_so_id = fields.Many2one('product.uom',string='Sale Unit of Measure')
#     notes = fields.Text('Notes')
#     bom_qty_function = fields.Float('BoM Qty Function',compute="_bom_qty")
#     bom_qty = fields.Float('BoM Qty',)
#     is_consignee = fields.Boolean('Is Consignee')
#     min_order_qty = fields.Float('Min Order Qty', default=1.0)
#
#     @api.onchange('season_id')
#     def onchange_season_id(self):
#         season = self.season_id.start_date
#         if season:
#             tahun = season[:4]
#             self.tahun = int(tahun)
#
#
# #     @api.multi
# #     def _create_default_code(self, brand_id, class_id, group_id, jenis_id):
# #         brand = self.env['master.brand'].browse(brand_id).code
# #         clas = self.env['product.class'].browse(class_id)
# #         class12 = clas.name
# #         class3 = clas.code
# #         class123 = class12+class3
# #         group = self.env['product.group'].browse(group_id).code
# #         jenis = self.env['product.jenis'].browse(jenis_id).code
# #         titik = '.'
# #         name = brand+class123+titik+group+jenis+titik
# #         new_name = name + '0001'
# #         old_name = name+'%'
# #         # SUBSTRING ( expression ,start , length )
# #         self._cr.execute("SELECT name,SUBSTRING(name, 7, 3) AS Initial FROM product_template " \
# #                             "WHERE default_code like %s AND LENGTH(name) = 9 ORDER BY Initial DESC limit 1" , (old_name ,))
# #         exist      = self._cr.fetchone()
# #         if exist :
# #             new_seq = "%04d" % (int(exist[1])+1)
# #             new_name = name + str(new_seq)
# #         return str(new_name)
#
# #     @api.model
# #     def create(self, vals):
# #         product_tmpl = super(ProductTemplate, self).create(vals)
# #         if product_tmpl.product_type == 'finish' and not product_tmpl.default_code:
# #             if product_tmpl.brand_id and product_tmpl.class_id and product_tmpl.group_id and product_tmpl.jenis_id :
# #                 default_code = self._create_default_code(product_tmpl.brand_id.id,product_tmpl.class_id.id,product_tmpl.group_id.id,product_tmpl.jenis_id.id)
# #                 product_tmpl.update({'default_code' : default_code})
# #         return product_tmpl
#
# # ProductTemplate()
#
# # class ProductProduct(models.Model):
# #     _inherit = "product.product"
#
# #     @api.model
# #     def create(self, vals):
# #         #import pdb;pdb.set_trace()
# #         product = super(ProductProduct, self).create(vals)
# #         if product.product_type == 'finish' and not product.default_code :
# #             if product.attribute_value_ids :
# #                 if product.brand_id and product.class_id and product.group_id and product.jenis_id :
# #                     default_code = self.env['product.template']._create_default_code(product.brand_id.id,product.class_id.id,product.group_id.id,product.jenis_id.id)
# #                     size = '0'
# #                     color = '0'
# #                     for vr in product.attribute_value_ids :
# #                         if vr.attribute_id.name in ('Size','SIZE','size') :
# #                             size = str(vr.code)
# #                         elif vr.attribute_id.name in ('Color','COLOR','color') :
# #                             color = str(vr.code)
# #                         elif vr.attribute_id.name in ('Color2','COLOR2','color2') :
# #                             size = ''
# #                             color = str(vr.code)
# #                     product.update({'default_code':default_code+size+color})
# #         return product
#
# # ProductProduct()
#
#
# class ProductAttributeValue(models.Model):
#     _inherit = "product.attribute.value"
#
#     @api.multi
#     def name_get(self):
#         result = []
#         for res in self:
#             name = res.name
#             if res.code :
#                 name = '['+res.code+'] '+name
#             result.append((res.id, name))
#         return result
#
#     code = fields.Char('Code', size=25)
#
# ProductAttributeValue()
#
#
# class ProductCategory(models.Model):
#     _inherit = 'product.category'
#
#     code = fields.Char('Code')
#
# ProductCategory