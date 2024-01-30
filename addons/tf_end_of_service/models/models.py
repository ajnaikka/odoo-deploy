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