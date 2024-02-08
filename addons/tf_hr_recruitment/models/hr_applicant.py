# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Applicant(models.Model):
    _inherit = "hr.applicant"

    contract_signed_stage = fields.Boolean('Contract Signed Stage', related="stage_id.contract_signed_stage")
    contract_issued_stage = fields.Boolean('Contract Issued Stage', related="stage_id.contract_issued_stage")

    def write(self, vals):
        if vals.get('stage_id') == 6:
            if self.job_id.no_of_recruitment:
                self.job_id.no_of_recruitment = self.job_id.no_of_recruitment - 1
        super(Applicant, self).write(vals)

    def toggle_active(self):
        res = super().toggle_active()
        active_applicants = self.filtered(lambda applicant: applicant.active and applicant.partner_id)
        if active_applicants:
            for record in active_applicants:
                record.partner_id.active = True
        return res
