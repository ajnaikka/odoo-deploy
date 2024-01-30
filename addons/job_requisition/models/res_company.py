# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    hr_manager_employee_id = fields.Many2one(
        comodel_name="hr.employee", string="HR Manager(Employee)",
        domain="[('company_id', '=', id)]")

