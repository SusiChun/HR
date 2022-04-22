# -*- coding: utf-8 -*-
{
    'name': "BRT Product State",

    'summary': """
       Product State With Manager Confirmation""",

    'description': """
       Product State With Manager Confirmation
    """,

    'author': "Brata Bayu",
    'website': "http://prahasiber.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Product',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','purchase','purchase_request'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/res_group.xml',
        'views/inherit_product.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

