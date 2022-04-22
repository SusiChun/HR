# -*- coding: utf-8 -*-
{
    'name': 'Multiple Discounts on Sale',
    'author': 'Almighty Consulting Services',
    'category': 'Sales Management',
    'summary': 'Multiple Discounts in Sale',
    'description': """Multiple Discounts in Sale
    Multi discount
    Multi discounts
    Multiple Discount
    Discount on discount
    Multiple Discounts in Sale
    Sale Multiple Discounts
    Purchase Multiple Discounts
    """,
    'website': 'http://www.almightycs.com',
    'version': '1.0',
    'sequence': 1,
    'depends': ['sale','account'],
    'data': [
        'views/sale_view.xml',
        'views/report_saleorder.xml',
    ],
    'images': [
        'static/description/almightycs_multiple_disocunts_cover.jpg',
    ],
    'installable': True,
    'price': 20,
    'currency': 'EUR',
}