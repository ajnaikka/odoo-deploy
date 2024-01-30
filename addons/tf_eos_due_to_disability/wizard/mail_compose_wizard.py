from odoo import models, fields, api

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    emp_dis_ter_id = fields.Many2one('employee.disability.termination')
    partner_id_bool = fields.Boolean('Partner Hide')

    def action_send_mail(self):

        result = super(MailComposeMessage, self).action_send_mail()
        emp_ter = self.emp_bus_ter_id.id

        if emp_ter:
            ter_record = self.env['employee.disability.termination'].browse(emp_ter)

            if ter_record.states == 'req' and not self.partner_id_bool:
                ter_record.write({'state':'app_1'})

            elif ter_record.states == 'app_1' and not self.partner_id_bool:
                ter_record.write({'state':'app_2'})

            elif ter_record.states == 'app_2' and not self.partner_id_bool:
                ter_record.write({'state':'app_3'})

            elif ter_record.states == 'app_2' and self.partner_id_bool:
                ter_record.write({'state':'app_4'})

            elif ter_record.states == 'app_3' and self.partner_id_bool:
                ter_record.write({'state':'ext'})

            elif ter_record.states == 'app_4' and self.partner_id_bool:
                ter_record.write({'state':'app_5'})

            elif ter_record.states == 'app_5' and self.partner_id_bool:
                ter_record.write({'state':'done'})



            ter_record_mang = ter_record.email_to.user_id.id
            department_users = self.env['res.users'].search([('id','=',ter_record_mang)])

            notification_ids = [(0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }) for user in department_users]

            self.env['mail.message'].create({
                'message_type': "notification",
                'body': "Termination due to disability",
                'subject': "Employee Termination",
                'partner_ids': [(4, user.partner_id.id) for user in department_users],
                'model': ter_record._name,
                'res_id': ter_record.id,
                'notification_ids': notification_ids,
                'author_id': ter_record.env.user.partner_id.id
            })

        return result
