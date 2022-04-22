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


class Hr_attendance(models.Model):
    _inherit = "hr.attendance"

    latitude	= fields.Char(string="Latitude Sign In")
    longitude	= fields.Char(string="Longitude Sign In")
    latitude2	= fields.Char(string="Latitude Sign Out")
    longitude2	= fields.Char(string="Longitude Sign Out")
    warehouse_id	= fields.Many2one("stock.warehouse",string="Warehouse")
    image1 = fields.Binary("Sign In Image ", attachment=True,)
    image2 = fields.Binary("Sign Out Image ", attachment=True,)

Hr_attendance()