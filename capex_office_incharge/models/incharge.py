# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class OfficeIncharge(models.Model):
    _name = 'office.incharge'

    name = fields.Char(string="Name", required=True)


class PurchaseProject(models.Model):
    _inherit = 'purchase.project'

    incharge_id = fields.Many2one("office.incharge", string="Office Incharge")


class PurchaseProjectBoq(models.Model):
    _inherit = 'purchase.project.boq'

    incharge_id = fields.Many2one("office.incharge", string="Office Incharge")


    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
                rec.incharge_id = rec.project_id.incharge_id and rec.project_id.incharge_id.id or False

class PurchaseResquisition(models.Model):
    _inherit = 'purchase.requisition'

    incharge_id = fields.Many2one("office.incharge", string="Office Incharge")

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            if rec.project_id:
                rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
                rec.incharge_id = rec.project_id.incharge_id and rec.project_id.incharge_id.id or False


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    incharge_id = fields.Many2one("office.incharge", string="Office Incharge")

    @api.onchange('requisition_id')
    def onchange_requisition_id(self):
        for rec in self:
            if rec.requisition_id:
                rec.boq_id = rec.requisition_id.boq_id
                rec.project_id = rec.requisition_id.project_id
                rec.operating_unit_id = rec.requisition_id.operating_unit_id and rec.requisition_id.operating_unit_id.id or False
                rec.operating_unit_div_id = rec.requisition_id.operating_unit_id and rec.requisition_id.operating_unit_id.division_id  and rec.requisition_id.operating_unit_id.division_id.id or False
                rec.company_id = rec.requisition_id.operating_unit_id and rec.requisition_id.operating_unit_id.company_id and rec.requisition_id.operating_unit_id.company_id.id or self.env.user.company_id.id
                rec.incharge_id = rec.requisition_id.incharge_id and rec.requisition_id.incharge_id.id or False
                
    # @api.onchange('project_id')
    # def onchange_project_id(self):
    #     for rec in self:
    #         if rec.project_id:
    #             rec.operating_unit_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.id or False
    #             rec.operating_unit_div_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.division_id  and rec.project_id.operating_unit_id.division_id.id or False
    #             rec.company_id = rec.project_id.operating_unit_id and rec.project_id.operating_unit_id.company_id and rec.project_id.operating_unit_id.company_id.id or self.env.user.company_id.id
    #             rec.incharge_id = rec.project_id.incharge_id and rec.project_id.incharge_id.id or False