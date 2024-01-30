# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_manager_employee_id = fields.Many2one(
        comodel_name="hr.employee", related="company_id.hr_manager_employee_id",
        string="HR Manager(Employee)", readonly=False,
        domain="[('company_id', '=', company_id)]")
