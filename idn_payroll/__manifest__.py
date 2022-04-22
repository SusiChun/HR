# -*- coding: utf-8 -*-

{
    "name": "Indonesia Payroll Management",
    "version": "1.0",
    "depends": ["idn_holidays", "hr_payroll"],
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    "category": "HR",
    "description": """
        This module manage employee's payslips.
    """,
    "init_xml": [],
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
       'data/hr_salary_rule_category_data.xml',
       'data/hr_salary_rules_data.xml',
       'data/payroll_schedule_data.xml',
       'data/payroll_sequence.xml',
       'views/hr_payroll_view.xml',
       'wizard/hr_payroll_payslips_by_employees_view.xml'

    ],
    'installable': True,
    'auto_install':False,
    'application':False,
    'price': 24,
    'currency': 'EUR',
}
