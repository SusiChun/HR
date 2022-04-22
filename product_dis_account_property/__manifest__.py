# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'Product Discount Account Property',
    'version': '1.0',
    'category': 'account',
    'summary':'Set Income and Expense Property for Discount',
    'description': 'This module allows you to set income and expense property product vice for dicount accounting entries.',
    'author': 'VperfectCS',
    'website': 'http://www.vperfectcs.com',
    'depends': ['sale'],
    'data': [
            'data/property_data.xml',
            'views/product_view.xml',
            'views/invoice_view.xml'
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'price': 99.0,
    'currency': 'USD',
    'license': 'Other proprietary',
    'images':[
        'static/description/1.jpg',
        'static/description/2.jpg',
        'static/description/3.jpg',
    ],
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
