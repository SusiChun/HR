# -*- coding: utf-8 -*-
from odoo import http

# class BrtProductState(http.Controller):
#     @http.route('/brt_product_state/brt_product_state/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_product_state/brt_product_state/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_product_state.listing', {
#             'root': '/brt_product_state/brt_product_state',
#             'objects': http.request.env['brt_product_state.brt_product_state'].search([]),
#         })

#     @http.route('/brt_product_state/brt_product_state/objects/<model("brt_product_state.brt_product_state"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_product_state.object', {
#             'object': obj
#         })