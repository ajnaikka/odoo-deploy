from odoo import models, fields, api, _
from odoo.osv import expression


class TravelClass(models.Model):
    _name = 'travel.class'
    _description = 'Class of Travel'
    _order = 'sequence asc'

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', help='Used to sort')
