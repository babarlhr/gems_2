{
    'name' : 'Billing and shipping address',
    'description' : 'Billing and shipping address on PO',
    'author' : 'Odoo IE',
    "version": "11.2018.03.30.1",
    'website' : 'erp.odoo.ie',
    'category' : 'purchase',
    'data' : [
                'views/purchase_order_view.xml',
            ],
    'depends' : ['purchase', 'stock'],
    'installable' : True,
}