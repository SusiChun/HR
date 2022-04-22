# -*- coding: utf-8 -*-
{
    'name': "Metrocom Accounting Custom",
    'summary': """
        Metrocom Accounting Custom""",
    'description': """
        Metrocom Accounting Custom
    """,
    'author': "Ibrahim",
    'website': "http://www.example.co.id",
	'application' : False,
    'category': 'HR',
    'version': '1.0',
    # any module necessary for this one to work correctly
    'depends': ['account'],
    # always loaded
    'data': [
        'views/account_view.xml',
    ],
}