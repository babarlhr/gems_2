# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class WizPurchaseProjectState(models.TransientModel):
    _name = 'wiz.purchase.project.state'
    _description = "Approve Capex Project"

    comments = fields.Char("Comments")

    @api.multi
    def set_state_hold(self):
        active_model = self._context.get('active_model', 'purchase.project')
        project_id = self.env[active_model].browse(
            self._context.get('active_ids', [])
        )
        approval_type = None
        state_type = 'On Hold'
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                project_id.write({
                    'technical_state': 'hold',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                project_id.write({
                    'commercial_state': 'hold',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                project_id.write({
                    'financial_state': 'hold',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Mannagement'
                project_id.write({
                    'management_state': 'hold',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.name:
                name = self.name and self.name.strip()
                message += "with bellow comments<br/>%s " % (name)
            project_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )

    @api.multi
    def set_state_cancel(self):
        active_model = self._context.get('active_model', 'purchase.project')
        project_id = self.env[active_model].browse(
            self._context.get('active_ids', [])
        )
        approval_type = None
        state_type = 'Rejected'
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                project_id.write({
                    'technical_state': 'cancelled',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                project_id.write({
                    'commercial_state': 'cancelled',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                project_id.write({
                    'financial_state': 'cancelled',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Management'
                project_id.write({
                    'management_state': 'cancelled',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.name:
                name = self.name and self.name.strip()
                message += "with bellow comments<br/>%s " % (name)
            project_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )

    @api.multi
    def set_state_approved(self):
        active_model = self._context.get('active_model', 'purchase.project')
        project_id = self.env[active_model].browse(
            self._context.get('active_ids', [])
        )
        approval_type = None
        state_type = 'Approved'
        # approval_name = ''
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                # if project_id.commersial_manager:
                    # approval_name = project_id.commersial_manager.partner_id.name
                project_id.write({
                    'state': 'commercial_approval',
                    'technical_state': 'done',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                # if project_id.financial_manager:
                    # approval_name = project_id.financial_manager.partner_id.name
                project_id.write({
                    'state': 'finance_approval',
                    'commercial_state': 'done',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                # if project_id.management_manager:
                    # approval_name = project_id.management_manager.partner_id.name
                project_id.write({
                    'state': 'management_approval',
                    'financial_state': 'done',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Management'
                # approval_name = ''
                project_id.write({
                    'state': 'done',
                    'management_state': 'done',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.name:
                name = self.name and self.name.strip()
                message += "with bellow comments<br/>%s " % (name)

            project_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )


class PurchaseProject(models.Model):
    _name = 'purchase.project'
    _description = 'Project'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.multi
    @api.depends('boq_ids')
    def _get_total_boq(self):
        for rec in self:
            rec.total_boq = rec.boq_ids and len(rec.boq_ids) or 0

    @api.multi
    @api.depends('rfq_ids')
    def _get_total_rfq(self):
        for rec in self:
            rec.total_rfq = rec.rfq_ids and len(rec.rfq_ids) or 0

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '&',
                ('res_model', '=', 'purchase.project'), ('res_id', '=', project.id),
            ])

    def _inverse_send_notification_approve(self):
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
            responsible_id = self.project_manager or self.create_uid
            approval_name = self.project_manager.partner_id or self.create_uid.partner_id
        if responsible_id:
            model_id = self.env.ref('capex_procurement.model_purchase_project').id
            if approval_type:
                approval_user_name = _('<a href="#" data-oe-id="%s" data-oe-model="res.partner">%s</a>') % (approval_name.id, approval_name.name)
                message = _('Project "%s" is waiting for %s approval from %s .') % (self.name, approval_type, approval_user_name)
                self.sudo().message_post(
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
                #activity._onchange_activity_type_id()

    def _inverse_operating_unit_id(self):
        # purchase_projects = self.env['purchase.project'].sudo()
        for project in self:
            project.operating_unit_div_id = project.operating_unit_id.division_id
            project.company_id = project.operating_unit_id.company_id

    def _inverse_approval_by_group(self):
        for project in self:
            partner_ids = []
            # -- Commersial MANAGER
            if project.commersial_manager:
                partner_ids.append(project.commersial_manager.partner_id.id)
            # -- Financial MANAGER
            if project.financial_manager:
                partner_ids.append(project.financial_manager.partner_id.id)
            # -- Management Person
            if project.management_manager:
                partner_ids.append(project.management_manager.partner_id.id)
            # -- TECH MANAGER
            if project.technical_manager:
                partner_ids.append(project.technical_manager.partner_id.id)
            # -- PROJECT MANAGER
            if project.project_manager:
                partner_ids.append(project.project_manager.partner_id.id)

            partner_ids = list(set(partner_ids))
            project.message_subscribe(partner_ids=partner_ids)

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

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        for project in self:
            project.operating_unit_div_id = project.operating_unit_id.division_id or False
            project.company_id = project.operating_unit_id.company_id or False

    name = fields.Char('Name', required=True, placeholder="e.g. Sample Project, ...")
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda self: self.env.user.company_id.id
    )
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_operating_unit_id"
    )
    operating_unit_div_id = fields.Many2one(
        'operating.unit.division', string='Division'
    )
    department_id = fields.Many2one(
        'hr.department', string='Department', required=True
    )
    technical_approved_date = fields.Datetime(string="Technicaly Approved Date")
    commercial_approved_date = fields.Datetime(string="Commercial Approved Date")
    financial_approved_date = fields.Datetime(string="Financial Approved Date")
    management_approved_date = fields.Datetime(string="Management Approved Date")

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
    state = fields.Selection([
        ('draft', 'New'),
        ('technical_approval', 'Technical Approval'),
        ('commercial_approval', 'Commercial Approval'),
        ('finance_approval', 'Finance Approval'),
        ('management_approval', 'management Approval'),
        ('done', 'Done'),
    ], string="State", inverse='_inverse_send_notification_approve')

    create_uid = fields.Many2one('res.users', string='Project Created By', readonly=True)
    project_manager = fields.Many2one(
        'res.users', string='Project Manager',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]"
    )
    technical_manager = fields.Many2one(
        'res.users', string='Technical approval by:',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]", required=True
    )
    commersial_manager = fields.Many2one(
        'res.users', string='Commercial approval by:',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]", required=True
    )
    financial_manager = fields.Many2one(
        'res.users', string='Financial approval by:',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]", required=True
    )
    management_manager = fields.Many2one(
        'res.users', string='Management approval by:',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]", required=True
    )

    is_tec_manager = fields.Boolean(compute='_compute_is_manager')
    is_com_manager = fields.Boolean(compute='_compute_is_manager')
    is_fin_manager = fields.Boolean(compute='_compute_is_manager')
    is_mgt_manager = fields.Boolean(compute='_compute_is_manager')

    approval_date = fields.Date(string="Date of Approval")
    project_start_date = fields.Date(string="Project Start Date")
    project_end_date = fields.Date(string="Project End Date")
    revised_end_date = fields.Date(string="Revised End Date")
    project_completion_date = fields.Date(string="Actual Project Completion Date")

    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    project_purpose = fields.Char('Purpose', placeholder="Project Purpose")
    approved_budget_amount = fields.Monetary(string='Approved Budget Amount')
    approved_budget_date = fields.Date(string="Approved Budget Date")
    revised_budget_amount = fields.Monetary(string='Revised Budget Amount')
    revised_budget_date = fields.Date(string="Revised Budget Date")
    total_boq = fields.Integer(string="Total BOQ", compute="_get_total_boq")
    total_rfq = fields.Integer(string="Total Tender", compute="_get_total_rfq")
    boq_ids = fields.One2many("purchase.project.boq", "project_id", string="BOQ")
    rfq_ids = fields.One2many("purchase.requisition", "project_id", string="Tender")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    comments = fields.Text("Comments")

    @api.multi
    def request_next_approval(self):
        for project in self:
            if project.state == 'draft':
                project.write({
                    'state': 'technical_approval',
                })

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            '&', ('res_model', '=', 'purchase.project'), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.model
    def create(self, vals):
        if 'operating_unit_id' in vals:
            unit_id = self.env['operating.unit'].browse(vals['operating_unit_id'])
            vals.update({
                'operating_unit_div_id': unit_id and unit_id.division_id and unit_id.division_id.id or False,
                'company_id': unit_id and unit_id.company_id and unit_id.company_id.id or self.env.user.company_id.id,
                'state': 'draft',
            })
        return super(PurchaseProject, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'operating_unit_id' in vals:
            unit_id = self.env['operating.unit'].browse(vals['operating_unit_id'])
            vals.update({
                'operating_unit_div_id': unit_id and unit_id.division_id and unit_id.division_id.id or False,
                'company_id': unit_id and unit_id.company_id and unit_id.company_id.id or self.env.user.company_id.id,
            })
        if 'state' in vals:
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
                model_id = self.env.ref('capex_procurement.model_purchase_project').id
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
        return super(PurchaseProject, self).write(vals)

    @api.multi
    def create_boq(self):
        for rec in self:
            context = {
                'default_project_id': rec.id,
            }
            action = {
                'name': _('BOQ'),
                'res_model': 'purchase.project.boq',
                'type': 'ir.actions.act_window',
                'domain' : [('project_id', '=', rec.id)],
                'context': context,
            }
            if rec.total_boq <= 0:
                view_type = 'form'
                view_mode = 'form'
            else:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'capex_procurement.view_purchase_project_boq_tree'
                            ).id,
                        'list'),
                        (self.env.ref(
                                'capex_procurement.view_purchase_project_boq_form'
                            ).id,
                        'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action

    @api.multi
    def create_rfq(self):
        for rec in self:
            context = {
                'default_project_id': rec.id,
            }
            action = {
                'name': _('Tender'),
                'res_model': 'purchase.requisition',
                'type': 'ir.actions.act_window',
                'domain': [('project_id', '=', rec.id)],
                'context': context,
            }
            if rec.total_rfq <= 0:
                view_type = 'form'
                view_mode = 'form'
            else:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'purchase_requisition.view_purchase_requisition_tree'
                            ).id,
                        'list'),
                        (self.env.ref(
                                'purchase_requisition.view_purchase_requisition_form'
                            ).id,
                        'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action

    @api.multi
    def set_state_hold(self):
        active_model = 'purchase.project'
        project_id = self
        approval_type = None
        state_type = 'On Hold'
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                project_id.write({
                    'technical_state': 'hold',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                project_id.write({
                    'commercial_state': 'hold',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                project_id.write({
                    'financial_state': 'hold',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Mannagement'
                project_id.write({
                    'management_state': 'hold',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            project_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            project_id.comments = ''

    @api.multi
    def set_state_cancel(self):
        active_model = 'purchase.project'
        project_id = self
        approval_type = None
        state_type = 'Rejected'
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                project_id.write({
                    'technical_state': 'cancelled',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                project_id.write({
                    'commercial_state': 'cancelled',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                project_id.write({
                    'financial_state': 'cancelled',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Management'
                project_id.write({
                    'management_state': 'cancelled',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            project_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            project_id.comments = ''

    @api.multi
    def set_state_approved(self):
        active_model = 'purchase.project'
        project_id = self
        approval_type = None
        state_type = 'Approved'
        # approval_name = ''
        if project_id:
            if project_id.state == 'technical_approval':
                approval_type = 'Technical'
                # if project_id.commersial_manager:
                    # approval_name = project_id.commersial_manager.partner_id.name
                project_id.sudo().write({
                    'state': 'commercial_approval',
                    'technical_state': 'done',
                    'technical_approved_date': datetime.now()
                })
            elif project_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                # if project_id.financial_manager:
                    # approval_name = project_id.financial_manager.partner_id.name
                project_id.sudo().write({
                    'state': 'finance_approval',
                    'commercial_state': 'done',
                    'commercial_approved_date': datetime.now()
                })
            elif project_id.state == 'finance_approval':
                approval_type = 'Financial'
                # if project_id.management_manager:
                    # approval_name = project_id.management_manager.partner_id.name
                project_id.sudo().write({
                    'state': 'management_approval',
                    'financial_state': 'done',
                    'financial_approved_date': datetime.now()
                })
            elif project_id.state == 'management_approval':
                approval_type = 'Management'
                # approval_name = ''
                project_id.sudo().write({
                    'state': 'done',
                    'management_state': 'done',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                project_id._description,
                project_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            project_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            project_id.comments = ''


class PurchaseAgreement(models.Model):
    _inherit = 'purchase.requisition'

    def _inverse_operating_unit_id(self):
        for project in self:
            project.operating_unit_div_id = project.operating_unit_id.division_id
            project.company_id = project.operating_unit_id.company_id

    @api.multi
    @api.depends('purchase_ids')
    def _compute_orders_number(self):
        for requisition in self:
            requisition.order_count = len(requisition.purchase_ids.filtered(lambda p: p.state not in ['purchase', 'cancel', 'done']))

    @api.multi
    @api.depends('purchase_ids')
    def _compute_orders_count(self):
        for requisition in self:
            requisition.purchase_order_count = len(requisition.purchase_ids.filtered(lambda p: p.state in ['purchase', 'done']))

    order_count = fields.Integer(compute='_compute_orders_number', string='Number of rfq')
    purchase_order_count = fields.Integer(compute='_compute_orders_count', string='Number of po')
    project_id = fields.Many2one('purchase.project', string="Project")
    title = fields.Char("Tender Title")
    boq_id = fields.Many2one('purchase.project.boq', string="BOQ")
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_operating_unit_id"
    )
    operating_unit_div_id = fields.Many2one(
        'operating.unit.division', string='Division'
    )

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.operating_unit_div_id = rec.operating_unit_id and rec.operating_unit_id.division_id  and rec.operating_unit_id.division_id.id or False
                rec.company_id = rec.operating_unit_id and rec.operating_unit_id.company_id and rec.operating_unit_id.company_id.id or self.env.user.company_id.id

    @api.onchange('boq_id')
    def onchange_boq(self):
        for rec in self:
            boq_lines = []
            if rec.boq_id and rec.boq_id.rfq_ids:
                for boq_line in rec.boq_id.boq_line_ids:
                    boq_lines.append([0, 0, {
                        'boq_id': rec.boq_id and rec.boq_id.id or False,
                        'project_id': rec.project_id and rec.project_id.id or False,
                        'product_categ_id': boq_line.product_categ_id and boq_line.product_categ_id.id or False,
                        'product_id': boq_line.product_id and boq_line.product_id.id or False,
                        'product_qty': boq_line.product_qty or 0.0,
                        'supply_type': boq_line.supply_type or False,
                        'supply_desc': boq_line.supply_desc or '',
                        'name' : boq_line.name or boq_line.product_id.name or False,
                        'product_uom_id': boq_line.product_uom and boq_line.product_uom.id or boq_line.product_id.uom_po_id or boq_line.product_id.uom_id or False,
                        'boq_line_id': boq_line.id,
                    }])
            rec['line_ids'] = boq_lines


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    product_categ_id = fields.Many2one('product.category', "Category")
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('categ_id', '=', product_categ_id),('purchase_ok', '=', True)]",
        required=True
    )
    name = fields.Char(string='Spec.', required=True)
    supply_type = fields.Selection([
        ('comp', 'Component(s)'),
        ('unit', 'Unit(s)'),
        ('sys', 'System(s)'),
        ('other', 'Other(s)'),
        ('lot', 'Lots(s)'),
        ('cont', 'Contract(s)'),
    ], string="Supply Type")
    supply_desc = fields.Char(string='Supply Description.')
    boq_line_id = fields.Many2one('purchase.project.boq.line', "Boq Product")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(PurchaseRequisitionLine, self)._onchange_product_id()
        if self.product_id and self.product_id.description_purchase:
            self.name = self.product_id.display_name + '\n ' + self.product_id.description_purchase
        return res

    @api.multi
    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLine, self)._prepare_purchase_order_line(
            name=name, product_qty=product_qty, price_unit=price_unit, taxes_ids=taxes_ids
        )
        res.update({
            'product_categ_id': self.product_categ_id and self.product_categ_id.id or False,
            'boq_line_id': self.boq_line_id and self.boq_line_id.id or False,
        })
        return res

    @api.model
    def create(self, vals):
        if vals.get('product_id', False):
            product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
            vals.update({
                'product_uom_id': (product_id.uom_po_id and product_id.uom_po_id.id) or (product_id.uom_id and product_id.uom_id.id or False)
            })
        if vals.get('product_categ_id', False):
            if vals.get('product_id', False):
                product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
                if product_id.categ_id != vals.get('product_categ_id'):
                    product_id.categ_id = int(vals.get('product_categ_id'))
        return super(PurchaseRequisitionLine, self).create(vals)

    @api.multi
    def write(self,  vals):
        for rec in self:
            if vals.get('product_id', False):
                product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
                vals.update({
                    'product_uom_id': (product_id.uom_po_id and product_id.uom_po_id.id) or (product_id.uom_id and product_id.uom_id.id or False)
                })
            if vals.get('product_categ_id', False):
                if vals.get('product_id', False) or rec.product_id:
                    product_id = vals.get('product_id', rec.product_id.id)
                    product_id = self.env['product.product'].browse([product_id])
                    if product_id.categ_id != vals.get('product_categ_id'):
                        product_id.categ_id = int(vals.get('product_categ_id'))
        return super(PurchaseRequisitionLine, self).write(vals)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

#     def _inverse_operating_unit_id(self):
#         # purchase_projects = self.env['purchase.project'].sudo()
#         for project in self:
#             project.operating_unit_div_id = project.operating_unit_id.division_id
#             project.company_id = project.operating_unit_id.company_id

    def _inverse_operating_unit_id(self):
        # purchase_projects = self.env['purchase.project'].sudo()
        for project in self:
            if project.operating_unit_id:
                project.operating_unit_div_id = project.operating_unit_id.division_id
                project.company_id = project.operating_unit_id.company_id

    project_id = fields.Many2one('purchase.project', string="Project", readonly=False)
    boq_id = fields.Many2one('purchase.project.boq', string="BOQ", readonly=True)
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_operating_unit_id", default=lambda self:self.env.user.default_operating_unit_id,
        domain=lambda self: [('id','in',[op_id.id for op_id in self.env.user.operating_unit_ids])]
    )
    operating_unit_div_id = fields.Many2one(
        'operating.unit.division', string='Division',readonly=True
    )

#     @api.model
#     def create(self, vals):
#         res = super(PurchaseOrder, self).create(vals)
#         if 'requisition_id' in vals:
#             res.boq_id = res.requisition_id.boq_id
#             res.project_id = res.requisition_id.project_id
#             res.operating_unit_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.id or False
#             res.operating_unit_div_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.division_id  and res.project_id.operating_unit_id.division_id.id or False
#             res.company_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.company_id and res.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
#         else:
#             res.company_id = self.env.user.company_id.id
#         return res

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        if 'requisition_id' in vals:
            res.boq_id = res.requisition_id.boq_id
            res.project_id = res.requisition_id.project_id
            if res.project_id:
                res.operating_unit_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.id or False
                res.operating_unit_div_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.division_id  and res.project_id.operating_unit_id.division_id.id or False
                res.company_id = res.project_id.operating_unit_id and res.project_id.operating_unit_id.company_id and res.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
        else:
            res.company_id = self.env.user.company_id.id
        return res

    @api.multi
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        if 'requisition_id' in vals:
            for rec in self:
                rec.boq_id = rec.requisition_id.boq_id
                rec.project_id = rec.requisition_id.project_id
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
        return res

#     @api.onchange('requisition_id')
#     def _onchange_requisition_id(self):
#         res = super(PurchaseOrder, self)._onchange_requisition_id()
#         self.boq_id = self.requisition_id.boq_id
#         self.project_id = self.requisition_id.project_id
#         self.operating_unit_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.id or False
#         self.operating_unit_div_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.division_id  and self.project_id.operating_unit_id.division_id.id or False
#         self.company_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.company_id and self.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
#         return res

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        res = super(PurchaseOrder, self)._onchange_requisition_id()
        if self.requisition_id:
            self.boq_id = self.requisition_id.boq_id
            self.project_id = self.requisition_id.project_id
            self.operating_unit_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.id or False
            self.operating_unit_div_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.division_id  and self.project_id.operating_unit_id.division_id.id or False
            self.company_id = self.project_id.operating_unit_id and self.project_id.operating_unit_id.company_id and self.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
        return res
        
    # @api.onchange('requisition_id')
    # def onchange_requisition_id(self):
    #     for rec in self:
    #         if rec.requisition_id:
    #             rec.boq_id = rec.requisition_id.boq_id
    #             rec.project_id = rec.requisition_id.project_id
    #             rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
    #             rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
    #             rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
                
    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.operating_unit_div_id = rec.operating_unit_id and rec.operating_unit_id.division_id  and rec.operating_unit_id.division_id.id or False
                rec.company_id = rec.operating_unit_id and rec.operating_unit_id.company_id and rec.operating_unit_id.company_id.id or False


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_categ_id = fields.Many2one('product.category', "Category")
    date_planned = fields.Datetime(
        string='Scheduled Date', required=False,
        index=True, default=fields.datetime.now()
    )
#     product_id = fields.Many2one(
#         'product.product', string='Product',
#         domain="[('categ_id', '=', product_categ_id), ('purchase_ok', '=', True)]", change_default=True, required=True
#     )
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('purchase_ok', '=', True)]", change_default=True, required=True
    )
    qty_initial = fields.Float("Qty Demand.", digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    qty_quoted = fields.Float("Qty.", digits=dp.get_precision('Product Unit of Measure'))
    boq_line_id = fields.Many2one('purchase.project.boq.line', "Boq Product", index=True)

    @api.multi
    @api.constrains('qty_quoted')
    def _check_qty(self):
        for line in self:
            if self.qty_quoted > self.qty_initial:
                raise ValidationError(_('Product might be submitted with qty actually required.'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id and self.product_id.description_purchase:
            self.name = self.product_id.display_name + '\n ' + self.product_id.description_purchase
        return res

    @api.model
    def create(self, vals):
        if vals.get('product_id', False):
            product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
            vals.update({
                'product_uom': (product_id.uom_po_id and product_id.uom_po_id.id) or (product_id.uom_id and product_id.uom_id.id or False)
            })
        if vals.get('product_categ_id', False):
            if vals.get('product_id', False):
                product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
                if product_id.categ_id != vals.get('product_categ_id'):
                    product_id.categ_id = int(vals.get('product_categ_id'))
        if vals.get('product_qty', False):
            vals.update({
                'qty_initial' : vals['product_qty'],
                'qty_quoted' : vals['product_qty'],
            })
        return super(PurchaseOrderLine, self).create(vals)

    @api.multi
    def write(self,  vals):
        for rec in self:
            if vals.get('product_id', False):
                product_id = self.env['product.product'].browse([int(vals.get('product_id'))])
                vals.update({
                    'product_uom': (product_id.uom_po_id and product_id.uom_po_id.id) or (product_id.uom_id and product_id.uom_id.id or False)
                })
            if vals.get('product_categ_id', False):
                if vals.get('product_id', False) or rec.product_id:
                    product_id = vals.get('product_id', rec.product_id.id)
                    product_id = self.env['product.product'].browse([product_id])
                    if product_id.categ_id != vals.get('product_categ_id'):
                        product_id.categ_id = int(vals.get('product_categ_id'))
        res = super(PurchaseOrderLine, self).write(vals)
