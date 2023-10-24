# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.branch"
    branch_code = fields.Char('Branch Code')
