# -*- coding: utf-8 -*-
{
    'name': "BRT Health Reimburse",

    'summary': """
       BRT Health Reimburse""",

    'description': """
        BRT Health Reimburse
    """,

    'author': "Brata Bayu",
    'website': "https://www.linkedin.com/in/brata-bayu-069829a8/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Health Reimburse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract', 'account_accountant', 'report', 'web_tour','hr_payroll','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'security/res_group.xml',
        'views/payslip.xml',
        'views/contract.xml',
    ],
    # only loaded in demonstration mode
    "application": True,
    'demo': [
        'demo/demo.xml',
    ],
}