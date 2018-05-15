# -*- coding: utf-8 -*-
{
    "name": "CAPEx Procurement",
    "version": "11.2018.03.29.1",
    "author": "Denero Team",
    "website": "https://www.deneroteam.com",
    "category": "Project",
    "depends": ['operating_unit_division', 'product', 'purchase', 'purchase_requisition'],
    "data": [
        "views/template.xml",
        "security/capex_procurement_module_categ.xml",
        "security/capex_procurement_security.xml",
        "security/ir.model.access.csv",
        "views/purchase_project_view.xml",
        "views/purchase_project_boq_view.xml",
        "views/purchase_view.xml",
    ],
    'demo': [
    ],
    'qweb': [
        'static/src/xml/base.xml',
    ],
    'installable': True,
}
