# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    observation_id = fields.Many2one('hse.observation', string="Observation")
    investigation_id = fields.Many2one('hse.observation', string="Investigation")
    further_investigation_id = fields.Many2one('hse.observation', string="Further Investigation")


class HSEObservation(models.Model):
    _name = "hse.observation"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    def _inverse_operating_unit_id(self):
        for observation in self:
            observation.company_id = observation.operating_unit_id and observation.operating_unit_id.company_id.id or self.env.user.company_id.id

    name = fields.Char(
        string="Name", readonly=True,
        required=True, copy=False, index=True, default=lambda self: _('New')
    )
    
    incident_report_desc = fields.Text('Incident Report Description')
    equipment_id = fields.Many2many('hse.equipment', 'hse_equipment_hse_observation_rel', string="Equipment Involved")
    corrective_acction = fields.Text('Corrective Action to take')
    corrective_action_further = fields.Text('Corrective Action To take')
    
    full_name_observer = fields.Char(string="Full Name of Observer")
    operating_unit_id = fields.Many2one(
        'operating.unit', string="Operating Unit", inverse="_inverse_operating_unit_id"
    )
    department_id = fields.Many2one(
        'hr.department', string='Department'
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True,
        default=lambda self: self.env.user.company_id.id
    )
    create_by = fields.Many2one(
        'res.users', string='Created By',
        default=lambda self: self.env.user.id, readonly=True
    )
    created_date_time = fields.Datetime(
        string="Created Date & Time", default=fields.datetime.now(),
        readonly=True
    )
    date_of_incident = fields.Date(string="Date of Incident")
    position = fields.Char(string="Position")
    location_on_site = fields.Char(string="Location on Site")
    equipment_involved = fields.Char(string="Equipment Involved")
    input_observation = fields.Text(string="Please input your observation in this box")
    officer_id = fields.Many2one('res.users', string='Officer')
    officer_datetime = fields.Datetime(
        string="Date & Time",
    )
    is_assign = fields.Boolean(string="Assign")
    root_cause_id = fields.One2many('hse.root.cause', 'observ_id', string='Root Cause')
    classification_id = fields.Many2one('hse.classification', string='Classification')
    risk_id = fields.Many2one('hse.risk', string='Risk Level')
    risk_level = fields.Selection([
                                ('low', 'Low'),
                                ('medium', 'Medium'),
                                ('High', 'High'),
                                ], string="Risk Level")
    initial_cause = fields.Char(string='Initial Cause')
    initial_cause_id = fields.One2many('hse.initial.cause', 'observe_id', 'Initial Cause')
    findings_investigation = fields.Text(string='Findings of investigation')
    investigation_ids = fields.One2many('hse.investigation.line', 'observation_id', 
        string='Investigation Line'
    )
    observation_msg = fields.Text("Non-Compliance Description / Observation / Opportunity for improvement")
    state = fields.Selection([
        ('draft', 'New'),
        ('initial_investigation', 'Initial Investigation'),
        ('further_investigation', 'Further Investigation'),
        ('close', 'Close')
    ], readonly=True, copy=False, index=True, track_visibility='onchange', string="State", default='draft')
    attachment_ids = fields.One2many(
        'ir.attachment', 'observation_id',
        string='Attachments'
    )
    investigation_attachment_ids = fields.One2many(
        'ir.attachment', 'investigation_id',
        string='Attachments'
    )
    
    further_investigation_attachment_ids = fields.One2many(
        'ir.attachment', 'further_investigation_id',
        string='Attachments'
    )
    
    @api.multi
    def submit_initial_investigation(self):
        for rec in self:
            rec.state = 'initial_investigation'

    @api.multi
    def submit_further_investigation(self):
        for rec in self:
            rec.state = 'further_investigation'

    @api.multi
    def click_to_close(self):
        for rec in self:
            rec.state = 'close'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('hse.observation') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('hse.observation') or _('New')
        return super(HSEObservation, self).create(vals)

    @api.multi
    def click_to_assign(self):
        for rec in self:
            rec.officer_id = self.env.user.id
            rec.is_assign = True
            rec.officer_datetime = fields.datetime.now()
    