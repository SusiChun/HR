# -*- coding: utf-8 -*-

{
    'name': 'Expense Advance Request - Employee',
    'version': '10.0',
    'license': 'Other proprietary',
    'category': 'Human Resources',
    'summary': 'Expense Advance Request - Employee + Support Return Amount',
    'description': """
        Employee Advance Expense Requests:

        Expense Advance Request - Employee

        Created Menus :

            Expenses/Expense Advances
            Expenses/Expense Advances/Expense Advance Requests
            Expenses/Expense Advances/Advance to Approve
            Expenses/Expense Advances/Advance to Pay
            Defined Reports

        Print Advance Expense
        This module allow your employees to create advance request for expenses. This module will work with multi currency.
        Note: We have not changed any accounting entries for expense or expense sheet, we are just showing advance taken for that expense by employee
        Employee advance expense
        Expense Advance Request - Employee
        advance expense
        expense request
        advance request
        accounting expense
        employee advance expense process
        director expense approval
        Employee Advance Expense Request 
        Employee Advance Expense Request PDF Report
        Employee Advance Expense Request QWEB Report
        hr employee advance
        cash advance
        expense advance
        advance form
        advance request
        advance application form
        employee advance request
        hr_expense
        hr_expense_advance
        hr_advance
        hr expense
        hr advance
        expense advance form
            """,
    'support': 'contact@probuse.com, baimnimax@gmail.com',
    'images': ['static/description/img1.jpg'],
    'author': 'Probuse Consulting Service Pvt. Ltd., Ibrahim',
    'website': 'www.probuse.com',
    'depends': ['hr_expense'],
    'live_test_url': 'https://youtu.be/Mty6cj6O6Xw',
    'data': ['security/employee_advance_expense_security.xml',
             'security/ir.model.access.csv',
             'data/expense_sequence_data.xml',
             'views/employee_advance_expense.xml',
             'views/hr_expense.xml',
             'views/advance_expense_sheet.xml',
             'views/advance_expense_line.xml',
             'report/employee_advance_expense_report.xml'
            ],
    'installable': True,
    'application': False,
}
