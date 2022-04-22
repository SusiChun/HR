# -*- coding: utf-8 -*-
{
    'name': "HR Payroll PPH21 Payslip",
    'summary': """
        HR Payroll PPH21 Payslip""",
    'description': """
        HR Payroll PPH21 Payslip
    """,
    'author': "Ibrahim",
    'website': "http://www.example.co.id",
	'application' : False,
    'category': 'HR',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['hr_payroll','idn_payroll','hr_payroll_allowance'],
    # always loaded
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_payslip_views.xml',
    ],
}