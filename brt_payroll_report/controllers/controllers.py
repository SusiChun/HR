# -*- coding: utf-8 -*-
from odoo import http

# class BrtPayrollReport(http.Controller):
#     @http.route('/brt_payroll_report/brt_payroll_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_payroll_report/brt_payroll_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_payroll_report.listing', {
#             'root': '/brt_payroll_report/brt_payroll_report',
#             'objects': http.request.env['brt_payroll_report.brt_payroll_report'].search([]),
#         })

#     @http.route('/brt_payroll_report/brt_payroll_report/objects/<model("brt_payroll_report.brt_payroll_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_payroll_report.object', {
#             'object': obj
#         })