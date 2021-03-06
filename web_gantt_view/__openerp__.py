# -*- coding: utf-8 -*-
###########################################################################
#    Copyright (C) 2017 - Today Turkesh Patel. <http://www.turkeshpatel.odoo.com>
#
#    @author Turkesh Patel (turkesh4friends@gmail.com)
##############################################################################

{
    "name": "Web Gantt View",
    "version": "1.0",
    "author": "Turkesh Patel, Odoo S.A.",
    "category": "Tools",
    'description': """Odoo Web Gantt chart view.""",
    "summary": """Odoo Web Gantt chart view.""",
    'depends': ['web'],
    'data' : [
        'views/web_gantt.xml', 
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'images': [
         'static/description/gantt_view_turkeshpatel_almihgtycs.png',
     ],
    'auto_install': True,
    'installable': True,
    "price": 18,
    "currency": "EUR",
}
