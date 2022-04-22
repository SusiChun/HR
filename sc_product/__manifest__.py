
{
    'name': 'Inherit Product, Purchase dan Stock',
    'version': '10.0.2.0.0',
    'summary': 'Inherit Product dan PO',
    'description': """
        Inherit Product dan PO
        """,
    'category': 'Inherit Product dan PO',
    'author': "Susi Chun",
    'depends': [
        'product','purchase','stock'
    ],
    'data': [
        'views/product_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
