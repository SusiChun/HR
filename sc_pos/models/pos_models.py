# -*- coding: utf-8 -*-

import logging

import psycopg2
import pytz

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class sc_pos(models.Model):
    _inherit = 'pos.config'

    bottom_price_active  = fields.Boolean(string='Bottom Price Active')
    bottom_price            = fields.Float(string='Bottom Price')


class pos(models.Model):
    _inherit = 'pos.order'


    pos_references  = fields.Char(string='POS References',copy=False,compute='_bottom_price',store=True)
    config_id           = fields.Many2one(comodel_name='pos.config',string='Config',related='session_id.config_id',store=True)
    bottom_price_active = fields.Boolean(string='Bottom Price Active',related='session_id.config_id.bottom_price_active',store=True)
    bottom_price        = fields.Float(string='Bottom Price',related='session_id.config_id.bottom_price',store=True)

    @api.multi
    @api.depends('bottom_price_active','bottom_price','amount_total')
    def _bottom_price(self):
        for x in self:
            if x.bottom_price_active == True and x.amount_total < x.bottom_price:
                x.pos_references = self.env['ir.sequence'].next_by_code('POS_REFERENCES')
                print ("POS References 1",x.pos_references)
            else:
                x.pos_references = ""
                print("POS References 2", x.pos_references)

                        #self.outlet = True



    @api.multi
    def action_pos_order(self):
        action = {
            'name': ('POS Order'),
            'type': "ir.actions.act_window",
            'res_model': "pos.order",
            'view_type': "form",
            'limit': 20,
            'view_mode': "tree,form",
            'view_id': False,
            'views': [
                (self.env.ref('point_of_sale.view_pos_order_tree').id, 'tree'),
                (self.env.ref('point_of_sale.view_pos_pos_form').id, 'form'),
            ],
            'context': {}
            ,
        }
        if self.env.user.has_group('sc_pos.group_user_outlet'):
            print ("masuk")
            action['domain'] = [('pos_references', '!=', False)]
        return action

# class PosOrderReport(models.Model):
#     _inherit = "report.pos.order"
#
#     outlet = fields.Boolean(string='Outlet', readonly=True)
#
#     @api.model_cr
#     def init(self):
#         if self.env.user.has_group('sc_pos.group_user_outlet'):
#             print ("user outlet")
#             tools.drop_view_if_exists(self._cr, 'point_of_sale.report_pos_order')
#             self._cr.execute("""
#                 CREATE OR REPLACE VIEW report_pos_order AS (
#                     SELECT
#                         MIN(l.id) AS id,
#                         COUNT(*) AS nbr_lines,
#                         s.date_order AS date,
#                         SUM(l.qty) AS product_qty,
#                         SUM(l.qty * l.price_unit) AS price_sub_total,
#                         SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
#                         SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
#                         (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
#                         SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
#                         s.id as order_id,
#                         s.partner_id AS partner_id,
#                         s.state AS state,
#                         s.user_id AS user_id,
#                         s.location_id AS location_id,
#                         s.company_id AS company_id,
#                         s.sale_journal AS journal_id,
#                         l.product_id AS product_id,
#                         pt.categ_id AS product_categ_id,
#                         p.product_tmpl_id,
#                         ps.config_id,
#                         pt.pos_categ_id,
#                         pc.stock_location_id,
#                         s.pricelist_id,
#                         s.session_id,
#                         s.invoice_id IS NOT NULL AS invoiced
#                     FROM pos_order_line AS l
#                         LEFT JOIN pos_order s ON (s.id=l.order_id)
#                         LEFT JOIN product_product p ON (l.product_id=p.id)
#                         LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
#                         LEFT JOIN product_uom u ON (u.id=pt.uom_id)
#                         LEFT JOIN pos_session ps ON (s.session_id=ps.id)
#                         LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
#                         where s.outlet ='t'
#                     GROUP BY
#                         s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
#                         s.user_id, s.location_id, s.company_id, s.sale_journal,
#                         s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
#                         l.product_id,
#                         pt.categ_id, pt.pos_categ_id,
#                         p.product_tmpl_id,
#                         ps.config_id,
#                         pc.stock_location_id
#                     HAVING
#                         SUM(l.qty * u.factor) != 0
#                 )
#             """)
#         else:
#             tools.drop_view_if_exists(self._cr, 'point_of_sale.report_pos_order')
#             self._cr.execute("""
#                 CREATE OR REPLACE VIEW report_pos_order AS (
#                     SELECT
#                         MIN(l.id) AS id,
#                         COUNT(*) AS nbr_lines,
#                         s.date_order AS date,
#                         SUM(l.qty) AS product_qty,
#                         SUM(l.qty * l.price_unit) AS price_sub_total,
#                         SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total,
#                         SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount,
#                         (SUM(l.qty*l.price_unit)/SUM(l.qty * u.factor))::decimal AS average_price,
#                         SUM(cast(to_char(date_trunc('day',s.date_order) - date_trunc('day',s.create_date),'DD') AS INT)) AS delay_validation,
#                         s.id as order_id,
#                         s.partner_id AS partner_id,
#                         s.state AS state,
#                         s.user_id AS user_id,
#                         s.location_id AS location_id,
#                         s.company_id AS company_id,
#                         s.sale_journal AS journal_id,
#                         l.product_id AS product_id,
#                         pt.categ_id AS product_categ_id,
#                         p.product_tmpl_id,
#                         ps.config_id,
#                         pt.pos_categ_id,
#                         pc.stock_location_id,
#                         s.pricelist_id,
#                         s.session_id,
#                         s.invoice_id IS NOT NULL AS invoiced
#                     FROM pos_order_line AS l
#                         LEFT JOIN pos_order s ON (s.id=l.order_id)
#                         LEFT JOIN product_product p ON (l.product_id=p.id)
#                         LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
#                         LEFT JOIN product_uom u ON (u.id=pt.uom_id)
#                         LEFT JOIN pos_session ps ON (s.session_id=ps.id)
#                         LEFT JOIN pos_config pc ON (ps.config_id=pc.id)
#                     GROUP BY
#                         s.id, s.date_order, s.partner_id,s.state, pt.categ_id,
#                         s.user_id, s.location_id, s.company_id, s.sale_journal,
#                         s.pricelist_id, s.invoice_id, s.create_date, s.session_id,
#                         l.product_id,
#                         pt.categ_id, pt.pos_categ_id,
#                         p.product_tmpl_id,
#                         ps.config_id,
#                         pc.stock_location_id
#                     HAVING
#                         SUM(l.qty * u.factor) != 0
#                 )
#             """)
