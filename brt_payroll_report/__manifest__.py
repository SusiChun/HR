# -*- coding: utf-8 -*-
{
    'name': "BRT Payroll Export",

    'summary': """
       Module Export PaySlip Employee""",

    'description': """
        Module Export PaySlip Employee
    """,

    'author': "Brata Bayu",
    'website': "http://bratabayu.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report','hr','hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/payslip.xml',
        'views/pdf_report.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}