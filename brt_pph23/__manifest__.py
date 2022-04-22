# -*- coding: utf-8 -*-
{
    'name': "Print PPh23",

    'summary': """
        Cetak PPh 23""",

    'description': """
        Cetak PPh 23
    """,

    'author': "Brata Bayu",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],
    # 'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/btn_ctk_pph23.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
