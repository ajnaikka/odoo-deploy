from odoo import models, fields, api

class MailComposeMessageDis(models.TransientModel):
    _inherit = 'mail.compose.message'

    emp_dis_ter_id = fields.Many2one('employee.disability.termination')
    partner_id_bool_dis = fields.Boolean('Partner Hide')

    def action_send_mail(self):

        result = super(MailComposeMessageDis, self).action_send_mail()
        emp_dis = self.emp_dis_ter_id.id

        if emp_dis:
            dis_record = self.env['employee.disability.termination'].browse(emp_dis)

            if dis_record.states == 'req' and not self.partner_id_bool_dis:
                dis_record.write({'states':'app_1'})

            elif dis_record.states == 'app_1' and not self.partner_id_bool_dis:
                dis_record.write({'states':'app_2'})

            elif dis_record.states == 'app_2' and not self.partner_id_bool_dis:
                dis_record.write({'states':'app_3'})

            elif dis_record.states == 'app_2' and self.partner_id_bool_dis:
                dis_record.write({'states':'app_4'})

            elif dis_record.states == 'app_3' and self.partner_id_bool_dis:
                dis_record.write({'states':'ext'})

            elif dis_record.states == 'app_4' and self.partner_id_bool_dis:
                dis_record.write({'states':'app_5'})

            elif dis_record.states == 'app_5' and self.partner_id_bool_dis:
                dis_record.write({'states':'done'})

            for rec in self.partner_ids:
                if rec.user_ids:
                    dis_users = self.env['res.users'].search([('id','=',rec.user_ids[0].id)])

                    dis_notification_ids = [(0, 0, {
                        'res_partner_id': user.partner_id.id,
                        'notification_type': 'inbox'
                    }) for user in dis_users]


                    self.env['mail.message'].create({
                        'message_type': "notification",
                        'body': self.body,
                        'subject': self.subject,
                        'partner_ids': [(4, user.partner_id.id) for user in dis_users],
                        'model': dis_record._name,
                        'res_id': dis_record.id,
                        'notification_ids': dis_notification_ids,
                        'author_id': dis_record.env.user.partner_id.id
                    })

        return result
