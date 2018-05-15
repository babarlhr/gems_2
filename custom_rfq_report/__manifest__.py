# -*- coding: utf-8 -*-
{
    "name": "Purchase Order Custom Report",
    "description": "Custom PO QWEB report",
    "version": "11.2018.03.12.1",
    'author': "Denero Team",
    'website': 'https://www.deneroteam.com',
    'category': 'purchase',
    'depends': ['purchase', 'capex_procurement', 'operating_unit_division'],
    'data': [
        "views/po_rfq_custom_report_action.xml",
        "report/custom_purchase_order_templates.xml",
    ],
    'installable': True,
}
