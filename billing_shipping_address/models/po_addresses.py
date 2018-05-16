from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    partner_bill_to_id = fields.Many2one(
        'res.partner', string='Billing Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help="Invoice address for current purchase order.",
        domain=lambda self: [('type','in',['invoice']),('parent_id', '=', self.env.user.company_id.partner_id.id)]
    )
    
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Shipping Address',
        readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help="Delivery address for current purchase order.",
        domain=lambda self: [('type','in',['delivery']),('parent_id', '=', self.env.user.company_id.partner_id.id)]
    )
    
#     partner_shipping_id = fields.Many2one(
#         'stock.location', string='Shipping Address',
#         readonly=True, required=True,
#         states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
#         help="Delivery address for current purchase order."
#     )

    @api.onchange('partner_id')
    def onchange_partner_id_warning(self):
        res = super(PurchaseOrder, self).onchange_partner_id_warning()
        if not self.partner_id:
            return res
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        self.partner_bill_to_id = addr['invoice']
        return res


# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'
# 
#     @api.model
#     def default_get(self,default_fields):
#         """ Compute default partner_id field.
#         """
#         res = super(AccountInvoice, self).default_get(default_fields)
#         if 'purchase_id' in res:
#             res['partner_id'] = self.env['purchase.order'].browse(res['purchase_id']).partner_bill_to_id.id
#         return res


# class StockPicking(models.Model):
#     _inherit = 'stock.picking'

    # @api.model
    # def default_get(self, default_fields):
    #     """ Compute default partner_id field.
    #     """
    #     res = super(StockPicking, self).default_get(default_fields)
    #     picking_type_id = False
    #     if res.get('picking_type_id', False):
    #         picking_type_id = self.env['stock.picking.type'].browse(res.get('picking_type_id'))
    #     if 'origin' in res and picking_type_id and picking_type_id.code == 'incoming' and res.get('origin'):
    #         purchase_order = self.env['purchase.order'].search(
    #             [('name', '=', vals['origin'])])
    #         if purchase_order and purchase_order.partner_shipping_id:
    #             res['partner_id'] = purchase_order.partner_shipping_id.id
    #     return res

#     @api.model
#     def create(self, vals):
#         picking_type_id = False
#         if vals.get('picking_type_id', False):
#             picking_type_id = self.env['stock.picking.type'].browse(vals.get('picking_type_id'))
#         if 'origin' in vals and picking_type_id and picking_type_id.code == 'incoming' and vals.get('origin'):
#             purchase_order = self.env['purchase.order'].search(
#                 [('name', '=', vals['origin'])])
#             if purchase_order and purchase_order.partner_shipping_id:
#                 vals['location_dest_id'] = purchase_order.partner_shipping_id.id
#         res = super(StockPicking, self).create(vals)
#         return res

