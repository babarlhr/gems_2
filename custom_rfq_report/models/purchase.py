# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vendor_comment = fields.Char("Vendor Comments")


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    description = fields.Html("Description")


class irsequence(models.Model):
    _inherit = 'ir.sequence'

    @api.model
    def po_change_sequence(self):
        sequence_id = self.env.ref('purchase.seq_purchase_order').id
        sequence_id = self.env['ir.sequence'].search([('id', '=', sequence_id)])
        sequence_id.write({
            'prefix': ''
        })