# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode


class PerformanceAppraisal(models.Model):
    _name = 'performance.appraisal'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Performance appraisal'
    _order = 'state desc, id desc'
    _rec_name = 'employee_id'
    _mail_post_access = 'read'

    def _get_default_employee(self):
        if (self.env.context.get('active_model') in
                ('hr.employee', 'hr.employee.public') and 'active_id' in self.env.context):
            return self.env.context.get('active_id')
        elif self.env.context.get('active_model') == 'res.users' and 'active_id' in self.env.context:
            return self.env['res.users'].browse(self.env.context['active_id']).employee_id
        else:
            return self.env.user.employee_id

    active = fields.Boolean(default=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True, string='Employee', index=True,
        default=_get_default_employee)
    employee_user_id = fields.Many2one('res.users', string="Employee User", related='employee_id.user_id')
    company_id = fields.Many2one('res.company', related='employee_id.company_id', store=True)
    department_id = fields.Many2one(
        'hr.department', compute='_compute_department_id', string='Department', store=True)
    job_code = fields.Char(string="Code", related='employee_id.employee_unique_id')
    job_position_id = fields.Many2one('hr.job', compute='_compute_job_position_id', string='Job Position', store=True)
    date_close = fields.Date(
        string='Appraisal Date',
        help='Date of the appraisal, automatically updated when the appraisal is Done or Cancelled.', required=True,
        index=True,
        default=lambda self: datetime.date.today() + relativedelta(months=+1))
    requested_date = fields.Date(string='Requested Date', required=True, index=True,
                                 default=lambda self: datetime.date.today())
    state = fields.Selection(
        [('new', 'Draft'),
         ('request_sent', 'Request Sent'),
         ('pending', 'Confirmed'),
         ('done', 'Done'),
         ('cancel', "Cancelled")],
        string='Status', tracking=True, required=True, copy=False,
        default='new', index=True, group_expand='_group_expand_states')
    note = fields.Html(string="Private Note", help="The content of this note is not visible by the Employee.")
    goal_setting_form_attachment_ids = fields.Many2many(
        'ir.attachment', 'appraisal_attachment_rel', 'performance_appraisal_id',
        'attachment_id', string='Goal Setting Form',)
    compensation_package_attachment_ids = fields.Many2many(
        'ir.attachment', 'appraisal_compensation_attachment_rel', 'performance_appraisal_id',
        'attachment_id', string='Compensation Package', )
    type_of_review = fields.Selection(
        [('goal', 'Goal Setting'), ('interim', 'Interim(Project)'), ('year_end', 'Year-End')],)

    @api.depends('employee_id')
    def _compute_department_id(self):
        for appraisal in self:
            if appraisal.employee_id:
                appraisal.department_id = appraisal.employee_id.department_id
            else:
                appraisal.department_id = False

    @api.depends('employee_id')
    def _compute_job_position_id(self):
        for appraisal in self:
            if appraisal.employee_id:
                appraisal.job_position_id = appraisal.employee_id.job_id
            else:
                appraisal.job_position_id = False

    def action_cancel(self):
        self.state = 'cancel'
        message = "Appraisal request has been cancelled. " + '<a href="#" data-oe-id=' + str(
            self.id) + ' data-oe-model="performance.appraisal">Appraisal' + '</a>'

        post = self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
            partner_ids=[self.employee_user_id.partner_id.id],
            author_id=self.env.user.id,)
        # if post:
        #     notification_ids = [
        #         (0, 0, {'res_partner_id': self.employee_user_id.partner_id.id, 'mail_message_id': post.id})]
        #     post.write({'notification_ids': notification_ids})

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancel(self):
        if any(appraisal.state not in ['new', 'cancel'] for appraisal in self):
            raise UserError(_("You cannot delete appraisal which is not in draft or canceled state"))

    def action_send_appraisal_request(self):
        for record in self:
            template_id = self.env.ref('performance_appraisal.mail_template_appraisal_request')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)
            record.state = 'request_sent'

    def action_approve_appraisal(self):
        for record in self:
            if not record.type_of_review:
                raise UserError(_("Please select type of review"))
            record.state = 'pending'
            template_id = self.env.ref('performance_appraisal.mail_template_appraisal_request_confirmed')
            if template_id:
                template_id.send_mail(record.id, force_send=True, raise_exception=False)

    def action_incorrect_form(self):
        for record in self:
            if not record.type_of_review:
                raise UserError(_("Please select type of review"))

            message = "Please attach correct form. " + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="performance.appraisal">Appraisal' + '</a>'

            post = record.message_post(
                body=message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.employee_user_id.partner_id.id],
                author_id=self.env.user.id)
            # if post:
            #     notification_ids = [(0, 0, {'res_partner_id': record.employee_user_id.partner_id.id, 'mail_message_id': post.id})]
            #     post.write({'notification_ids': notification_ids})

    def action_done(self):
        for record in self:
            if not record.compensation_package_attachment_ids:
                raise UserError(_("Please attach compensation package"))
            message = "Appraisal approved. " + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="performance.appraisal">Appraisal' + '</a>'

            post = record.message_post(
                body=message,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[record.employee_user_id.partner_id.id],
                author_id=self.env.user.id)
            record.date_close = fields.Date.today()
            record.state = 'done'
