# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'LOS CRM Extension',
    'version' : '1.1',
    'summary': 'LOS CRM Extension',
    'sequence': 30,
    'description': """
CRM Extension
====================
Custom Model.
    """,
    'category': 'crm',
    'author': 'MJT',
    'website': '',
    'depends' : ['base','crm', 'sale', 'muk_dms'
        ],
    'data': [
        # 'security/res_groups.xml',
        'views/lead_document_view.xml',
        'views/document_type_view.xml',
        'views/res_partner_view.xml',
        'views/crm_lead_view.xml',
        'views/product_template_view.xml',
        ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
