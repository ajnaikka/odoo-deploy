# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class JobDescription(models.Model):
    _name = 'job.description'
    _description = 'Job Description'
    _order = 'id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(copy=False, required=True, default="/", index='trigram')
    job_position_id = fields.Many2one('hr.job', string="Position", required=True,
                                      domain="[('company_id', 'in', (False, company_id))]")
    job_requisition_id = fields.Many2one(
        'job.requisition', string="Job Requisition", required=True,
        domain="[('company_id', '=', company_id), "
               "('state', 'in', ('hr_approved', 'job_description_created', 'processed'))]")
    requestor_id = fields.Many2one('hr.employee', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Requestor User', index=True, tracking=True,
                              default=lambda self: self.env.user, check_company=True)
    department_id = fields.Many2one('hr.department', "Department/ Division", required=True,
                                    domain="[('company_id', 'in', (False, company_id))]")
    grade_structure_id = fields.Many2one(
        'grading.structure', string="Grade Code", required=True,
        domain="[('company_id', 'in', (False, company_id)), ('job_position_ids', '=', job_position_id)]")
    job_code = fields.Char(string='Job Code', required=True)
    reports_to = fields.Many2one('res.users', string="Reports To", required=True,
                                 help="The position the role reports to")
    reports_in = fields.Char(string="Reports In", required=True, help="The position that reports in")
    title = fields.Char()
    type_of_position = fields.Selection(
        [('full_time', 'Full Time'), ('contractor', 'Contractor'), ('part_time', 'Part Time'), ('other', 'Other')],
        default='full_time', required=True)
    other_position = fields.Char(string="Other")
    position_summary = fields.Html(string="Position Summary", help="Should be a short narrative of the primary purpose of the role, approximately 5 to 10 lines long")
    major_responsibilities = fields.Html(string="Major Responsibilities")
    other_responsibilities = fields.Html(string="Other Responsibilities")
    other_details = fields.Html(string="Qualifications, Experience and Competencies")
    reviewed_by = fields.Many2one('res.users', string="Reviewed By")
    approved_by = fields.Many2one('res.users', string="Approved By")
    reviewed_title = fields.Char(string="Title")
    approved_title = fields.Char(string="Title")
    date_posted = fields.Date(string="Date Posted")
    date_hired = fields.Date(string="Date Hired")

    @api.constrains('company_id', 'job_requisition_id')
    def _check_requisition_uniqueness(self):
        # check for duplicates in each root company
        by_root_company = self.grouped(lambda record: record.company_id.root_id)
        by_job_requisition = []
        for root_company, records in by_root_company.items():
            grouped_by_requisition = records.grouped('job_requisition_id')
            for requisition, description in grouped_by_requisition.items():
                by_job_requisition.append(requisition.id)
            if len(by_job_requisition) < len(records):
                # retrieve duplicates within self
                duplicates = next(recs for recs in grouped_by_requisition.values() if len(recs) > 1)
            else:
                # search for duplicates of self in database
                duplicates = self.search([
                    ('company_id', 'child_of', root_company.id),
                    ('job_requisition_id', 'in', by_job_requisition),
                    ('id', 'not in', records.ids),
                ])
            if duplicates:
                raise ValidationError(
                    _("The job requisition of the job description must be unique!")
                    + "\n" + "\n".join(f"- {duplicate.job_requisition_id.name} in {duplicate.name}" for duplicate in duplicates)
                )

    @api.onchange('job_requisition_id')
    def set_job_requisition_details(self):
        self.job_position_id = self.job_requisition_id.job_position_id.id
        self.requestor_id = self.job_requisition_id.requestor_id.id
        self.department_id = self.job_requisition_id.department_id.id
        self.grade_structure_id = self.job_requisition_id.grade_structure_id.id
        self.job_code = self.job_requisition_id.job_title_code

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'job_requisition_id' in vals:
                job_requisition_id = self.env['job.requisition'].browse(vals['job_requisition_id'])
                if self.env.user.id != job_requisition_id.user_id.id:
                    raise UserError(_("Only Requester has permission to create job description"))
            vals["name"] = self.env["ir.sequence"].next_by_code("job.description") or "/"
        res = super().create(vals_list)
        for record in self:
            record.job_requisition_id.job_description_id = record.id
        return res


