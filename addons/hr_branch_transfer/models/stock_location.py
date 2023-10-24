# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    transfer_request_branch_id = fields.Many2one('res.branch', string="Branch for Transfer Request")

