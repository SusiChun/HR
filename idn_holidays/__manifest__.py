# -*- coding: utf-8 -*-

{
    "name" : "Indonesia Holidays Management",
    "version" : "1.0",
    "author" :"Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "Human Resources",
    "description" :
    '''
        This Moduel is used for extend leave allocation and request
        functionality.
        Module to manage leave request approval.
        Documents can attached with a leave request.
        Calculate remaining leaves and carry forward to the next year.
        Carry forwarded leaves period.
        Public holiday lists and pdf report directly emailed to employees.
    ''',
    "depends" : ["idn_employee", 'hr_holidays','brt_health_reimburse'],
    "data": [
        "security/ir.model.access.csv",
        "data/leave_data.xml",
        "data/holiday_scheduler.xml",
        "wizard/hr_refuse_leave_view.xml",
        "views/hr_year_setting_view.xml",
        "views/hr_holidays_view.xml",
        "views/board_hr_holidays_view.xml",
        "report/hr_report_menu.xml",
        "report/employee_info_report.xml",
        "report/public_holiday_report.xml"


    ],
    "installable": True,
    "auto_install": False,
    "application": False,
    'price': 25,
    'currency': 'EUR',
}
