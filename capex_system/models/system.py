# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Officesystem(models.Model):
    _name = 'office.system'

    name = fields.Char(string="Name", required=True)


class PurchaseProject(models.Model):
    _inherit = 'purchase.project'

    system_id = fields.Many2one("office.system", string="System")


class PurchaseProjectBoq(models.Model):
    _inherit = 'purchase.project.boq'

    system_id = fields.Many2one("office.system", string="System")


    @api.onchange('project_id')
    def onchange_project_id(self):
        res = super(PurchaseProjectBoq, self).onchange_project_id()
        for rec in self:
            if rec.project_id:
                rec.system_id = rec.project_id.system_id and rec.project_id.system_id.id or False
        return res


class PurchaseResquisition(models.Model):
    _inherit = 'purchase.requisition'

    system_id = fields.Many2one("office.system", string="System")

    @api.onchange('project_id')
    def onchange_project_id(self):
        res = super(PurchaseResquisition, self).onchange_project_id()
        for rec in self:
            if rec.project_id:
                rec.system_id = rec.project_id.system_id and rec.project_id.system_id.id or False
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    system_id = fields.Many2one("office.system", string="System")

    @api.onchange('requisition_id')
    def onchange_requisition_id(self):
        res = super(PurchaseOrder, self).onchange_requisition_id()
        for rec in self:
            if rec.requisition_id:
                rec.system_id = rec.requisition_id.system_id and rec.requisition_id.system_id.id or False
        return res

    # @api.onchange('project_id')
    # def onchange_project_id(self):
    #     res = super(PurchaseOrder, self).onchange_project_id()
    #     for rec in self:
    #         if rec.project_id:
    #             rec.system_id = rec.project_id.system_id and rec.project_id.system_id.id or False
    #     return res