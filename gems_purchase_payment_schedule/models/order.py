from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError



class PurchasePaymentSchedule(models.Model):
    _name = 'purchase.payment.schedule'

    name = fields.Char(string="Description", required=True)
    date = fields.Date(string="Date")
    percentage = fields.Float(string="Percentage (%)", required=True)
    order_id = fields.Many2one("purchase.order", string="Order", required=True)

    @api.model
    def create(self, vals):
        res = super(PurchasePaymentSchedule, self).create(vals)
        total_percent = 0
        if vals.get('order_id', False):
            lines = self.search([('order_id', '=', vals.get('order_id'))])
            for line in lines:
                total_percent += line.percentage
            if total_percent != 100 and not total_percent < 100:
                raise UserError(" Please check total payment schedule always less than or equal to 100%.")
            res.order_id.update_on = fields.datetime.now()
            res.order_id.update_by = self.env.user.id
        return res

    @api.multi
    def write(self, vals):
        res = super(PurchasePaymentSchedule, self).write(vals)
        for rec in self:
            total_percent = 0
            if vals.get('order_id', False) or rec.order_id:
                order_id = vals.get('order_id', rec.order_id.id)
                lines = self.search([('order_id', '=', order_id)])
                for line in lines:
                    total_percent += line.percentage
                if total_percent != 100 and not total_percent < 100:
                    raise UserError(" Please check total payment schedule always less than or equal to 100%.")
            rec.order_id.update_on = fields.datetime.now()
            rec.order_id.update_by = self.env.user.id
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    payment_schedule_ids = fields.One2many(
        "purchase.payment.schedule",
        "order_id",
        string="Payment Schedule",
        track_visibility='always',
    )
    update_on = fields.Datetime("Last Updated On")
    update_by = fields.Many2one("res.users", "Last Updated By")
