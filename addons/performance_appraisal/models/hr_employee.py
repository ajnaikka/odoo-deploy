# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    performance_appraisal_ids = fields.One2many('performance.appraisal', 'employee_id')

