# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'


    emp_resi_id = fields.Many2one('end.service')



    def action_send_mail(self):

        result = super(MailComposeMessage, self).action_send_mail()
        emp_resi = self.emp_resi_id.id

        if emp_resi:
            resi_record = self.env['end.service'].browse(emp_resi)

            if resi_record.state == 'req':
                resi_record.write({'state':'req_sent'})

            for resi_partner in self.partner_ids:
                if resi_partner.user_ids:
                    resig_users = self.env['res.users'].search([('id','=',resi_partner.user_ids[0].id)])

                    notification_ids = [(0, 0, {
                        'res_partner_id': user.partner_id.id,
                        'notification_type': 'inbox'
                    }) for user in resig_users]

                    self.env['mail.message'].create({
                        'message_type': "notification",
                        'body':  self.body,
                        'subject': self.subject,
                        'partner_ids': [(4, user.partner_id.id) for user in resig_users],
                        'model': resi_record._name,
                        'res_id': resi_record.id,
                        'notification_ids': notification_ids,
                        'author_id': resi_record.env.user.partner_id.id
                    })

        return result

    # def action_discussion_mail(self):
    #     result = super(MailComposeMessage, self).action_discussion_mail()
    #     emp_disc = self.emp_resi_id
    #
    #     if emp_disc:
    #         disc_record = self.env['end.service'].browse(emp_disc)
    #
    #         if disc_record.state == 'req_sent':
    #             print('dxfcvbvcfxdz')
    #             disc_record.write({'state': 'man_disc'})
    #
    #     return result