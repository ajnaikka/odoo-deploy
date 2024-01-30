# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class JobRequisition(models.Model):
    _name = 'job.requisition'
    _description = 'Job Requisition'
    _order = 'id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(copy=False, required=True, default="/", index='trigram')
    job_position_id = fields.Many2one('hr.job', string="Job Title", required=True,
                                      domain="[('company_id', 'in', (False, company_id))]")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    requestor_id = fields.Many2one('hr.employee', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Requestor User', index=True, tracking=True,
                              default=lambda self: self.env.user, check_company=True)
    department_id = fields.Many2one('hr.department', "Requesting Department", required=True,
                                    domain="[('company_id', 'in', (False, company_id))]")
    authorizing_director_id = fields.Many2one('hr.employee', string='Authorizing Director', required=True,
                                              domain="[('company_id', 'in', (False, company_id))]")
    grade_structure_id = fields.Many2one(
        'grading.structure', string="Grade", required=True,
        domain="[('company_id', 'in', (False, company_id)), ('job_position_ids', '=', job_position_id)]")
    salary_band = fields.Char('salary Band')
    date_position_became_vacant = fields.Date(required=True)
    replacement_new_post = fields.Selection(
        [('replacement', 'Replacement'), ('new_post', 'New Post')], string="Replacement/ New Post",
        required=True, default='new_post')
    leaving_employee_id = fields.Many2one('hr.employee', string="Leaver", copy=False)
    reason_for_vacancy = fields.Text(string="Reason for Vacancy")
    cost_centre = fields.Char()
    permanent_fixed_term = fields.Selection([('permanent', 'Permanent'), ('fixed', 'Fixed')],
                                            string="Permanent/Fixed Term", required=True, default="permanent")
    fixed_term_reason = fields.Text(string="Fixed Term Reason")
    fixed_term_duration = fields.Integer(string="Fixed Term Duration")

    job_title_code = fields.Char()
    hr_signature = fields.Image(string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    hr_signed_by = fields.Many2one('res.users', string="Signed By", copy=False,
                                   domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    hr_signed_on = fields.Date(string="Signed On", copy=False)
    hr_initials = fields.Char('Initials')

    department_manager_signature = fields.Image(
        string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    department_manager_signed_by = fields.Many2one(
        'res.users', string="Signed By", copy=False,
        domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    department_manager_signed_on = fields.Date(string="Signed On", copy=False)
    department_manager_initials = fields.Char('Initials')

    finance_department_signature = fields.Image(
        string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    finance_department_signed_by = fields.Many2one(
        'res.users', string="Signed By", copy=False,
        domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    finance_department_signed_on = fields.Date(string="Signed On", copy=False)
    finance_department_initials = fields.Char('Initials')

    other_signature = fields.Image(
        string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    other_signed_by = fields.Many2one('res.users', string="Signed By", copy=False,
                                      domain="[('company_id', 'in', (False, company_id))]")
    other_signed_on = fields.Date(string="Signed On", copy=False)
    other_initials = fields.Char('Initials')
    state = fields.Selection(
        [('draft', 'Draft'), ('manager_approval', 'Manager Approval'), ('manager_approved', 'Manager Approved'),
         ('hr_approval', 'HR Approval'), ('hr_approved', 'HR Approved'), ('job_description_created', 'Job Description'),
         ('processed', 'Processed'), ('rejected', 'Rejected')], default='draft', string='Status',
        readonly=True, index=True, copy=False, tracking=True)
    reason_for_rejection = fields.Text(string="Reason for Rejection")
    job_description_id = fields.Many2one(
        'job.description', string="Job Description",
        domain="[('company_id', '=', company_id), ('job_requisition_id', '=', id)]")

    @api.onchange('job_position_id')
    def set_employee_department(self):
        if self.job_position_id:
            self.department_id = self.job_position_id.department_id.id
            self.authorizing_director_id = self.department_id.manager_id.id

    @api.onchange('department_id')
    def set_authorizing_director(self):
        if self.department_id:
            self.authorizing_director_id = self.department_id.manager_id.id

    @api.onchange('grade_structure_id')
    def set_salary_band(self):
        if self.grade_structure_id:
            self.salary_band = self.grade_structure_id.salary_range

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("job.requisition") or "/"
        return super().create(vals_list)

    def write(self, vals):
        if 'department_manager_signed_by' in vals or 'department_manager_signature' in vals or 'department_manager_signed_on' in vals or 'department_manager_initials' in vals:
            if self.env.user.id != self.authorizing_director_id.user_id.id:
                raise UserError(_("Only Department Manager has permission to approve requisition"))
        if 'hr_signed_by' in vals or 'hr_signature' in vals or 'hr_signed_on' in vals or 'hr_initials' in vals or 'job_title_code' in vals:
            if self.env.user.id != self.company_id.hr_manager_employee_id.user_id.id:
                raise UserError(_("Only HR Manager has permission to approve requisition"))
        return super().write(vals)

    def get_manager_approval(self):
        for record in self:
            if self.env.user.id != record.user_id.id:
                raise UserError(_("Only Requester has permission to get approval"))
            template_id = self.env.ref('job_requisition.job_requisition_manager_approval')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'manager_approval'

    def approve_requisition(self):
        for record in self:
            if self.env.user.id != record.authorizing_director_id.user_id.id:
                raise UserError(_("Only Department Manager has permission to approve requisition."))
            if not record.department_manager_signed_by or not record.department_manager_signature or not record.department_manager_signed_on:
                raise UserError(_("Please fill the department manager authorization details."))
            record.department_manager_signed_by = record.authorizing_director_id.user_id.id
            template_id = self.env.ref('job_requisition.job_requisition_manager_approved')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'manager_approved'

    def get_hr_approval(self):
        for record in self:
            if self.env.user.id != record.user_id.id:
                raise UserError(_("Only Requester has permission to get approval"))
            template_id = self.env.ref('job_requisition.job_requisition_hr_approval')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'hr_approval'

    def hr_approve_requisition(self):
        for record in self:
            if self.env.user.id != record.company_id.hr_manager_employee_id.user_id.id:
                raise UserError(_("Only HR Manager has permission to approve requisition at this stage."))
            if not record.hr_signed_by or not record.hr_signature or not record.hr_signed_on:
                raise UserError(_("Please fill the HR manager authorization details."))
            if not record.job_title_code:
                raise UserError(_("Please enter job title code."))
            record.hr_signed_by = record.company_id.hr_manager_employee_id.user_id.id
            template_id = self.env.ref('job_requisition.job_requisition_hr_manager_approved')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'hr_approved'

    def create_job_description(self):
        for record in self:
            if self.env.user.id != record.user_id.id:
                raise UserError(_("Only Requester has permission to create job description"))
            if not record.job_description_id:
                raise UserError(_("Please create job description and assign it to requisition"))
            template_id = self.env.ref('job_requisition.job_description_created')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'job_description_created'

    def process_job_requisition(self):
        for record in self:
            if self.env.user.id != record.company_id.hr_manager_employee_id.user_id.id:
                raise UserError(_("Only HR Manager has permission to process requisition."))
            record.job_position_id.currently_available_position = True
            record.state = 'processed'
