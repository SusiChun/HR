# -*- coding: utf-8 -*-
from odoo import http

# class BrtPph23(http.Controller):
#     @http.route('/brt_pph23/brt_pph23/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_pph23/brt_pph23/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_pph23.listing', {
#             'root': '/brt_pph23/brt_pph23',
#             'objects': http.request.env['brt_pph23.brt_pph23'].search([]),
#         })

#     @http.route('/brt_pph23/brt_pph23/objects/<model("brt_pph23.brt_pph23"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_pph23.object', {
#             'object': obj
#         })