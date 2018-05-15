from odoo import models, fields, api
from odoo.exceptions import UserError, AccessError

class resusers(models.Model):
    _inherit = 'res.users'
    
    @api.model
    def create(self,  vals):
        res = super(resusers, self).create(vals)
        if res.partner_id:
            res.partner_id.customer = False
        return res
