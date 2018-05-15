# -*- coding: utf-8 -*-
{
    "name": "Website Supplier Portal",
    "version": "11.2018.03.24.1",
    "author": "Denero Team",
    "website": "http://www.deneroteam.com",
    "category": "purchase",
    "depends": ["website","portal", "purchase", 'capex_procurement'],
    "data": [
        "view/purchase_view.xml",
        "security/ir.model.access.csv",
        "security/purchase_security.xml"
    ],
    'demo': [
    ],
    'installable': True,
}
