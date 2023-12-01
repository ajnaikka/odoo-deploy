from odoo import models, fields, api, _


class ResponseStatus(models.Model):
    _name = 'response.status.name'
    _description = 'Response Status'

    name = fields.Char('Name', required=True)