
from odoo import models, fields, api





class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    end_of_service_type = fields.Selection([
        ('resignation', 'End of service due to resignation'),
        ('termination', 'End of service due to termination'),
        ('condition', 'End of service due to condition and requirement of business'),
        ('non_fitness', 'End of service due to non-fitness and total disability'),
        ('cancel_by_govt', 'End of service due to cancellation by the government authorities'),
        ('retirement', 'End of service due to reaching retirement age'),
        ('due_to_death', 'End of service due to death'),
    ], string='End of Service Type')

    end_of_service_ids = fields.One2many('end.service','related_emp_id')
    ceo_id = fields.Many2one('hr.employee', 'CE0')
    hr_manager_id = fields.Many2one('hr.employee', 'HR Manager')

    def action_view_end_of_service_application_form(self):
        return {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'end.service',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('related_emp_id', '=', self.id)]
        }

    def action_end_of_service_application_form(self):
        action = {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'end.service',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_id': self.id},

        }

        return action





class EndofServiceForm(models.Model):
    _name = 'end.service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'End of Service Form'

    end_of_service_type = fields.Selection(
        related='related_emp_id.end_of_service_type',
        string='End of Service Type',
        store=True,
        readonly=True
    )

    inv_letter = fields.Binary(string="End of service request attachment")
    resi_acceptance_form = fields.Binary(string="Resignation Acceptance Form")
    file_name = fields.Char()
    state = fields.Selection([
        ('req', 'Request'),
        ('req_sent', 'Request Send'),
        ('man_disc', 'Discussion with Manager'),
        ('man_ap', 'Manager Approved'),
        ('req_hr', 'Request HR Approval'),
        ('hr_accept', 'Resignation Accepted'),
        ('hr_reject', 'Resignation Rejected'),
        ('req_ceo', 'Request CEO Approval'),
        ('ceo_accept', 'CEO Approved'),
        ('ceo_reject', 'CEO Rejected'),
    ],default='req', string='State')

    related_emp_id = fields.Many2one('hr.employee',string="Employee")
    user_id = fields.Many2one('res.users',default=lambda self:self.env.user)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)


    def action_send_mail(self, ctx=None):
        template = self.env.ref('tf_end_of_service.employee_resignation_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'Resignation Letter',
            'datas': self.inv_letter,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data)
        context = {
            'default_model': 'end.service',
            'default_res_ids': [self.id],
            'default_partner_ids': [],
            'default_emp_resi_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'force_email': True,
            'default_email_to': self.related_emp_id.parent_id.user_id.partner_id.email,
            'default_email_from': self.related_emp_id.user_id.partner_id.email,
            'default_partner_id': self.related_emp_id.parent_id.user_partner_id.id
        }

        if ctx:
            context.update(ctx)
        # Sending email using the mail.template
        template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)
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


    def action_discussion_mail(self, ctx=None):
            template = self.env.ref('tf_end_of_service.manager_disc_email')
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id


            context = {
                'default_model': 'end.service',
                'default_res_ids': [self.id],
                'default_partner_ids': [],
                'default_emp_resi_id': self.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'force_email': True,
                'default_email_to': self.related_emp_id.user_id.partner_id.email,
                'default_email_from': self.related_emp_id.parent_id.user_id.partner_id.email,
                'default_partner_id': self.related_emp_id.parent_id.user_partner_id.id
            }

            if ctx:
                context.update(ctx)
            template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)

            self.write({'state': 'man_disc'})

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

    def action_manager_approve(self):
        for record in self:
            if record.state == 'man_disc':
                record.write({'state': 'man_ap'})
        return True

    def action_req_hr_mail(self, ctx=None):
            template = self.env.ref('tf_end_of_service.req_hr_email')
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

            attachment_data = {
                'name': 'Resignation Letter',
                'datas': self.inv_letter,
                'res_model': self._name,
                'res_id': self.id,
            }

            attachment = self.env['ir.attachment'].create(attachment_data)
            context = {
                'default_model': 'end.service',
                'default_res_ids': [self.id],
                'default_partner_ids': [],
                'default_emp_resi_id': self.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'default_attachment_ids': [(6, 0, [attachment.id])],
                'force_email': True,
                'default_email_to': self.related_emp_id.hr_manager_id.user_id.partner_id.email,
                'default_email_from': self.related_emp_id.parent_id.user_id.partner_id.email,
                'default_partner_id': self.related_emp_id.parent_id.user_partner_id.id
            }

            if ctx:
                context.update(ctx)
            template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)

            self.write({'state': 'req_hr'})

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

    def action_hr_accept(self):
        for record in self:
            if record.state == 'req_hr':
                record.write({'state': 'hr_accept'})
        return True

    def action_hr_reject(self):
        for record in self:
            if record.state == 'req_hr':
                record.write({'state': 'hr_reject'})
        return True

    def action_req_ceo_mail(self, ctx=None):
        template = self.env.ref('tf_end_of_service.req_ceo_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'Resignation Letter',
            'datas': self.inv_letter,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data)

        context = {
            'default_model': 'end.service',
            'default_res_ids': [self.id],
            'default_partner_ids': [],
            'default_emp_resi_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'force_email': True,
            'default_email_to': self.related_emp_id.ceo_id.user_id.partner_id.email,
            'default_email_from': self.related_emp_id.hr_manager_id.user_id.partner_id.email,
            # 'default_partner_id': self.related_emp_id.parent_id.user_partner_id.id
        }

        if ctx:
            context.update(ctx)
        template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)

        self.write({'state': 'req_ceo'})

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

    def action_ceo_accept(self):
        for record in self:
            if record.state == 'req_ceo':
                record.write({'state': 'ceo_accept'})
        return True

    def action_ceo_reject(self):
        for record in self:
            if record.state == 'req_ceo':
                record.write({'state': 'ceo_reject'})
        return True

    def action_send_resignation_acceptance_form(self, ctx=None):
        template = self.env.ref('tf_end_of_service.resignation_acceptance_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'Resignation Acceptance Form',
            'datas': self.resi_acceptance_form,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data)

        context = {
            'default_model': 'end.service',
            'default_res_ids': [self.id],
            'default_partner_ids': [],
            'default_emp_resi_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'force_email': True,
            'default_email_to': self.related_emp_id.user_id.partner_id.email,
            'default_email_from': self.related_emp_id.hr_manager_id.user_id.partner_id.email,
            'default_partner_id': self.related_emp_id.parent_id.user_partner_id.id
        }

        if ctx:
            context.update(ctx)
        template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)


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
