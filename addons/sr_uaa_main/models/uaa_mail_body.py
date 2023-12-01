from odoo import models, fields, api, _
from odoo.osv import expression


class UaaMailBody(models.Model):
    _name = 'uaa.mail.body'
    _description = 'Custom Mail Body'

    name = fields.Char('Name', required=True)
    body = fields.Html('Body Message')