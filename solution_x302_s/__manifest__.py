# -*- coding: utf-8 -*-
{
    'name' : 'Attendance with fingerprint Solution X302-S',
    'version' : '10.0',
    'summary': 'Read Attendance Data from Solution X302-S',
    'sequence': 30,
    'author': 'Bima Wijaya & Dani Ramdani',
    'description': """
Syncrone fingerprint x302-s with ir cron.
    """,
    'category': 'Human resource',
    'website': '-',
    'depends' : ['hr_attendance'],
    'data': [
        'data/cron.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
