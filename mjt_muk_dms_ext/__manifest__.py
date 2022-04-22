# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'DMS Extension',
    'version' : '1.1',
    'summary': 'Document Management System Extension',
    'sequence': 30,
    'description': """
DMS Extension
====================
Custom Model.
    """,
    'category': 'Document Management',
    'author': 'MJT',
    'website': '',
    'depends' : ['mjt_crm_ext', 'muk_dms'
        ],
    'data': [
        # 'security/res_groups.xml',
        'data/dms_data_view.xml',
        'views/dms_directory_view.xml',
        'views/dms_file_view.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
