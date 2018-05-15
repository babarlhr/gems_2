# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError


class ProductTemplate(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    @api.depends('purchase_ids')
    def _get_po_line(self):
        #result = dict((tender.id, []) for tender in self)
        for element in self:
            for po in element.purchase_ids:
                element.po_line_ids += po.order_line

    po_line_ids = fields.One2many(
        'purchase.order.line',
        compute='_get_po_line',
        string="Order Lines"
    )

    @api.multi
    def cancel_unconfirmed_quotations(self):
        #cancel other orders
        for tender in self:
            for quotation in tender.purchase_ids:
                if quotation.state in ['draft', 'sent', 'bid' ,'to approve']:
                    quotation.button_cancel()
                    quotation.message_post(body=_('Cancelled by the call for tenders associated to this request for quotation.'))
        return True

    @api.multi
    def generate_po(self):
        po = self.env['purchase.order']
        # poline = self.env['purchase.order.line']
        id_per_supplier = {}

        for tender in self:
            if tender.state == 'done':
                continue

            # CHECK : atleast one line confirmed
            confirm = False
            for po_line in tender.po_line_ids:
                if po_line.quantity_tendered > 0:
                    confirm = True
                    break
            if not confirm:
                continue
            # SET : Confirmed Products by Supplier
            for po_line in tender.po_line_ids:
                if po_line.quantity_tendered > 0 and po_line.order_id.state in ['draft', 'sent', 'bid' , 'to approve']:
                    if po_line.partner_id.id in id_per_supplier:
                        id_per_supplier[po_line.partner_id.id].append(po_line)
                    else:
                        id_per_supplier[po_line.partner_id.id] = [po_line]

            # GENERATE NEW PO on SUPPLIER AND CANCELLED PREVIOUS RFQ
            for supplier, product_line in id_per_supplier.items():
                #copy a quotation for this supplier and change order_line then validate it
                rfq_id = po.search([
                    ('requisition_id', '=', tender.id),
                    ('partner_id', '=', supplier),
                    ('state', 'in', ('draft', 'sent', 'bid', 'to approve'))
                ], limit=1)
                if rfq_id:
                    new_rfq = rfq_id.copy(default={
                        'order_line': [],
                        'origin': tender.name,
                        'requisition_id': tender.id
                    })
                    for line in product_line:
                        line.copy(
                            default={'product_qty': line.quantity_tendered, 'order_id': new_rfq.id}
                        )
                    new_rfq.button_confirm()
            self.cancel_unconfirmed_quotations()
            self.action_done()


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('bid','Received Quote'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])
    received_date = fields.Datetime("Received On")
    received_count = fields.Integer("Received Version")

    @api.multi
    def button_received(self):
        if self.state in ['draft', 'sent', 'bid']:
            for line in self.order_line:
                line.product_qty = line.qty_quoted
            self.write({
                'state': 'bid',
                'received_count': self.received_count and self.received_count + 1 or 1,
                'received_date': fields.Datetime.now()
            })
        else:
            raise UserError("You cant submit bid once it is approved or canceled")
        return {}


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    quantity_tendered = fields.Float("Quantity Tenered", digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    def button_confirm(self):
        for element in self:
            self.quantity_tendered = self.product_qty

    @api.multi
    def button_cancel(self):
        for element in self:
            self.quantity_tendered = 0
