# -*- coding: utf-8 -*-
from odoo import http

# class BrtHealthReimburse(http.Controller):
#     @http.route('/brt_health_reimburse/brt_health_reimburse/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_health_reimburse/brt_health_reimburse/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_health_reimburse.listing', {
#             'root': '/brt_health_reimburse/brt_health_reimburse',
#             'objects': http.request.env['brt_health_reimburse.brt_health_reimburse'].search([]),
#         })

#     @http.route('/brt_health_reimburse/brt_health_reimburse/objects/<model("brt_health_reimburse.brt_health_reimburse"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_health_reimburse.object', {
#             'object': obj
#         })