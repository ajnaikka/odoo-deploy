from odoo import fields, models,api,_


class EmployeeReferral(models.Model):
    _name = 'employee.referral'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Referral Form'
    _rec_name = 'reference_no'

    post_name = fields.Char("Subject / Application", required=True, help="Email subject for applications sent via email")
    reference_no = fields.Char(string='Order Reference', required=True,
                               readonly=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'employee.referral') or _('New')
        res = super(EmployeeReferral, self).create(vals)
        return res

    partner_name = fields.Char("Applicant's Name")
    email_from = fields.Char('Email')
    email_to = fields.Many2one('res.partner',string="Email To",required=True)
    email_cc = fields.Char('Email CC')
    partner_phone = fields.Char('Phone')
    partner_mobile = fields.Char('Mobile')
    linkedln_profile = fields.Char('LinkedIn Profile')
    type_id = fields.Many2one('hr.recruitment.degree',string="Degree")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Mail Sent'),
        ('app', 'Approved'),
        ('hir','Hired'),
        ('proc', 'Processed'),
        ('rej', 'Rejected'),

    ],default='draft', string='State')

    emp_type = fields.Selection([
        ('friend', 'Friend'),
        ('rel', 'Close Relative'),
    ],default='', string='Type of Refer')

    relation = fields.Selection([
        ('spouse', "Employee’s Spouse"),
        ('grandparents', "Grandparents"),
        ('grandchildren', "Grandchildren"),
        ('great_grandchildren', "Great-Grandchildren"),
        ('parent', "Parent"),
        ('mother_in_law', "Mother-in-law"),
        ('father_in_law', "Father-in-law"),
        ('step_parents', "Step-parents"),
        ('children', "Children"),
        ('son_in_law', "Son-in-law"),
        ('daughter_in_law', "Daughter-in-law"),
        ('step_children', "Step-children"),
        ('brothers', "Brothers"),
        ('step_brothers', "Step-brothers"),
        ('brothers_in_law', "Brothers-in-law"),
        ('sisters', "Sisters"),
        ('step_sisters', "Step-sisters"),
        ('sisters_in_law', "Sisters-in-law"),
        ('aunts', "Aunts"),
        ('uncles', "Uncles"),
        ('first_cousins', "First Cousins"),
        ('second_cousins', "Second Cousins"),
        ('nephews', "Nephews"),
        ('nieces', "Nieces"),
    ], default='', string='Relation')

    job_id = fields.Many2one('hr.job',domain="[('no_of_recruitment','>',0)]")
    department_id = fields.Many2one('hr.department',string="Department")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    applicant_id = fields.Many2one('hr.applicant',string="Applicant")
    resume = fields.Binary(string='Resume')
    filename = fields.Char()

    @api.onchange('job_id')
    def _onchange_job_id(self):
        for applicant in self:
            if applicant.job_id.name:
                applicant.post_name = applicant.job_id.name


    def action_mail_sent(self):
        self.ensure_one()

        template_id = self.env['ir.model.data']._xmlid_to_res_id('tf_employee_referral.email_referral_applicant_id',
                                                                 raise_if_not_found=False)

        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'Resume',
            'datas': self.resume,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data) if attachment_data.get('datas') else False
        default_composition_mode = self.env.context.get('default_composition_mode',
                                                        self.env.context.get('composition_mode', 'comment'))

        compose_ctx = dict(
            default_composition_mode=default_composition_mode,
            default_model='employee.referral',
            default_res_ids=self.ids,
            default_emp_ref_id=self.id,
            default_template_id=template_id,
            default_partner_ids=[self.email_to.id],
            default_emp_ref_bool=True,
            default_use_template= bool(template_id),
            default_email_from=self.user_id.email_formatted,
            mail_tz=self.env.user.tz,
            default_attachment_ids=[(6, 0, [attachment.id])] if attachment else None,

        )

        return {
            'type': 'ir.actions.act_window',
            'name': _('applicant Mail'),
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': compose_ctx,
        }


    def action_chr_approve(self):
        for referral in self:

            vals = {
                'name': referral.post_name,
                'partner_name': referral.partner_name,
                'email_from': referral.email_from,
                'email_cc': referral.email_cc,
                'partner_phone': referral.partner_phone,
                'partner_mobile': referral.partner_mobile,
                'linkedin_profile': referral.linkedln_profile,
                'type_id': referral.type_id.id,
                'job_id': referral.job_id.id,
                'department_id': referral.department_id.id,
                'emp_referral': referral.id,

            }

            self.env['hr.applicant'].sudo().create(vals)
            referral.state = 'app'


    def action_chr_reject(self):
        self.state = 'rej'











