from odoo import models, fields, api

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    emp_ref_id = fields.Many2one('employee.referral')
    emp_ref_bool = fields.Boolean('Partner Hide')

    def action_send_mail(self):

        result = super(MailComposeMessage, self).action_send_mail()
        emp_ref = self.emp_ref_id.id

        if emp_ref:
            ref_record = self.env['employee.referral'].browse(emp_ref)

            if self.emp_ref_bool:
                ref_record.write({'state':'send'})


            ref_record_mang = ref_record.email_to.user_id.id

            hr_user = self.env['res.users'].search([('id','=',ref_record_mang)])


            notification_ids = [(0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }) for user in hr_user]

            self.env['mail.message'].create({
                'message_type': "notification",
                'body': "Employee Referral",
                'subject': "Employee Referral",
                'partner_ids': [(4, user.partner_id.id) for user in hr_user],
                'model': ref_record._name,
                'res_id': ref_record.id,
                'notification_ids': notification_ids,
                'author_id': ref_record.env.user.partner_id.id
            })


        return result
