# -*- coding: utf-8 -*-
{
    "name": "Operating Unit Division",
    "version": "11.2018.03.13.1",
    "author": "DeneroTeam",
    "website": "https://www.deneroteam.com",
    "category": "Sales",
    "depends": ["hr", "operating_unit"],
    "data": [
        "security/ir.model.access.csv",
        "views/operating_unit_view.xml",
        "data/operating_unit_data.xml",
    ],
    'demo': [
        "demo/operating_unit_demo.xml"
    ],
    'installable': True,
}
