# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseAgreement(models.Model):
    _inherit = 'purchase.requisition'

    name = fields.Char(string='TENDERING', required=False, copy=False, default='New')

    @api.model
    def create(self, vals):
        vals.update({
            'name': self.env['ir.sequence'].next_by_code('purchase.order.requisition')
        })
        res = super(PurchaseAgreement, self).create(vals)
        return res
