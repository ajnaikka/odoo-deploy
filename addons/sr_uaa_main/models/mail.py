# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning


class MailMail(models.Model):
    _inherit = 'mail.mail'
    
    def create(self, vals):
        '''To Aviod sending the email from odoobot'''
        res = super(MailMail, self).create(vals)
        context = self.env.context
        if context.get('with_superuser_payment'):
            pass
        elif res and res.author_id and res.author_id.id==2:
            return self
        return res
    

    def write(self, vals):
        res = super(MailMail, self).write(vals)
        for rec in self:
            if vals.get('state', False) == 'sent':
                booking_template = self.env.ref('sr_uaa_main.email_template_booking_confirmation').id
                payment_template = self.env.ref('sr_uaa_main.email_template_payment_receipt').id
                if self._context.get('default_template_id', False) in (booking_template, payment_template):
                    if rec.attachment_ids:
                        for attachment in rec.attachment_ids:
                            attachment.sudo().unlink()
        return res


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        res = super(MailComposer, self).action_send_mail()
        active_model = self.env.context.get('active_model', '')
        active_id = self.env.context.get('active_id', False)
        confirmation_voucher_send = self.env.context.get('confirmation_voucher_send', False)

        if active_model == 'airport.enquiry' and active_id and confirmation_voucher_send:
            enquiry_id = self.env[active_model].browse(active_id)
            enquiry_id.response_status_id = self.env.ref('sr_uaa_main.confirmation_voucher_sent_response_status').id
            enquiry_id.write({'response_status': 'confirmation_voucher_send',
                              'resp_status_change': 'confirmation_voucher_send'})
        return res
