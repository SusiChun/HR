# -*- coding: utf-8 -*-
##############################################################################
#
#    Spellbound soft solution.
#    Copyright (C) 2017-TODAY Spellbound soft solution(<http://www.spellboundss.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Employee Attendance Report',
    'author':'Spellbound Soft Solutions',
    'category': 'Hr_Timesheets',
    'summary': 'Employee Attendance Management',
    'website':'http://www.spellboundss.com',
    'version': '1.0',
    'description': """""",
    'depends': ['hr_timesheet_attendance','hr_timesheet_sheet','hr'],
    'images' : ['static/description/images/banner.jpg',],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_attendance.xml',
        'views/employee_attendance_report.xml',
        'views/attendance_report.xml',
        'views/excel_view.xml',
    ],

    'price':49,
    'currency':'EUR',
    'auto_install': False,
    'installable': True,	
   
}



