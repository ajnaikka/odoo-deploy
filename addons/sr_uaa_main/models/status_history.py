# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _, tools


DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%d %H:%M'
DEFAULT_FACTURE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class StatusHistoryLine(models.Model):
    _name = 'status.history.line'
    _order = 'id desc'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    status_change_time = fields.Datetime('Time')
    enquiry_id = fields.Many2one('airport.enquiry')
    description = fields.Text('Description')
