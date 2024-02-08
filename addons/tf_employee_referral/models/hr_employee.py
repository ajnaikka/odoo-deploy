from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_referral = fields.Many2one('employee.referral', string="Employee Referral",copy=False)




