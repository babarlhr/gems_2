# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime


class WizPurchaseProjectPacState(models.TransientModel):
    _name = 'wiz.purchase.project.pac.state'
    _description = "Approve Capex Project PAC"

    name = fields.Char("Comments")

    @api.multi
    def set_state_hold(self):
        active_model = self._context.get('active_model', 'purchase.project.pac')
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
            project_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )

    @api.multi
    def set_state_cancel(self):
        active_model = self._context.get('active_model', 'purchase.project.pac')
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
            project_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )

    @api.multi
    def set_state_approved(self):
        active_model = self._context.get('active_model', 'purchase.project.pac')
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
            if self.name:
                name = self.name and self.name.strip()
                message += "with bellow comments<br/>%s " % (name)

            project_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )


class PurchaseProjectPac(models.Model):
    _name = 'purchase.project.pac'
    _description = 'Project PAC'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'project_id'

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '&',
                ('res_model', '=', 'purchase.project.pac'), ('res_id', '=', project.id),
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
            responsible_id = self.pac_manager or self.create_uid
            approval_name = self.pac_manager.partner_id or self.create_uid.partner_id
        if responsible_id:
            model_id = self.env.ref('capex_pac.model_purchase_project_pac').id
            if approval_type:
                approval_user_name = _('<a href="#" data-oe-id="%s" data-oe-model="res.partner">%s</a>') % (approval_name.id, approval_name.name)
                message = _('PAC "%s" is waiting for %s approval from %s .') % (self.name, approval_type, approval_user_name)
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
            if project.pac_manager:
                partner_ids.append(project.pac_manager.partner_id.id)

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

    name = fields.Char('Name')
    pac_desc = fields.Char('PAC Description')
    project_id = fields.Many2one('purchase.project', 'Capex Project', required=True)
    boq_id = fields.Many2one('purchase.project.boq', string="BOQ")
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda self: self.env.user.company_id.id
    )
    pac_incharge_id = fields.Many2one('res.users', string='PAC Incharge')
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_operating_unit_id"
    )
    operating_unit_div_id = fields.Many2one(
        'operating.unit.division', string='Division'
    )
    technical_approved_date = fields.Datetime(string="Technicaly Approved Date")
    commercial_approved_date = fields.Datetime(string="Commercial Approved Date")
    financial_approved_date = fields.Datetime(string="Financial Approved Date")
    management_approved_date = fields.Datetime(string="Management Approved Date")
    create_date = fields.Date(string="PAC Creation Date")
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
    create_uid = fields.Many2one('res.users', string='PAC Created By', readonly=True)
    pac_manager = fields.Many2one(
        'res.users', string='PAC Manager',
        inverse="_inverse_approval_by_group"
    )
    technical_manager = fields.Many2one(
        'res.users', string='Technical approval by:',
        inverse="_inverse_approval_by_group", required=True
    )
    commersial_manager = fields.Many2one(
        'res.users', string='Commercial approval by:',
        inverse="_inverse_approval_by_group", required=True
    )
    financial_manager = fields.Many2one(
        'res.users', string='Financial approval by:',
        inverse="_inverse_approval_by_group", required=True
    )
    management_manager = fields.Many2one(
        'res.users', string='Management approval by:',
        inverse="_inverse_approval_by_group", required=True
    )
    is_tec_manager = fields.Boolean(compute='_compute_is_manager')
    is_com_manager = fields.Boolean(compute='_compute_is_manager')
    is_fin_manager = fields.Boolean(compute='_compute_is_manager')
    is_mgt_manager = fields.Boolean(compute='_compute_is_manager')
    approval_date = fields.Date(string="PAC Approval Date")
    project_purpose = fields.Char('Project Purpose', placeholder="Purpose")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    comments = fields.Text("Comments")

    @api.multi
    def set_state_hold(self):
        active_model = 'purchase.project.pac'
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
        active_model = 'purchase.project.pac'
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
            if self.name:
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
        active_model = 'purchase.project.pac'
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

    @api.multi
    def request_next_approval(self):
        for project in self:
            if project.state == 'draft':
                project.write({
                    'state': 'technical_approval',
                })

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
                rec.project_purpose = rec.project_id.project_purpose or ''

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.operating_unit_div_id = rec.operating_unit_id and rec.operating_unit_id.division_id  and rec.operating_unit_id.division_id.id or False
                rec.company_id = rec.operating_unit_id and rec.operating_unit_id.company_id and rec.operating_unit_id.company_id.id or self.env.user.company_id.id


    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            '&', ('res_model', '=', 'purchase.project.pac'), ('res_id', 'in', self.ids),
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
                        Documents are attached of your PAC.</p><p>
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
        return super(PurchaseProjectPac, self).create(vals)

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
                model_id = self.env.ref('capex_pac.model_purchase_project_pac').id
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
        return super(PurchaseProjectPac, self).write(vals)


class PurchaseProject(models.Model):
    _inherit = 'purchase.project'

    @api.multi
    @api.depends('pac_ids')
    def _get_total_pac(self):
        for rec in self:
            rec.total_pac = rec.pac_ids and len(rec.pac_ids) or 0

    total_pac = fields.Integer(string="Total PAC", compute="_get_total_pac")
    pac_ids = fields.One2many("purchase.project.pac", "project_id", string="BOQ")

    @api.multi
    def create_pac(self):
        for rec in self:
            context = {
                'default_project_id': rec.id,
            }
            action = {
                'name': _('PAC'),
                'res_model': 'purchase.project.pac',
                'type': 'ir.actions.act_window',
                'domain' : [('project_id', '=', rec.id)],
                'context': context,
            }
            if rec.total_pac <= 0:
                view_type = 'form'
                view_mode = 'form'
            else:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'capex_pac.view_purchase_project_pac_tree'
                            ).id,
                        'list'),
                        (self.env.ref(
                                'capex_pac.view_purchase_project_pac_form'
                            ).id,
                        'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action


class PurchaseProjectBoq(models.Model):
    _inherit = 'purchase.project.boq'

    @api.multi
    @api.depends('pac_ids')
    def _get_total_pac(self):
        for rec in self:
            rec.total_pac = rec.pac_ids and len(rec.pac_ids) or 0

    total_pac = fields.Integer(string="Total PAC", compute="_get_total_pac")
    pac_ids = fields.One2many("purchase.project.pac", "boq_id", string="BOQ")

    @api.multi
    def create_pac(self):
        for rec in self:
            context = {
                'default_boq_id': rec.id,
                'default_project_id': rec.project_id and rec.project_id.id or False,
            }
            action = {
                'name': _('PAC'),
                'res_model': 'purchase.project.pac',
                'type': 'ir.actions.act_window',
                'domain' : [('boq_id', '=', rec.id)],
                'context': context,
            }
            if rec.total_pac <= 0:
                view_type = 'form'
                view_mode = 'form'
            else:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'capex_pac.view_purchase_project_pac_tree'
                            ).id,
                        'list'),
                        (self.env.ref(
                                'capex_pac.view_purchase_project_pac_form'
                            ).id,
                        'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action
