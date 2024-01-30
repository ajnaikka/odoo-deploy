from odoo import models, fields, api

class MailComposeMessageBus(models.TransientModel):
    _inherit = 'mail.compose.message'

    emp_bus_ter_id = fields.Many2one('employee.business.requirement')
    partner_id_bus_bool = fields.Boolean('Partner Hide')

    def action_send_mail(self):

        result = super(MailComposeMessageBus, self).action_send_mail()
        emp_bus = self.emp_bus_ter_id.id

        if emp_bus:
            bus_record = self.env['employee.business.requirement'].browse(emp_bus)

            if bus_record.state == 'req' and not self.partner_id_bus_bool:
                bus_record.write({'state':'app_1'})

            elif bus_record.state == 'app_1' and self.partner_id_bus_bool:
                bus_record.write({'state':'app_2'})

            elif bus_record.state == 'app_2' and not self.partner_id_bus_bool:
                bus_record.write({'state':'app_3'})

            bus_record_mang = bus_record.email_to.user_id.id
            bus_department_users = self.env['res.users'].search([('id','=',bus_record_mang)])

            notification_bus_ids = [(0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }) for user in bus_department_users]

            self.env['mail.message'].create({
                'message_type': "notification",
                'body': "Termination due to business requiremnt",
                'subject': "Employee Termination",
                'partner_ids': [(4, user.partner_id.id) for user in bus_department_users],
                'model': bus_record._name,
                'res_id': bus_record.id,
                'notification_ids': notification_bus_ids,
                'author_id': bus_record.env.user.partner_id.id
            })

        return result
