# -*- coding: utf-8 -*-
from odoo import http

# class BrtHirsReport(http.Controller):
#     @http.route('/brt_hirs_report/brt_hirs_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_hirs_report/brt_hirs_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_hirs_report.listing', {
#             'root': '/brt_hirs_report/brt_hirs_report',
#             'objects': http.request.env['brt_hirs_report.brt_hirs_report'].search([]),
#         })

#     @http.route('/brt_hirs_report/brt_hirs_report/objects/<model("brt_hirs_report.brt_hirs_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_hirs_report.object', {
#             'object': obj
#         })