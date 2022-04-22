# -*- coding: utf-8 -*-
from odoo import http

# class BrtInheritHoliday(http.Controller):
#     @http.route('/brt_inherit_holiday/brt_inherit_holiday/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brt_inherit_holiday/brt_inherit_holiday/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brt_inherit_holiday.listing', {
#             'root': '/brt_inherit_holiday/brt_inherit_holiday',
#             'objects': http.request.env['brt_inherit_holiday.brt_inherit_holiday'].search([]),
#         })

#     @http.route('/brt_inherit_holiday/brt_inherit_holiday/objects/<model("brt_inherit_holiday.brt_inherit_holiday"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brt_inherit_holiday.object', {
#             'object': obj
#         })