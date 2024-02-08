# -*- coding: utf-8 -*-

from odoo import models, fields, api




class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'


    emp_resi_id = fields.Many2one('end.service')



    def action_send_mail(self):

        result = super(MailComposeMessage, self).action_send_mail()
        emp_resi = self.emp_resi_id.id

        if emp_resi:
            resi_record = self.env['eos.cancellation'].browse(emp_resi)

            if resi_record.state == 'req':
                resi_record.write({'state':'req_sent'})

        return result
class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    end_of_service_cancellation_ids = fields.One2many('eos.cancellation','related_emp_id')

    def action_view_end_of_service_cancellation_application_form(self):
        return {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.cancellation',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('related_emp_id', '=', self.id)]
        }

    def action_end_of_service_cancellation_application_form(self):
        action = {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.cancellation',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_id': self.id},

        }

        return action

class EndofServiceForm(models.Model):
    _name = 'eos.cancellation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'End of Service cancellation by govt Form'

    end_of_service_type = fields.Selection(
        related='related_emp_id.end_of_service_type',
        string='End of Service Type',
        store=True,
        readonly=True
    )

    eos_cancellation_letter = fields.Binary(string="End of service request attachment")
    file_name = fields.Char()
    state = fields.Selection([
        ('req', 'Cancellation Request'),
        ('req_sent', 'Request Send'),
        ('employee_accept', 'Accepted by Employee'),

    ],default='req', string='State')

    related_emp_id = fields.Many2one('hr.employee',string="Employee")
    user_id = fields.Many2one('res.users',default=lambda self:self.env.user)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)


    def action_send_mail(self, ctx=None):
        template = self.env.ref('tf_eos_cancellation_by_govt.eos_cancellation_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'EoS Cancellation Letter',
            'datas': self.eos_cancellation_letter,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data)
        context = {
            'default_model': 'eos.cancellation',
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
        # Sending email using the mail.template
        template.with_context(**context).send_mail(self.id, force_send=True, raise_exception=True)
        self.write({'state': 'req_sent'})

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

    def action_employee_accept(self):
        for record in self:
            if record.state == 'req_sent':
                record.write({'state': 'employee_accept'})
        return True

