# -*- coding: utf-8 -*-
{
    'name': 'Multiple Discounts on Sale and Invoice',
    'author': 'Almighty Consulting Services',
    'category': 'Sales Management',
    'summary': 'Multiple Discounts in Sale and Invoice',
    'description': """Multiple Discounts in Sale and Invoice
    Multi discount
    Multi discounts
    Multiple Discount
    Discount on discount
    Multiple Discounts in Sale
    Multiple Discounts in Invoice
    Sale Multiple Discounts
    Purchase Multiple Discounts
    """,
    'website': 'http://www.almightycs.com',
    'version': '1.0',
    'sequence': 1,
    'depends': ['sale','account'],
    'data': [
        'views/sale_view.xml',
        'views/invoice_view.xml',
        'views/report_saleorder.xml',
        'views/report_invoice.xml',
    ],
    'images': [
        'static/description/almightycs_multiple_disocunts_cover.jpg',
    ],
    'installable': True,
    'price': 35,
    'currency': 'EUR',
}