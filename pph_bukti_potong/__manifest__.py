# -*- coding: utf-8 -*-
{
    'name': "PPH Bukti Potong",
    'summary': """
        PPH Bukti Potong""",
    'description': """
        PPH Bukti Potong
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
        'views/account_tax_views.xml',
        'views/partner.xml',
    ],
}