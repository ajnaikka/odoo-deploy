from odoo import models, fields, api


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    emp_referral = fields.Many2one('employee.referral', string="Employee Referral")

    @api.onchange('stage_id')
    def onchange_stage_id(self):
        for rec in self:
            if rec.stage_id.hired_stage:
                if rec.emp_referral:
                    rec.emp_referral.write({'state': 'hir'})


