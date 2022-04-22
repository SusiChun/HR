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
from odoo.exceptions import ValidationError, RedirectWarning, UserError


class ProductGroup(models.Model):
    _name = "product.group"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductGroup, self).unlink()

    name = fields.Char('Name', size=60, required=True, copy=False)
    code = fields.Char('Code', size=10, required=True, copy=False)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code duplikat !'),
    ]

ProductGroup()

class ProductJenis(models.Model):
    _name = "product.jenis"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductJenis, self).unlink()

    name = fields.Char('Name', size=60, required=True, copy=False)
    code = fields.Char('Code', size=10, required=True, copy=False)
    description = fields.Char("Description")
    group_id = fields.Many2one('product.group','Group', required=True, copy=False)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code duplikat !'),
    ]

ProductGroup()

class ProductClass(models.Model):
    _name = "product.class"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductClass, self).unlink()

    code = fields.Char("Code", required=True, copy=False)
    name = fields.Char("Name", required=True, copy=False)
    description = fields.Char("Description")
    note = fields.Char("Note")
    active = fields.Boolean("Active", default=True)

    @api.multi
    @api.depends('name', 'note')
    def name_get(self):
        result = []
        for klas in self:
            name = klas.name
            if klas.note :
                name = name +' ('+klas.note+')'
                if klas.description :
                    name = name + ' || '+klas.description
            result.append((klas.id, name))
        return result

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code duplikat !'),
    ]

ProductClass()

class ProductSeason(models.Model):
    _name = "product.season"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductSeason, self).unlink()

    @api.onchange('name')
    def _check_name(self):
        season_name = self.name
        if season_name:
            name_exist  = self.env['product.season'].sudo().search([('name','=ilike',season_name)],limit=1)
            if name_exist:
                warning_mess = {
                    'title': _('Warning!'),
                    'message' : _('Nama mirip %s sudah pernah di inputkan !') % \
                        (season_name)
                }
                return {'warning': warning_mess}
        return {}

    code = fields.Char("Code", required=True, copy=False)
    name = fields.Char("Name", required=True, copy=False)
    start_date = fields.Date("Start Date")
    note = fields.Char("Note")
    end_date = fields.Date("End Date")
    active = fields.Boolean("Active", default=True)
 
    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code duplikat !'),
    ]   

ProductSeason()

class ProductCaraCuci(models.Model):
    _name = "product.caracuci"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductCaraCuci, self).unlink()

    code = fields.Char("Code", required=True, copy=False)
    name = fields.Char("Name", required=True, copy=False)
    note = fields.Char("Note")
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Code duplikat !'),
    ]

ProductCaraCuci()

class ProductTag(models.Model):
    _name = "product.tag"

    @api.multi
    def unlink(self):
        for x in self:
            if x.active:
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus non active'))
        return super(ProductTag, self).unlink()

    name = fields.Char("Name", required=True)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Name duplikat !'),
    ]

ProductTag()
