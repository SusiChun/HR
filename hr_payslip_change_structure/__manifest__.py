# -*- coding: utf-8 -*-
{
    'name': "HR Payroll Change Salary Structure in Payslip",
    'summary': """
        HR Payroll Change Salary Structure in Payslip""",
    'description': """
        HR Payroll Change Salary Structure in Payslip
    """,
    'support': "baimnimax@gmail.com",
    'author': "Ibrahim",
    'website': "http://www.example.co.id",
	'application' : False,
    'category': 'HR',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],
    # always loaded
    'data': [
        'views/hr_payslip_views.xml',
    ],
}