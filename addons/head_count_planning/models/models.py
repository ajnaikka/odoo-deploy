# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HeadCountPlanning(models.Model):
    _name = 'head.count.planning'
    _description = 'Yearly head count planning'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(copy=False, required=True, default="/", index='trigram')
    department_id = fields.Many2one('hr.department', "Requesting Department", required=True,
                                    domain="[('company_id', 'in', (False, company_id))]")
    year = fields.Char(string="Year", required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Requestor User', index=True, tracking=True,
                              default=lambda self: self.env.user, check_company=True)
    planning_line_ids = fields.One2many('head.count.planning.lines', 'head_count_planning_id',
                                        string="Lines", copy=True, auto_join=True)

    hr_signature = fields.Image(string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    hr_signed_by = fields.Many2one('res.users', string="Signed By", copy=False,
                                   domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    hr_signed_on = fields.Date(string="Signed On", copy=False)

    department_manager_signature = fields.Image(string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    department_manager_signed_by = fields.Many2one(
        'res.users', string="Signed By", copy=False,
        domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    department_manager_signed_on = fields.Date(string="Signed On", copy=False)

    ceo_signature = fields.Image(string="Signature", copy=False, attachment=True, max_width=1024, max_height=1024)
    ceo_signed_by = fields.Many2one('res.users', string="Signed By", copy=False,
                                   domain="[('company_id', 'in', (False, company_id)), ('employee_ids', '!=', False)]")
    ceo_signed_on = fields.Date(string="Signed On", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code("head.count.planning") or "/"
        return super().create(vals_list)


class HeadCountPlanningLines(models.Model):
    _name = 'head.count.planning.lines'
    _description = 'Head count planning lines'
    _order = 'head_count_planning_id, id'

    head_count_planning_id = fields.Many2one('head.count.planning', string='Head Count Planning Reference',
                                             index=True, required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', related='head_count_planning_id.company_id',
                                 string='Company', store=True, readonly=True)
    user_id = fields.Many2one('res.users', related='head_count_planning_id.user_id',  string='User',
                              store=True, readonly=True)
    job_position_id = fields.Many2one('hr.job', string="Job Title", required=True,
                                      domain="[('company_id', 'in', (False, company_id))]")
    existing_no_of_employees = fields.Integer()
    no_of_vacancies = fields.Integer()
    justification = fields.Text()
    status = fields.Selection([('transfer', 'Transfer'), ('promotion', 'Promotion'), ('recruitment', 'Recruitment')])
    Joining_month = fields.Selection([
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'),
        ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')],
        string="Joining Month(Expected)")
