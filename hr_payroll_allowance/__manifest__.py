# -*- coding: utf-8 -*-
{
    'name': "HR Payroll Allowance",
    'summary': """
        HR Payroll Allowance""",
    'description': """
        HR Payroll Allowance
    """,
    'author': "Ibrahim",
    'website': "http://www.example.co.id",
	'application' : False,
    'category': 'HR',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','idn_payroll'],
    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'views/hr_contract_views.xml',
        'views/hr_tunjangan.xml',
    ],
}