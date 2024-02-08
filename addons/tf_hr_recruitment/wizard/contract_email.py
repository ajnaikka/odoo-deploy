# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApplicantContractEmail(models.TransientModel):
    _name = 'applicant.contract.email'
    _description = 'Applicant Contract Email'

    email_to = fields.Char(string="Email To", required=True, compute="compute_email_to", readonly=False)
    applicant_id = fields.Many2one('hr.applicant')

    @api.depends('applicant_id.email_from')
    def compute_email_to(self):
        for record in self:
            if record.applicant_id.stage_id.contract_issued_stage:
                if record.applicant_id.email_from:
                    record.email_to = record.applicant_id.email_from

    def send_email(self):
        for record in self:
            if record.applicant_id.stage_id.contract_signed_stage:
                email_template = self.env.ref('tf_hr_recruitment.applicant_contract_signed')
                email_values = {
                    'email_to': record.email_to,
                }
                email_template.send_mail(self.id, force_send=True, email_values=email_values)
            if record.applicant_id.stage_id.contract_issued_stage:
                email_template = self.env.ref('tf_hr_recruitment.applicant_contract_issued')
                email_values = {
                    'email_to': record.email_to,
                }
                email_template.send_mail(self.id, force_send=True, email_values=email_values)
