# -*- coding: utf-8 -*-
from odoo import http

# class ScPos(http.Controller):
#     @http.route('/sc_pos/sc_pos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sc_pos/sc_pos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sc_pos.listing', {
#             'root': '/sc_pos/sc_pos',
#             'objects': http.request.env['sc_pos.sc_pos'].search([]),
#         })

#     @http.route('/sc_pos/sc_pos/objects/<model("sc_pos.sc_pos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sc_pos.object', {
#             'object': obj
#         })