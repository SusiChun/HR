# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name': "Print Account Cash Flow Statement",
    'version': '1.0',
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': """This module allow you to print Cash Flow Statement""",
    'description': """
Add the selection field for Cashflow statement like
Operational
Financial & 
Investing
CashFlow Statement
CashFlow
CashFlow Statement PDF Report
print cashflow
Account Cash Flow Statement Report
Chart of Account Configuration
Cash Flow Report
Cash Flow Statement
Cash Flow Statement Report Menu and Wizard
bi account flow cash statement
cash statement
cash flow
account flow cash
cash register
cash payment
company cash
cash management
accounting cash management
print cash flow
cash flow statement
odoo cash flow statement
account cashflow
account cash flow statement report
print cashflow report
accounting reports

Print Account Cash Flow Statement

This module allow you to print Cash Flow Statement.
This module is only compatible for Odoo COMMUNITY edition.

You have to configure on your chart of accounts with two fields:
1. Cash Flow Type and 2. Financial Report.

Cash Flow Type Options: 1. Operating Activities 2. Investing Activities 3. Financial Activities.
Financial Report Options: You have select Financial Report here which will push account to that Financial Report.

For your existing chart of accounts you have to setup above configuration by going to every accounts which should be included on Cash Flow Statement and in future if you add new account in your chart of accounts you have to set up same things.

This report is totally based on accounts you configured for Cash Flow Statement using two above new fields on account form. All accounts configured for Cash Flow will be automatically add up on respected Financial Report selected on that account. 

You can watch video demo.


account report
""",
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "www.probuse.com",
    'support': 'contact@probuse.com',
    'live_test_url': 'https://youtu.be/46J1kkwPj3E',
    'images': ['static/description/img11.jpg'],
    'category' : 'Accounting',
    'depends': ['account'],
    'data':[
        'data/account_financial_report_data.xml',
        'wizard/account_cashflow_view.xml',
        'views/report_cashflow_view.xml',
        'views/account_cashflow_view.xml',
    ],
    'installable' : True,
    'application' : False,
    'auto_install' : False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
