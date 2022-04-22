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

{
    "name": "Common Field Garment",
    "version": "0.6",
    "category": "Extra Tools",
    "sequence": 14,
    "author":  "vITraining",
    "website": "www.vitraining.com",
    "license": "AGPL-3",
    "summary": "",
    "description": """

    * Tambah field product category (fg,rawmat,asset,other) 
    * Tambah field type rawmate (fabric , support) 
    * Tambah master grup (import)
    * Tambah master grup jenis (import)
    * Tambah master season
    * Tambah master class
    * Tambah master cara cuci
    * Tambah master product tag
    * Menu ditambah di addons lain (MD)
    * Auto name ketika create product
    * import product category (view)
    * import partner (mitra) dan vendor

    """,
    "depends": [
        "base",
        "sale",
        "product",
        "stock",
        # "mrp",
        "hr_attendance",
        # "vit_company",

    ],
    "data": [
        # "security/ir.model.access.csv",
        "views/partner.xml",
        "views/product.xml",
        "views/stock.xml",
        "views/attendance.xml",
        "views/warehouse.xml",
        # "data/data.xml",
        #"data/account.payment.term.csv",
        #"data/res.partner.csv",
        # "data/product.attribute.csv",
        #"data/product.attribute.value.csv",
        # "data/product.group.csv",
        # "data/product.jenis.csv",
        # "data/product.class.csv",
        # "data/product.season.csv",
        # "data/product.caracuci.csv",
        #"data/stock.warehouse.csv",
        #"data/stock.location.csv", import (tarik dulu parent locationnya) manual karena location di warehouse di create otomatis
    ],


    "demo": [
    ],

    "test": [
    ],

    "installable": True,
    "auto_install": False,
    "application": True,
}
