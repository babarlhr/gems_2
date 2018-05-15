# -*- encoding: utf-8 -*-
{
    'name': 'Bid Selection From Tender',
    "version": "11.2018.03.24.1",
    'category': 'Product Description',
    'description': '''
        This module adds new product tabs on product form
    ''',
    'author': 'DeneroTeam',
    'website': 'http://www.deneroteam.com',
    'depends': ['purchase', 'purchase_requisition'],
    'data': [
        'views/purchase_requisition_view.xml',
    ],
    'installable': True,
}
