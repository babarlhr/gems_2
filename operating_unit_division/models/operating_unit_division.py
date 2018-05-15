# -*- coding: utf-8 -*-
from odoo import fields, models, _


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    division_id = fields.Many2one(
        'operating.unit.division',
        string='Division', required=True)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit')


class OperatingUnitDivision(models.Model):
    _name = 'operating.unit.division'
    _description = 'Operating Unit Division'

    name = fields.Char('Name', required=True)
    description = fields.Char(string=_('Description'))

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env.user.company_id.id
    )

    _sql_constraints = [
        ('name_company_uniq', 'unique (name,company_id)',
         'The name of the operating unit division must '
         'be unique per company!')
    ]
