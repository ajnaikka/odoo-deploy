# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RejectJobRequisition(models.TransientModel):
    _name = "reject.job.requisition"
    _description = "Reject Job Requisition"

    job_requisition_id = fields.Many2one(
        "job.requisition",
        required=True,
        readonly=True,
    )
    reason = fields.Text(string="Reason for Rejection")

    def reject_job_requisition(self):
        self.ensure_one()
        if self.job_requisition_id.authorizing_director_id.user_id.id != self.env.user.id:
            raise UserError(_("Only Department Manager has permission to reject requisition"))
        if not self.job_requisition_id.department_manager_signed_by or not self.job_requisition_id.department_manager_signature or not self.job_requisition_id.department_manager_signed_on:
            raise UserError(_("Please fill the department manager authorization details."))
        self.job_requisition_id.department_manager_signed_by = self.job_requisition_id.authorizing_director_id.user_id.id
        template_id = self.env.ref('job_requisition.job_requisition_manager_rejected')
        if template_id:
            template_id.send_mail(self.job_requisition_id.id, force_send=True, raise_exception=False)
        self.job_requisition_id.reason_for_rejection = self.reason
        self.job_requisition_id.state = 'rejected'
