# -*- coding: utf-8 -*-

{
    "name" : "Indonesia HR Management",
    "version" : "1.0",
    "author" :"Serpent Consulting Services Pvt. Ltd.",
    "category": "Human Resources",
    "description" :
    '''
    This module manage Employees details.
    ''',
    "depends" : [
                 "hr_recruitment" , "hr_contract", 'board',"hr","base","hr_payroll","hr_timesheet_sheet","hr_employee_loan"],
    "init_xml": [],
    "data": [
        "data/sequence.xml",
        "data/data.xml",
        "data/status_scheduler.xml",
        "data/mail_template.xml",
        "security/group.xml",
        "views/hr_employee_view.xml",
        "views/board_hr_employee_view.xml",
        "views/hr_contract_view.xml",
        "security/ir.model.access.csv",
        "report/employee_info_report.xml",
        "report/hr_report_menu.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    'price': 25,
    'currency': 'EUR',
}
