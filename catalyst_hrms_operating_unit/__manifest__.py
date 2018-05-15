# -*- encoding: utf-8 -*-
{
    'name': 'Catalyst HRMS Operating Unit',
    "version": "11.2018.03.13.1",
    'category': 'Hr',
    'description': '''
        This module adds new field operating unit on employee form
    ''',
    'author': 'DeneroTeam',
    'website': 'http://www.deneroteam.com',
    'depends': ['hr', 'operating_unit_division'],
    'data': [
        'views/hr_view.xml',
    ],
    'installable': True,
}
