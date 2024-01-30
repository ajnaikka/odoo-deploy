# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GradingStructure(models.Model):
    _name = 'grading.structure'
    _description = 'Grading Structure'

    name = fields.Char(string="Grade", required=True)
    salary_from = fields.Float('Salary From')
    salary_to = fields.Float('Salary To')
    salary_range = fields.Char('Salary Band', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    job_position_ids = fields.One2many('hr.job', 'grading_structure_id', string="Job Positions",
                                       required=True, domain="[('company_id', 'in', (False, company_id))]")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    referral_recognition_amount = fields.Monetary(currency_field="currency_id", string="Referral Bonus")



class Job(models.Model):
    _inherit = 'hr.job'

    grading_structure_id = fields.Many2one(
        'grading.structure', string="GradingStructure",
        domain="[('company_id', 'in', (False, company_id))]", ondelete='restrict')
