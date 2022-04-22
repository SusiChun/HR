# -*- coding: utf-8 -*-
{
    'name': "BRT Report HIRS",

    'summary': """
       Module Report HIRS""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Brata Bayu S",
    'website': "https://www.linkedin.com/in/brata-bayu-069829a8/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/btn_cetak_kontrak.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

