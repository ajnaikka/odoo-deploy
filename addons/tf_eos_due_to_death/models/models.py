# -*- coding: utf-8 -*-

from odoo import models, fields, api




class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'


    emp_death_id = fields.Many2one('eos.death')



    def action_send_mail(self):

        result = super(MailComposeMessage, self).action_send_mail()
        emp_death = self.emp_death_id.id

        if emp_death:
            resi_record = self.env['eos.death'].browse(emp_death)

            if resi_record.state == 'req':
                resi_record.write({'state':'req_sent'})

        return result

    def action_send_mail_to_fm(self):

        result = super(MailComposeMessage, self).action_send_mail_to_fm()
        emp_death = self.emp_death_id.id

        if emp_death:
            resi_record = self.env['eos.death'].browse(emp_death)

            if resi_record.state == 'req':
                resi_record.write({'state':'hr_req_fm'})

        return result

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    end_of_service_death_ids = fields.One2many('eos.death','related_emp_id')

    def action_view_end_of_service_death_application_form(self):
        return {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.death',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('related_emp_id', '=', self.id)]
        }

    def action_end_of_service_death_application_form(self):
        action = {
            'name': 'End of Service',
            'type': 'ir.actions.act_window',
            'res_model': 'eos.death',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_id': self.id},

        }

        return action

class EndofServiceForm(models.Model):

    _name = 'eos.death'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'End of Service Due to Death'

    end_of_service_type = fields.Selection(
        related='related_emp_id.end_of_service_type',
        string='End of Service Type',
        store=True,
        readonly=True
    )
    email_from = fields.Char(string="From", required=True)
    email_to = fields.Many2one('res.partner', string="To", required=True)

    eos_death_letter = fields.Binary(string="End of service due to death attachment")
    file_name = fields.Char()
    state = fields.Selection([
        ('req', 'HR Request to CEO'),
        ('req_sent', 'Request Send to CEO'),
        ('ceo_accept', 'CEO Approved'),
        ('ceo_reject', 'CEO Rejected'),
        ('hr_req_fm', 'Request Send to FM'),
        ('fm_accept', 'FM Approved'),
        ('fm_reject', 'FM Rejected'),

    ],default='req', string='State')

    related_emp_id = fields.Many2one('hr.employee',string="Employee")
    user_id = fields.Many2one('res.users',default=lambda self:self.env.user)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)


    def action_send_mail(self, ctx=None):
        template = self.env.ref('tf_eos_due_to_death.eos_death_email')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id

        attachment_data = {
            'name': 'EoS Due to Death Letter',
            'datas': self.eos_death_letter,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data)
        context = {
            'default_model': 'eos.death',
            'default_res_ids': [self.id],
            'default_partner_ids': [],
            'default_emp_death_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])],
            'force_email': True,
            'default_email_to': self.related_emp_id.ceo_id.user_id.partner_id.email,
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

    def action_ceo_accept(self):
        for record in self:
            if record.state == 'req_sent':
                record.write({'state': 'ceo_accept'})
        return True

    def action_ceo_reject(self):
        for record in self:
            if record.state == 'req_sent':
                record.write({'state': 'ceo_reject'})
        return True

    def action_send_mail_to_fm(self, ctx=None):
        template = self.env.ref('tf_eos_due_to_death.hr_send_email_to_fm')
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        attachment_data = {
            'name': 'Reward/Grand RequestLetter',
            'datas': self.eos_death_letter,
            'res_model': self._name,
            'res_id': self.id,
        }
        attachment = self.env['ir.attachment'].create(attachment_data) if attachment_data.get('datas') else False
        context = {
            'default_model': 'eos.death',
            'default_res_ids': self.ids,
            'default_partner_ids':[self.email_to.id],
            'default_emp_death_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])] if attachment else None,
            'force_email': True,
            'default_email_to':self.email_to,
            'default_email_from': self.related_emp_id.hr_manager_id.user_id.partner_id.email,
            'default_partner_id_bus_bool': False,
            'default_partner_id':self.email_to.id
        }

        if ctx:
            context.update(ctx)
        self.write({'state': 'hr_req_fm'})
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

    def action_fm_accept(self):
        for record in self:
            if record.state == 'hr_req_fm':
                record.write({'state': 'fm_accept'})
        return True

    def action_fm_reject(self):
        for record in self:
            if record.state == 'hr_req_fm':
                record.write({'state': 'fm_reject'})
        return True