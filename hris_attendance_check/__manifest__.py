# -*- coding: utf-8 -*-
{
    'name': "HRIS Attendance Check",

    'summary': """
        Module for check employee attendance""",

    'description': """
        Long description of module's purpose
    """,

    'author': "MJT",
    'website': "www.metrocom.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance', 'hr', 'attendance_regularization'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/attendance_views.xml',
        'wizard/attendance_wiz_view.xml',
    ],
    # only loaded in demonstration mode

}