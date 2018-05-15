# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime


class HSEobservation(models.Model):
    _inherit = "hse.observation"

    @api.multi
    @api.depends('hse_obs_activity_ids')
    def _get_total_activity(self):
        for rec in self:

            rec.total_activity = rec.hse_obs_activity_ids and len(rec.hse_obs_activity_ids) or 0

    total_activity = fields.Integer(string="Total Activities", compute="_get_total_activity")
    hse_obs_activity_ids = fields.One2many(
        'mail.activity', 'observation_id', string='Activities',
        domain=['|',('active','=',False),('active','=',True)],
    )


    @api.multi
    def activity_tree_view(self):
        for rec in self:
            activity_todo_id = self.env.ref('mail.message_activity_done').id
            model_id = self.env.ref('hse_observation.model_hse_observation').id
            context = {
                'default_observation_id': rec.id,
                'default_res_model_id': model_id,
                'default_res_id': rec.id,
                'activity_type_id': activity_todo_id,
            }
            action = {
                'name': _('Activities'),
                'res_model': 'mail.activity',
                'type': 'ir.actions.act_window',
                'domain': ['|', ('active', '=', False), ('active', '=', True), ('observation_id', '=', rec.id)],
                'context': context,
            }
            if rec.total_activity <= 0:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'hse_observation.observation_mail_activity_view_tree'
                            ).id,
                        'list'),
                    ],
                })
            else:
                view_type = 'tree'
                view_mode = 'tree,form'
                action.update({
                    'views': [
                        (self.env.ref(
                                'hse_observation.observation_mail_activity_view_tree'
                            ).id,
                        'list'),
                        (self.env.ref(
                                'hse_observation.observation_mail_activity_view_form_popup'
                            ).id,
                        'form')
                    ],
                })
            action.update({
                'view_type': view_type,
                'view_mode': view_mode,
            })
            return action


class MailActivity(models.Model):
    _inherit = "mail.activity"

    observation_id = fields.Many2one("hse.observation", string="Observation", ondelete='cascade')
    active = fields.Boolean("Active", default=True)

    def action_feedback(self, feedback=False):
        observations = self.mapped('observation_id')
        res = super(MailActivity, self).action_feedback(feedback)
        if feedback:
            for observation in observations:
                description = observation.observation_msg
                description = '%s\n%s%s' % (description or '', _("Feedback: "), feedback)
                observation.write({'description': description})
        return res

    def unlink_w_meeting(self):
        observations = self.mapped('observation_id')
        res = self.unlink()
        observations.unlink()
        return res

    @api.multi
    def unlink(self):
        res = True
        self._check_access('unlink')
        for activity in self:
            if activity.date_deadline <= fields.Date.today():
                self.env['bus.bus'].sendone(
                    (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                    {'type': 'activity_updated', 'activity_deleted': True})
            if activity.observation_id:
                activity.active = False
            else:
                res = super(MailActivity, self.sudo()).unlink()
        return res

    @api.multi
    def action_reschedule_dialog(self):
        for rec in self:
            context = {
                'default_observation_id': rec.observation_id and rec.observation_id.id or False,
                'default_activity_id': rec.id,
                'default_reschedule': True
            }
            action = {
                'name': _('Feedback'),
                'res_model': 'wiz.activity',
                'type': 'ir.actions.act_window',
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'
            }
            return action

    @api.multi
    def action_mark_done(self):
        for rec in self:
            context = {
                'default_observation_id': rec.observation_id and rec.observation_id.id or False,
                'default_activity_id': rec.id,
                'default_reschedule': False
            }
            action = {
                'name': _('Feedback'),
                'res_model': 'wiz.activity',
                'type': 'ir.actions.act_window',
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'
            }
            return action