# -*- coding: utf-8 -*-

from odoo import models, fields


class Job(models.Model):
    _inherit = "hr.job"

    currently_available_position = fields.Boolean(default=False, string="Currently Active Job position")

