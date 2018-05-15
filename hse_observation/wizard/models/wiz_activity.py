# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class wizactivity(models.Model):
    _name = "wiz.activity"

    reschedule = fields.Boolean("Reschedule")
    feedback = fields.Html('Feedback', required=True)
    activity_id = fields.Many2one("mail.activity", string="Activity")
    observation_id = fields.Many2one("hse.observations", string="Observation")
    date_deadline = fields.Date('Schedual Date', index=True, default=fields.Date.today)

    @api.multi
    def action_done(self):
        for rec in self:
            if rec.activity_id:
                rec.activity_id.action_feedback(feedback=rec.feedback)
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def action_reschedule(self):
        for rec in self:
            if rec.activity_id and rec.date_deadline:
                date = datetime.strptime(rec.date_deadline, DEFAULT_SERVER_DATE_FORMAT).date()
                if date >= datetime.now().date():
                    rec.activity_id.date_deadline = rec.date_deadline
                    message = self.env['mail.message']
                    if rec.feedback:
                        feedback=rec.feedback
                        rec.activity_id.write(dict(feedback=rec.feedback))
                        feedback += "Reschedual date on :- %s \n" % (date.strftime("%m/%d/%Y"))
                        record = self.env[rec.activity_id.res_model].browse(rec.activity_id.res_id)
                        record.message_post(
                            body=feedback,
                            subtype='mail.mt_comment',
                            message_type="notification"
                        )
                else:
                    raise UserError(_("Please Select date bigger then today.!"))
        return {'type': 'ir.actions.act_window_close'}