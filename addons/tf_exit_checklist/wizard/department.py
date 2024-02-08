from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import logging
import pdfkit

_logger = logging.getLogger(__name__)
import os
import base64

class MailTravelagent(models.TransientModel):
    _name = 'mail.travelagent'

    exit_id = fields.Many2one('exit.form', string='Exit_id')
    email_to = fields.Many2one('hr.employee', string='Email To')
    partner_id = fields.Many2one('res.partner', string='Email To')
    is_travel_agent = fields.Boolean(string='Travel Agent')
    is_department = fields.Boolean(string='Department')
    is_Finance = fields.Boolean(string='Finance')

    def get_url(self):
        # Get the base URL from the configuration parameters
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # Construct the URL for the form view of the current record
        url = f'{base_url}/web#id={self.id}&model={self._name}&view_type=form'

        # If the exit_id field is set, append its ID to the URL
        if self.exit_id:
            url += f'&exit_id={self.exit_id.id}'
        print(url)

        return url


    def send_to_exit(self):

        if self.exit_id.is_travel:
            print('okkkkkkkkkkkkkkkkkkkkkk')
            template_values = {
                'name': 'Release Check List For Travel Agent',
                'subject': 'Release Check List For Travel Agent',
                'body_html': """
                            <div style="font-family: Arial, sans-serif; max-width: 1400px; margin: auto; border: 1px solid #fff; direction: ltr;">
                                <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                    <strong>Clearence Mail</strong>
                                </p>
                                <p style="text-align: left; font-size: 18px; color: #333; margin-bottom: 20px;" >
                                    <b>Dear %s,</b>
                                </p>
                                <br/>
                                <br/>
                                <p>
                                 All the clearances are approved by the company for %s so you can proceed." 
                                </p>
                                <br/>
                                <br/>
                                <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                                    Sincerely,
                                </p>
                                 <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                                    %s
                                </p>
                                <p style="text-align: left; font-size: 14px; color: #888;">
                                    (Signature)
                                    <br/>
                                    (Title)
                                </p>
                            </div>
                        """ % (self.email_to.name, self.exit_id.employee_id.name, self.env.user.name),
                'model_id': self.env.ref('tf_exit_checklist.model_exit_form').id,
            }

            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content
            rendered_message = mail_template.body_html

            # Create and send the email with attachment
            pdf_data = pdfkit.from_string(rendered_message, False)

            # Encode the PDF data
            pdf_data_base64 = base64.b64encode(pdf_data)

            # Create attachment data for the PDF
            attachment_data = {
                'name': 'Release_checklist.pdf',
                'datas': pdf_data_base64,
                'res_model': 'mail.mail',
                'res_id': 0,
            }

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': self.partner_id.email,
                'attachment_ids': [(0, 0, attachment_data)],
            })
            mail.send()

            # Notify sender and recipient
            self.env['mail.message'].create({
                'model': 'mail.mail',
                'res_id': mail.id,
                'subject': 'Notification',
                'partner_ids': [(4, self.env.user.partner_id.id), (4, self.partner_id.id)],
                'body': 'Notification Message',
            })
        if self.exit_id.is_dpt:
            template_values = {
                'name': 'Release Check List For Department Manager',
                'subject': 'Release Check List For Department Manager',
                'body_html': """
                            <div style="font-family: Arial, sans-serif; max-width: 1400px; margin: auto; border: 1px solid #fff; direction: ltr;">
                                <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                    <strong>Release Check List For Department Manager</strong>
                                </p>
                                <p style="text-align: left; font-size: 18px; color: #333; margin-bottom: 20px;" >
                                    <b>Dear %s,</b>
                                </p>
                                <br/>
                                <br/>
                                <p>
                                    I attached the link below. Verify the details, if it is correct, approve it, and also attach a signed copy.
                                </p>
                                <br/>
                                 <p>
                                   <a t-att-href="object.get_url()">
                                    Link of record</a>
                                </p>
                                <br/>
                                <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                                    Sincerely,
                                </p>
                                <p style="text-align: left; font-size: 14px; color: #888;">
                                    (Signature)
                                    <br/>
                                    (Title)
                                </p>
                            </div>
                        """ % (self.exit_id.employee_id.parent_id.name,self.get_url()),
                'model_id': self.env.ref('tf_exit_checklist.model_exit_form').id,
            }

            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content
            rendered_message = mail_template.body_html

            pdf_data = pdfkit.from_string(rendered_message, False)

            # Encode the PDF data
            pdf_data_base64 = base64.b64encode(pdf_data)

            # Create attachment data for the PDF
            attachment_data = {
                'name': 'Release_checklist.pdf',
                'datas': pdf_data_base64,
                'res_model': 'mail.mail',
                'res_id': 0,
            }

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': self.partner_id.email,
                'attachment_ids': [(0, 0, attachment_data)],
            })
            mail.send()

            # Notify sender and recipient
            self.env['mail.message'].create({
                'model': 'mail.mail',
                'res_id': mail.id,
                'subject': 'Notification',
                'partner_ids': [(4, self.env.user.partner_id.id), (4, self.partner_id.id)],
                'body': 'Notification Message',
            })

        if self.exit_id.is_Fin:
            template_values = {
                'name': 'Release Check List For Finance Manager',
                'subject': 'Release Check List For Finance Manager',
                'body_html': """
                               <div style="font-family: Arial, sans-serif; max-width: 1400px; margin: auto; border: 1px solid #fff; direction: ltr;">
                                   <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                       <strong>Release Check List For Finance Manager</strong>
                                   </p>
                                   <p style="text-align: left; font-size: 18px; color: #333; margin-bottom: 20px;" >
                                       <b>Dear %s,</b>
                                   </p>
                                   <br/>
                                   <br/>
                                   <p>
                                       I attached the link below. Verify the details, if it is correct, approve it, and also attach a signed copy.
                                   </p>
                                   <br/>
                                    <p>
                                       <a t-att-href="object.get_url()">
                                        Link of record</a>
                                    </p>
                                   <br/>
                                   <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                                       Sincerely,
                                   </p>
                                   <p style="text-align: left; font-size: 14px; color: #888;">
                                       (Signature)
                                       <br/>
                                       (Title)
                                   </p>
                               </div>
                           """ % (self.exit_id.employee_id.parent_id.name,self.get_url()),
                'model_id': self.env.ref('tf_exit_checklist.model_exit_form').id,
            }

            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content
            rendered_message = mail_template.body_html

            pdf_data = pdfkit.from_string(rendered_message, False)

            # Encode the PDF data
            pdf_data_base64 = base64.b64encode(pdf_data)

            # Create attachment data for the PDF
            attachment_data = {
                'name': 'Release_checklist.pdf',
                'datas': pdf_data_base64,
                'res_model': 'mail.mail',
                'res_id': 0,
            }

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': self.partner_id.email,
                'attachment_ids': [(0, 0, attachment_data)],
            })
            mail.send()

            # Notify sender and recipient
            self.env['mail.message'].create({
                'model': 'mail.mail',
                'res_id': mail.id,
                'subject': 'Notification',
                'partner_ids': [(4, self.env.user.partner_id.id), (4, self.partner_id.id)],
                'body': 'Notification Message',
            })