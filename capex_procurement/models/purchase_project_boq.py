# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.addons import decimal_precision as dp


class PurchaseProjectBoq(models.Model):
    _name = 'purchase.project.boq'
    _description = 'BOQ'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    @api.multi
    @api.depends('rfq_ids')
    def _get_total_rfq(self):
        for rec in self:
            rec.total_rfq = rec.rfq_ids and len(rec.rfq_ids) or 0

    # ------------------------------------------------------------------
    # Inverse Methods
    # ------------------------------------------------------------------

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
            responsible_id = self.boq_incharge_id or self.boq_manager_id or self.create_uid
            approval_name = responsible_id.partner_id
        if responsible_id:
            model_id = self.env.ref('capex_procurement.model_purchase_project_boq').id
            if approval_type:
                approval_user_name = _('<a href="#" data-oe-id="%s" data-oe-model="res.partner">%s</a>') % (approval_name.id, approval_name.name)
                message = _('BOQ "%s" is waiting for %s approval from %s .') % (self.name, approval_type, approval_user_name)
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
                #activity._onchange_activity_type_id()

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
            # -- BOQ INCHARGE
            if project.boq_incharge_id:
                partner_ids.append(project.boq_incharge_id.partner_id.id)
            # -- BOQ MANAGER
            if project.boq_manager_id:
                partner_ids.append(project.boq_incharge_id.partner_id.id)

            partner_ids = list(set(partner_ids))
            project.message_subscribe(partner_ids=partner_ids)

    def _inverse_operating_unit_id(self):
        # purchase_projects = self.env['purchase.project'].sudo()
        for project in self:
            project.operating_unit_div_id = project.operating_unit_id.division_id
            project.company_id = project.operating_unit_id.company_id

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

    name = fields.Char('BOQ Title', required=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')],
        string="Priority", help='Gives the sequence order when displaying a list of documents.'
    )

    boq_type = fields.Char('Type')
    project_id = fields.Many2one('purchase.project', 'Capex Project', required=True)
    create_uid = fields.Many2one('res.users', string='BOQ Created By', readonly=True)
    boq_manager_id = fields.Many2one('res.users', string='BOQ Manager')
    boq_incharge_id = fields.Many2one('res.users', string='BOQ Incharge')
    create_date = fields.Date(string="Date of Origination", default=fields.datetime.now().date())
    approved_date = fields.Date(string="Date of Approval for issue")

    boq_line_ids = fields.One2many("purchase.project.boq.line", "boq_id", "Products")
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda self: self.env.user.company_id.id
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('technical_approval', 'Technical Approval'),
        ('commercial_approval', 'Commercial Approval'),
        ('finance_approval', 'Finance Approval'),
        ('management_approval', 'management Approval'),
        ('done', 'Done'),
    ], string="State", inverse='_inverse_send_notification_approve')
    # -- Approval Managers
    technical_manager = fields.Many2one(
        'res.users', string='Technical approval by:',
        inverse="_inverse_approval_by_group", domain="[('share','=',False)]", required=True,
        
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
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_operating_unit_id"
    )
    operating_unit_div_id = fields.Many2one(
        'operating.unit.division', string='Division'
    )
    # -- Approval Updates Dates
    technical_approved_date = fields.Datetime(string="Technicaly Approved Date")
    commercial_approved_date = fields.Datetime(string="Commercial Approved Date")
    financial_approved_date = fields.Datetime(string="Financial Approved Date")
    management_approved_date = fields.Datetime(string="Management Approved Date")

    # -- Approval States
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
    total_rfq = fields.Integer(string="Total Tender", compute="_get_total_rfq")
    rfq_ids = fields.One2many("purchase.requisition", "boq_id", string="Tender")

    is_tec_manager = fields.Boolean(compute='_compute_is_manager')
    is_com_manager = fields.Boolean(compute='_compute_is_manager')
    is_fin_manager = fields.Boolean(compute='_compute_is_manager')
    is_mgt_manager = fields.Boolean(compute='_compute_is_manager')
    comments = fields.Text("Comments")


    @api.multi
    def set_state_hold(self):
        active_model = 'purchase.project.boq'
        boq_id = self
        approval_type = None
        state_type = 'On Hold'
        if boq_id:
            if boq_id.state == 'technical_approval':
                approval_type = 'Technical'
                boq_id.write({
                    'technical_state': 'hold',
                    'technical_approved_date': datetime.now()
                })
            elif boq_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                boq_id.write({
                    'commercial_state': 'hold',
                    'commercial_approved_date': datetime.now()
                })
            elif boq_id.state == 'finance_approval':
                approval_type = 'Financial'
                boq_id.write({
                    'financial_state': 'hold',
                    'financial_approved_date': datetime.now()
                })
            elif boq_id.state == 'management_approval':
                approval_type = 'Mannagement'
                boq_id.write({
                    'management_state': 'hold',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                boq_id._description,
                boq_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            boq_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            boq_id.comments = ''

    @api.multi
    def set_state_cancel(self):
        active_model = 'purchase.project.boq'
        boq_id = self
        approval_type = None
        state_type = 'Rejected'
        if boq_id:
            if boq_id.state == 'technical_approval':
                approval_type = 'Technical'
                boq_id.write({
                    'technical_state': 'cancelled',
                    'technical_approved_date': datetime.now()
                })
            elif boq_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                boq_id.write({
                    'commercial_state': 'cancelled',
                    'commercial_approved_date': datetime.now()
                })
            elif boq_id.state == 'finance_approval':
                approval_type = 'Financial'
                boq_id.write({
                    'financial_state': 'cancelled',
                    'financial_approved_date': datetime.now()
                })
            elif boq_id.state == 'management_approval':
                approval_type = 'Management'
                boq_id.write({
                    'management_state': 'cancelled',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                boq_id._description,
                boq_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            boq_id.message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            boq_id.comments = ''

    @api.multi
    def set_state_approved(self):
        active_model = 'purchase.project.boq'
        boq_id = self
        approval_type = None
        state_type = 'Approved'
        # approval_name = ''
        if boq_id:
            if boq_id.state == 'technical_approval':
                approval_type = 'Technical'
                # if project_id.commersial_manager:
                    # approval_name = project_id.commersial_manager.partner_id.name
                boq_id.sudo().write({
                    'state': 'commercial_approval',
                    'technical_state': 'done',
                    'technical_approved_date': datetime.now()
                })
            elif boq_id.state == 'commercial_approval':
                approval_type = 'Commercial'
                # if project_id.financial_manager:
                    # approval_name = project_id.financial_manager.partner_id.name
                boq_id.sudo().write({
                    'state': 'finance_approval',
                    'commercial_state': 'done',
                    'commercial_approved_date': datetime.now()
                })
            elif boq_id.state == 'finance_approval':
                approval_type = 'Financial'
                # if project_id.management_manager:
                    # approval_name = project_id.management_manager.partner_id.name
                boq_id.sudo().write({
                    'state': 'management_approval',
                    'financial_state': 'done',
                    'financial_approved_date': datetime.now()
                })
            elif boq_id.state == 'management_approval':
                approval_type = 'Management'
                # approval_name = ''
                boq_id.sudo().write({
                    'state': 'done',
                    'management_state': 'done',
                    'management_approved_date': datetime.now()
                })
            message = '%s "%s" is updated for %s approval with %s state ' % (
                boq_id._description,
                boq_id.name,
                approval_type,
                state_type
            )
            if self.comments:
                name = self.comments and self.comments.strip()
                message += "with bellow comments<br/>%s " % (name)
            boq_id.sudo().message_post(
                body=message,
                subtype='mail.mt_comment',
                message_type="notification"
            )
            boq_id.comments = ''

    @api.model
    def create(self, vals):
        res = super(PurchaseProjectBoq, self).create(vals)
        if 'project_id' in vals:
            project_id = self.env['purchase.project'].browse(vals['project_id'])
            res.operating_unit_id = project_id.operating_unit_id
            res.operating_unit_div_id =  project_id.operating_unit_div_id
        res.state = 'draft'
        return res

    @api.multi
    def write(self, vals):
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
                model_id = self.env.ref('capex_procurement.model_purchase_project_boq').id
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
        return super(PurchaseProjectBoq, self).write(vals)

    @api.multi
    def request_next_approval(self):
        for project in self:
            if project.state == 'draft':
                project.write({
                    'state': 'technical_approval',
                })
        return True

    @api.multi
    def create_rfq(self):
        for rec in self:
            context = {
                'default_boq_id': rec.id,
                'default_project_id': rec.project_id.id,
            }
            action = {
                'name': _('Tender'),
                'res_model': 'purchase.requisition',
                'type': 'ir.actions.act_window',
                'domain': [('boq_id', '=', rec.id)],
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
                        ).id, 'list'),
                        (self.env.ref(
                            'purchase_requisition.view_purchase_requisition_form'
                        ).id, 'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action


class PurchaseProjectBoqProduct(models.Model):
    _name = 'purchase.project.boq.line'
    _description = "BOQ Products"
    
    @api.multi
    def _compute_ordered_qty(self):
        for line in self:
            line.product_qty_confirmed = 0
            confirmed_po_lines = self.env['purchase.order.line'].search(
                [('boq_line_id', '=', line.id), ('state', '=', 'purchase')]
            )
            for po_line in confirmed_po_lines:
                line.product_qty_confirmed += po_line.product_qty


    product_categ_id = fields.Many2one('product.category', "Category")
    boq_id = fields.Many2one('purchase.project.boq', "BOQ", required=True)
    name = fields.Char(string='Spec.', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    po_boq_id = fields.Many2one(
        'purchase.order',
        string='PO Ref.',
    )
    product_uom = fields.Many2one(
        'product.uom',
        string='UOM',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('categ_id', '=', product_categ_id),('purchase_ok', '=', True)]",
        change_default=True,
        required=True
    )
    product_qty = fields.Float(
        string='Qty',
        #digits=dp.get_precision('Product Unit of Measure'),
        required=True
    )
    product_qty_confirmed = fields.Float(string="Ordered Qty.", compute="_compute_ordered_qty")
    company_id = fields.Many2one(
        'res.company',
        related='boq_id.company_id',
        string='Company', store=True,
        readonly=True,
    )
    supply_type = fields.Selection([
        ('comp', 'Component(s)'),
        ('unit', 'Unit(s)'),
        ('sys', 'System(s)'),
        ('other', 'Other(s)'),
        ('lot', 'Lots(s)'),
        ('cont', 'Contract(s)'),
    ], string="Supply Type")
    supply_desc = fields.Char(string='Supply Description.')

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {
            'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]
        }
        self.name = self.product_id.display_name
        if self.product_id.description_purchase:
            self.name += '\n' + self.product_id.description_purchase
        return result

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
        return super(PurchaseProjectBoqProduct, self).create(vals)

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
        return super(PurchaseProjectBoqProduct, self).write(vals)

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    # @api.multi
    # def button_confirm(self):
    #     res = super(purchase_order, self).button_confirm()
    #     # import pdb
    #     # pdb.set_trace()
    #     po_line_product_ids = []
    #     for line in self.order_line:
    #         po_line_product_ids.append(line.product_id.id)
    #     for po in self:
    #         if po.boq_id:
    #             if po.boq_id.boq_line_ids:
    #                 for boq_line in po.boq_id.boq_line_ids:
    #                     if boq_line.product_id.id in po_line_product_ids:
    #                         boq_line.po_boq_id = po.id
    #     return res
