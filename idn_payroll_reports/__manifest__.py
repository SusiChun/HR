# -*- coding: utf-8 -*-

{
    "name": "Indonesia Payroll Reports",
    "version": "1.0",
    'depends':[
                'base', 'idn_payroll',
                ],
    "author": 'Serpent Consulting Services Pvt. Ltd.',
    "category": "HR",
    "description": """
        Module to print the reports like bank summary, payroll summary and
        upload file.
    """,
    "init_xml": [],
    'data': [
        'report/hr_bank_summary_template.xml',
        'report/cheque_summary_report_temp.xml',
        'views/report_registrations.xml',
        'views/res_bank_view.xml',
        'views/hr_employee_view.xml',
        'wizard/upload_xls_wizard_view.xml',
        'wizard/bank_summary_wirard_view.xml',
        'wizard/payroll_generic_summary_wiz_view.xml',
        'wizard/bank_transfer_request_view.xml',
        'wizard/payslip_xls_export_file_view.xml',
        "wizard/export_employee_summary_wiz_view.xml",
        'wizard/comput_confirm_payslip_wiz_view.xml'
        ],
    'installable': True,
    'auto_install':False,
    'application':False,
    'price': 24,
    'currency': 'EUR',
}
