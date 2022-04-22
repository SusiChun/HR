
{
    'name': 'Account Payment Rate',
    'version': '10.0.2.0.0',
    'summary': 'Add Field rate in Payment',
    'description': """
        Add Field rate in Payment
        """,
    'category': 'Account Payment Rate',
    'author': "Susi Chun",
    'depends': [
        'account','vit_currency_inverse_rate'
    ],
    'data': [
        'views/account_payment_view.xml',
        'views/account_invoice_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
