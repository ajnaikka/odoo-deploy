# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApplicantGetRefuseReason(models.TransientModel):
    _inherit = 'applicant.get.refuse.reason'

    def action_refuse_reason_apply(self):
        super().action_refuse_reason_apply()
        applicants = self.applicant_ids.filtered(lambda x: x.partner_id)
        if applicants:
            for record in applicants:
                record.partner_id.active = False
