# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit'
    )
