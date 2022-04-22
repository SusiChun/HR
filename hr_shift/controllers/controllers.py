# -*- coding: utf-8 -*-
from odoo import http

# class HrShift(http.Controller):
#     @http.route('/hr_shift/hr_shift/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_shift/hr_shift/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_shift.listing', {
#             'root': '/hr_shift/hr_shift',
#             'objects': http.request.env['hr_shift.hr_shift'].search([]),
#         })

#     @http.route('/hr_shift/hr_shift/objects/<model("hr_shift.hr_shift"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_shift.object', {
#             'object': obj
#         })