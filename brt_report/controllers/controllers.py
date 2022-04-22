# -*- coding: utf-8 -*-
from odoo import http

# class BrtReport(http.Controller):
#     @http.route('/brt_report/brt_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_report/brt_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_report.listing', {
#             'root': '/brt_report/brt_report',
#             'objects': http.request.env['brt_report.brt_report'].search([]),
#         })

#     @http.route('/brt_report/brt_report/objects/<model("brt_report.brt_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_report.object', {
#             'object': obj
#         })