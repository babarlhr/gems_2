# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.user.company_id.id)
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', inverse="_inverse_division_units", required=True
    )
    operating_division_id = fields.Many2one(
        'operating.unit.division', 'Division'
    )

    def _inverse_division_units(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.company_id = rec.operating_unit_id.company_id and rec.operating_unit_id.division_id.company_id.id or self.env.user.company_id.id
                rec.operating_division_id = rec.operating_unit_id.division_id and rec.operating_unit_id.division_id.id or False

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        for job in self:
            job.operating_division_id = job.operating_unit_id.division_id and job.operating_unit_id.division_id.id or False
            job.company_id = job.operating_unit_id.company_id and job.operating_unit_id.company_id.id or self.env.user.company_id.id
