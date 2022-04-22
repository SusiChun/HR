# -*- coding: utf-8 -*-
from odoo import http

# class AttendanceSummary(http.Controller):
#     @http.route('/attendance_summary/attendance_summary/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attendance_summary/attendance_summary/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('attendance_summary.listing', {
#             'root': '/attendance_summary/attendance_summary',
#             'objects': http.request.env['attendance_summary.attendance_summary'].search([]),
#         })

#     @http.route('/attendance_summary/attendance_summary/objects/<model("attendance_summary.attendance_summary"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attendance_summary.object', {
#             'object': obj
#         })