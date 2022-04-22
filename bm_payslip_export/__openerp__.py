# -*- coding: utf-8 -*-

{
    "name": "Payslip Payroll Export to Excel",
    "version": "1.0",
    'depends':[
        'hr_payroll',
    ],
    "author": 'Ibrahim',
    "category": "Payroll",
    "description": """
        Module to print the reports like Payslip Export.
    """,
    "init_xml": [],
    'data': [
        'wizard/payslip_export_wizard_view.xml',
    ],
    'installable': True,
    'auto_install':False,
    'application':False,
}
