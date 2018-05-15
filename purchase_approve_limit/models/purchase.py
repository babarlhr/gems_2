# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

from odoo.addons.purchase.models.purchase import PurchaseOrder


def button_confirm(self):
    for order in self:
        if order.state not in ['draft', 'sent', 'bid']:
            continue
        order._add_supplier_to_product()
        # Deal with double validation process
        if order.company_id.po_double_validation == 'one_step'\
            or (order.company_id.po_double_validation == 'two_step'\
                and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                :
            order.button_approve()
        else:
            order.is_app_manager = True
            order.write({'state': 'select_manager'})
    return True

PurchaseOrder.button_confirm = button_confirm


class purchase(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _check_limit(self):
        for order in self:
            if order.company_id.po_double_validation == 'one_step'\
                or (order.company_id.po_double_validation == 'two_step'\
                and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id)):
                    order.is_purchase_limit_over = False
            else:
                order.is_purchase_limit_over = True

    def _inverse_approval_by_group(self):
        for purchase_id in self:
            partner_ids = []
            # -- Commersial MANAGER
            if purchase_id.commersial_manager:
                partner_ids.append(purchase_id.commersial_manager.partner_id.id)
            # -- Financial MANAGER
            if purchase_id.financial_manager:
                partner_ids.append(purchase_id.financial_manager.partner_id.id)
            # -- Management Person
            if purchase_id.management_manager:
                partner_ids.append(purchase_id.management_manager.partner_id.id)
            # -- TECH MANAGER
            if purchase_id.technical_manager:
                partner_ids.append(purchase_id.technical_manager.partner_id.id)
            # -- PROJECT MANAGER
            if purchase_id.project_manager:
                partner_ids.append(purchase_id.project_manager.partner_id.id)

            partner_ids = list(set(partner_ids))
            purchase_id.message_subscribe(partner_ids=partner_ids)

    @api.multi
    def _compute_is_manager(self):
        cid = self.env.uid
        for obj in self:
            if obj.technical_manager.id == cid:
                obj.is_tec_manager = True
            if obj.commersial_manager.id == cid:
                obj.is_com_manager = True
            if obj.financial_manager.id == cid:
                obj.is_fin_manager = True
            if obj.management_manager.id == cid:
                obj.is_mgt_manager = True

    technical_approved_date = fields.Datetime(string="Technicaly Approved Date")
    commercial_approved_date = fields.Datetime(string="Commercial Approved Date")
    financial_approved_date = fields.Datetime(string="Financial Approved Date")
    management_approved_date = fields.Datetime(string="Management Approved Date")
    is_purchase_limit_over = fields.Boolean(compute="_check_limit")

    technical_state = fields.Selection([
        ('pending','Pending'),
        ('hold','On-Hold'),
        ('done','Approved'),
        ('cancelled','Rejected')
    ], string="State", default='pending')
    commercial_state = fields.Selection([
        ('pending','Pending'),
        ('hold','On-Hold'),
        ('done','Approved'),
        ('cancelled','Rejected')
    ], string="State", default='pending')
    financial_state = fields.Selection([
        ('pending','Pending'),
        ('hold','On-Hold'),
        ('done','Approved'),
        ('cancelled','Rejected')
    ], string="State", default='pending')
    management_state = fields.Selection([
        ('pending', 'Pending'),
        ('hold', 'On-Hold'),
        ('done','Approved'),
        ('cancelled','Rejected')
    ], string="State", default='pending')

    project_manager = fields.Many2one(
        'res.users', string='Project Manager',
        inverse="_inverse_approval_by_group"
    )
    technical_manager = fields.Many2one(
        'res.users', string='Technical approval by:',
        inverse="_inverse_approval_by_group"
    )
    commersial_manager = fields.Many2one(
        'res.users', string='Commercial approval by:',
        inverse="_inverse_approval_by_group"
    )
    financial_manager = fields.Many2one(
        'res.users', string='Financial approval by:',
        inverse="_inverse_approval_by_group"
    )
    management_manager = fields.Many2one(
        'res.users', string='Management approval by:',
        inverse="_inverse_approval_by_group"
    )

    is_tec_manager = fields.Boolean(compute='_compute_is_manager')
    is_com_manager = fields.Boolean(compute='_compute_is_manager')
    is_fin_manager = fields.Boolean(compute='_compute_is_manager')
    is_mgt_manager = fields.Boolean(compute='_compute_is_manager')
    comments = fields.Text("Comments")
    state = fields.Selection(selection_add=[
        ('select_manager', 'Approval Manager Selection'),
        ('technical_approval', 'Technical Approval'),
        ('commercial_approval', 'Commercial Approval'),
        ('finance_approval', 'Finance Approval'),
        ('management_approval', 'management Approval'),
        ], string='Status', readonly=True,
        index=True, copy=False, default='draft', track_visibility='onchange',
    )
    is_app_manager = fields.Boolean("approve managemer selection")

    @api.multi
    def remove_activity_log(self):
        for rec in self:
            approval_type = False
            if rec.state == 'technical_approval':
                approval_type = 'Technical'
            elif rec.state == 'commercial_approval':
                approval_type = 'Commercial'
            elif rec.state == 'finance_approval':
                approval_type = 'Financial'
            elif rec.state == 'management_approval':
                approval_type = 'Management'
            model_id = self.env.ref('purchase.model_purchase_order').id
            try:
                activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
            except ValueError:
                activity_type_id = False
            if approval_type:
                activity_ids = self.env['mail.activity'].search([
                    ('project_approval', '=', approval_type),
                    ('res_id', '=', rec.id),
                    ('res_model_id', '=', model_id),
                    ('activity_type_id', '=', activity_type_id)
                ])
                for activity_id in activity_ids:
                    activity_id.action_feedback()
        return True

    @api.multi
    def button_sent_to_approve(self):
        for rec in self:
            rec.write({'state': 'technical_approval'})
            rec.activity_log()
        return True

    # @api.multi
    # def button_confirm(self):
    #     for order in self:
    #         if order.state not in ['draft', 'sent']:
    #             continue
    #         order._add_supplier_to_product()
    #         # Deal with double validation process
    #         if order.company_id.po_double_validation == 'one_step'\
    #                 or (order.company_id.po_double_validation == 'two_step'\
    #                     and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
    #                 :
    #             order.button_approve()
    #         else:
    #             order.is_app_manager = True
    #             order.write({'state': 'select_manager'})
    #     return True

    @api.multi
    def set_state_hold(self):
        active_model = 'purchase.order'
        purchase_id = self
        approval_type = None
        state_type = 'On Hold'
        if purchase_id:
            if purchase_id.state == 'technical_approval':
                approval_type = 'Technical'
                purchase_id.write({
                    'technical_state': 'hold',
                    'technical_approved_date': datetime.now()
                })
            elif purchase_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                purchase_id.write({
                    'commercial_state': 'hold',
                    'commercial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'finance_approval':
                approval_type = 'Financial'
                purchase_id.write({
                    'financial_state': 'hold',
                    'financial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'management_approval':
                approval_type = 'Mannagement'
                purchase_id.write({
                    'management_state': 'hold',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                purchase_id._description,
                purchase_id.name,
                approval_type,
                state_type
            )
            if purchase_id.comments:
                name = purchase_id.comments and purchase_id.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            purchase_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            purchase_id.comments = ''

    @api.multi
    def set_state_cancel(self):
        active_model = 'purchase.order'
        purchase_id = self
        approval_type = None
        state_type = 'Rejected'
        if purchase_id:
            if purchase_id.state == 'technical_approval':
                approval_type = 'Technical'
                purchase_id.write({
                    'technical_state': 'cancelled',
                    'technical_approved_date': datetime.now()
                })
            elif purchase_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                purchase_id.write({
                    'commercial_state': 'cancelled',
                    'commercial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'finance_approval':
                approval_type = 'Financial'
                purchase_id.write({
                    'financial_state': 'cancelled',
                    'financial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'management_approval':
                approval_type = 'Management'
                purchase_id.write({
                    'management_state': 'cancelled',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                purchase_id._description,
                purchase_id.name,
                approval_type,
                state_type
            )
            if purchase_id.comments:
                name = purchase_id.comments and purchase_id.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            purchase_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            purchase_id.comments = ''

    @api.multi
    def set_state_approved(self):
        active_model = 'purchase.order'
        purchase_id = self
        approval_type = None
        state_type = 'Approved'
        if purchase_id:
            purchase_id.remove_activity_log()
            if purchase_id.state == 'technical_approval':
                approval_type = 'Technical'
                purchase_id.write({
                    'state': 'commercial_approval',
                    'technical_state': 'done',
                    'technical_approved_date': datetime.now()
                })
            elif purchase_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                purchase_id.write({
                    'state': 'finance_approval',
                    'commercial_state': 'done',
                    'commercial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'finance_approval':
                approval_type = 'Financial'
                purchase_id.write({
                    'state': 'management_approval',
                    'financial_state': 'done',
                    'financial_approved_date': datetime.now()
                })
            elif purchase_id.state == 'management_approval':
                approval_type = 'Management'
                purchase_id.button_approve()
                purchase_id.write({
                    'management_state': 'done',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                purchase_id._description,
                purchase_id.name,
                approval_type,
                state_type
            )
            if purchase_id.comments:
                name = purchase_id.comments and purchase_id.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            purchase_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            purchase_id.comments = ''
            purchase_id.activity_log()

    @api.multi
    def button_draft(self):
        res = super(purchase, self).button_draft()
        for rec in self:
            rec.is_app_manager = False
            rec.technical_approved_date = False
            rec.commercial_approved_date = False
            rec.financial_approved_date = False
            rec.management_approved_date = False
            rec.technical_state = 'pending'
            rec.commercial_state = 'pending'
            rec.financial_state = 'pending'
            rec.management_state = 'pending'
        return res

    @api.one
    def activity_log(self):
        approval_type = None
        responsible_id = None
        approval_name = None
        if self.state == 'technical_approval':
            if self.technical_manager:
                responsible_id = self.technical_manager
                approval_type = 'Technical'
                approval_name = self.technical_manager.partner_id
        elif self.state == 'commercial_approval':
            responsible_id = self.commersial_manager
            approval_type = 'Commercial'
            approval_name = self.commersial_manager.partner_id
        elif self.state == 'finance_approval':
            responsible_id = self.financial_manager
            approval_type = 'Financial'
            approval_name = self.financial_manager.partner_id
        elif self.state == 'management_approval':
            responsible_id = self.management_manager
            approval_type = 'Management'
            approval_name = self.management_manager.partner_id
        else:
            responsible_id = self.env.user
            approval_name = self.env.user.partner_id
        if responsible_id:
            model_id = self.env.ref('purchase.model_purchase_order').id
            if approval_type:
                approval_user_name = _('<a href="#" data-oe-id="%s" data-oe-model="res.partner">%s</a>') % (approval_name.id, approval_name.name)
                message = _('Order "%s" is waiting for %s approval from %s .') % (self.name, approval_type, approval_user_name)
                self.message_post(
                    body=message,
                    partner_ids=[(4, responsible_id.partner_id.id)],
                    subtype='mail.mt_comment',
                    message_type="notification"
                )
                try:
                    activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
                except ValueError:
                    activity_type_id = False
                activity = self.env['mail.activity'].create({
                    'activity_type_id': activity_type_id,
                    'note': message,
                    'user_id': responsible_id.id,
                    'res_id': self.id,
                    'res_model_id': model_id,
                    'date_deadline': datetime.now().date(),
                    'project_approval': approval_type
                })
        return True
