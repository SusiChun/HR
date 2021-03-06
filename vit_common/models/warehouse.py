# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _, SUPERUSER_ID


class Stock_warehouse(models.Model):
    _inherit = "stock.warehouse"

    latitude = fields.Float('Latitude',digits=(16, 6))
    longitude = fields.Float('Longitude',digits=(16, 6))
    radius = fields.Float('Radius (m)',digits=(6, 2), default=30)
    interval_checking = fields.Float('Interval Checking Location (Minutes)', help='Interval checking location untuk gps android', default=10)
    user_id = fields.Many2one('res.users','Area Manager')
    user_id2 = fields.Many2one('res.users','Area Head')
    note = fields.Text('Note')

Stock_warehouse()