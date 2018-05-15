# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime


class HSEanalysis(models.Model):
    _name = "hse.analysis"

    name = fields.Char(string="Name", required=True)


class HSEClassification(models.Model):
    _name = "hse.classification"

    name = fields.Char(string="Name", required=True)


class HSERisk(models.Model):
    _name = "hse.risk"

    name = fields.Char(string="Name", required=True)
    
class HSEEquipment(models.Model):
    _name = "hse.equipment"

    name = fields.Char(string="Name", required=True)


class HSEinvestigation(models.Model):
    _name = "hse.investigation.line"

    name = fields.Many2one('hse.analysis', string="Analysis Type", required=True)
    schedule_datetime = fields.Datetime(
        string="Schedule Date & Time", default=fields.datetime.now()
    )
    assign_to = fields.Many2many('res.users', string='Assigned to')
    target_date = fields.Date(
        string="Target Completion Date"
    )
    actual_date = fields.Date(
        string="Actual Completion Date"
    )
    observation_id = fields.Many2one('hse.observation', string="Observation", required=True)
    


class HSERootcause(models.Model):
    _name = "hse.root.cause"

    observ_id = fields.Many2one('hse.observation')
    name = fields.Char(string="Name", required=True,)

class HSEInitialCause(models.Model):
    _name = "hse.initial.cause"

    observe_id = fields.Many2one('hse.observation')
    name = fields.Char(string="Name", required=True,)