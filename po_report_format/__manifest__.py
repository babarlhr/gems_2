{
    "name" : "Purchase Order Report Format",
    "description" : "Custom PO pdf report format",
    'author' : "Odoo Advantage, Ireland",
    'website' : 'erp.odoo.ie',
    'category' : 'purchase',
    'depends' : ['purchase'],
    'data' : [
                'reports/custom_po_report_template.xml',
            ],
    'installable' : True,
}