from odoo import models, fields, api, _

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    emp_visa_id = fields.Many2one('employee.visa.form')
    emp_send_mail = fields.Boolean('Emp send')
    emp_reject_mail = fields.Boolean('reject mail')
    partner_id = fields.Many2one('res.partner', string="Partner")


    def action_send_mail(self):
        result = super(MailComposeMessage, self).action_send_mail()
        emp_visa = self.emp_visa_id.id

        if emp_visa:
            visa_record = self.env['employee.visa.form'].browse(emp_visa)

            if visa_record.state == 'req' and self.emp_send_mail:
                visa_record.write({'state':'app_1'})
            elif visa_record.state == 'app_1' and self.emp_send_mail:
                visa_record.write({'state':'app_2'})
            elif visa_record.state == 'app_2' and self.emp_send_mail:
                visa_record.write({'state':'app_3'})
            elif visa_record.state == 'app_3' and self.emp_send_mail:
                visa_record.write({'state':'done'})
            elif visa_record.state in ['app_1', 'app_2', 'app_3'] and self.emp_reject_mail:
                visa_record.write({'state': 'cancel'})

            for visa_partner in self.partner_ids:
                if visa_partner.user_ids:
                    department_users = self.env['res.users'].search([('id','=',visa_partner.user_ids[0].id)])
                    if department_users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        }) for user in department_users]

                        self.env['mail.message'].sudo().create({
                            'message_type': "notification",
                            'body': self.body,
                            'subject': "Visa Application Form",
                            'partner_ids': [(4, user.partner_id.id) for user in department_users],
                            'model': visa_record._name,
                            'res_id': visa_record.id,
                            'notification_ids': notification_ids,
                            'author_id': visa_record.env.user.partner_id.id,
                            'subtype_id': self.env['ir.model.data']._xmlid_to_res_id('mail.mt_comment'),

                        })






        return result
