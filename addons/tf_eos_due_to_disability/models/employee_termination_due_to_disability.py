from odoo import fields, models,api


class TerBusinessRequirement(models.Model):
    _name = 'employee.disability.termination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Disability Termination Form'


    @api.model
    def default_get(self, fields):
        defaults = super(TerBusinessRequirement, self).default_get(fields)
        user = self.env.user
        defaults['email_from'] = user.partner_id.email if user.partner_id else ''
        return defaults

    #FIELDS

    email_from = fields.Char(string="From", required=True)
    email_to = fields.Many2one('res.partner',string="To",required=True)
    inv_letter = fields.Binary(string="Invitation Letter")
    file_name = fields.Char()
    states = fields.Selection([
        ('req', 'Request'),
        ('app_1', 'Send to Department'),
        ('app_2', 'In Extension'),
        ('app_3', 'Return to Department'),
        ('app_4', 'Send to Ceo'),
        ('app_5', 'Send to Hr'),
        ('ext', 'Leave Extended'),
        ('done', 'Contract Terminated'),
    ],default='req', string='State')
    related_dis_id = fields.Many2one('hr.employee', string="Employee", domain="[('id', '=', related_dis_id)]")
    user_id = fields.Many2one('res.users',default=lambda self:self.env.user)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)

    #EMAILS

    def action_send_mail_dis_dep_manager(self, ctx=None):
        template = self.env.ref('tf_eos_due_to_disability.employee_termination_due_to_disability_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        attachment_data = {
            'name': 'Termination Disability Letter',
            'datas': self.inv_letter,
            'res_model': self._name,
            'res_id': self.id,
        }
        attachment = self.env['ir.attachment'].create(attachment_data) if attachment_data.get('datas') else False
        context = {
            'default_model': 'employee.disability.termination',
            'default_res_ids': self.ids,
            'default_partner_ids':[self.email_to.id],
            'default_emp_dis_ter_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])] if attachment else None,
            'force_email': True,
            'default_email_from':self.email_from,
            'default_partner_id_bool_dis': False,
            'default_partner_id':self.email_to.id
        }

        if ctx:
            context.update(ctx)

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'views_id': compose_form_id,
            'target': 'new',
            'context': context,
        }

    def action_send_mail_ceo_manager(self):
        return self.action_send_mail_dis_dep_manager({'default_partner_id_bool_dis': True})

    def action_send_mail_hr_manager(self):
        return self.action_send_mail_dis_dep_manager()

    def action_send_mail_hr_to_emp(self):
        return self.action_send_mail_dis_dep_manager()

    def action_extension_yes(self):
        return self.action_send_mail_dis_dep_manager()

    def action_extension_no(self):
        return self.action_send_mail_dis_dep_manager({'default_partner_id_bool_dis': True})

    def action_send_mail_dep_to_hr(self):
        return self.action_send_mail_dis_dep_manager({'default_partner_id_bool_dis': True})

    def action_send_mail_hr(self):
        return self.action_send_mail_dis_dep_manager({'default_partner_id_bool_dis': True})

    def action_done(self):
        self.state = 'done'








