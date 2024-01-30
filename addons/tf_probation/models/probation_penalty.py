from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)
import os

import base64

class Ikkama(models.Model):
    _name = 'ikkama'
    _description = 'Ikkama'
    _order = 'id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='Ikkama Expiry Date')
    issued_date = fields.Date(string='Issued Date')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    # contract_id = fields.Many2one('hr.contract', string='Contract', default=lambda self: self._default_contract_id())
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
    )
    document_line_ids = fields.One2many('documents.line', 'document_id', string='Document')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ikkam_req', 'Ikkama Request'),
        ('appointment', 'Appointment for medical Test'),
        ('issued', 'Ikkama Issued'),
        ('cancel', 'Canceled')
    ])
    hospital_name = fields.Char(string='Hospital Name')
    Location = fields.Char(string='Location')
    def get_record_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"

    def ikkama_request(self):
        self.state = 'ikkam_req'
        for ikkama_record in self:
            template_values = {
                'name': 'IKKAMA REQUEST',
                'subject': 'IKKAMA REQUEST',
                'body_html': """
                    <div style="font-family: Arial, sans-serif; max-width: 600px;">
                        <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                            <strong>Ikkama Request BY %s</strong>
                        </p>
                        <p>I am writing to request the processing of an Ikkama for me:</p>
                        <p>Here is the link of the requested form:</p>
                        <p><a href="%s">Link to Record</a></p>
                        <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                                        Sincerely,
                        </p>
                        <p>
                        %s
                        </p>
                    </div>
                    """ % (
                    ikkama_record.employee_id.name,
                    ikkama_record.get_record_url(),ikkama_record.employee_id.name,  # Use the actual method to get the record URL
                ),
                'model_id': self.env.ref('tf_probation.model_ikkama').id,
            }
            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content with specific values
            rendered_message = mail_template.body_html

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': ikkama_record.employee_id.parent_id.work_email,
            })
            mail.send()

        return True

    def medical_request(self):
        self.state = 'appointment'
        for ikkama_record in self:
            template_values = {
                'name': 'Details Of Documents For IKKAMA',
                'subject': 'Details Of Documents For IKKAMA',
                'body_html': """
                    <div style="font-family: Arial, sans-serif; max-width: 600px;">
                        <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                            <strong>Your request for IKKAMA has been accepted. For further proceedings of IKKAMA, submit medical details</strong>
                        </p>

                        <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                            Sincerely,
                        </p>
                        <p>
                            Human resource manager
                        </p>
                    </div>
                    """,
                'model_id': self.env.ref('tf_probation.model_ikkama').id,
            }
            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content with specific values
            rendered_message = mail_template.body_html

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': ikkama_record.employee_id.work_email,
            })
            mail.send()

        return True

    def ikkama_issue(self):
        self.state = 'issued'
        for ikkama_record in self:
            template_values = {
                'name': 'Congrats',
                'subject': 'Congrats',
                'body_html': """
                    <div style="font-family: Arial, sans-serif; max-width: 600px;">
                        <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                            <strong> Your IKKAMA has been scuessfully issued </strong>
                        </p>

                        <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                            Sincerely,
                        </p>
                        <p>
                            Human resource manager
                        </p>
                    </div>
                    """,
                'model_id': self.env.ref('tf_probation.model_ikkama').id,
            }
            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content with specific values
            rendered_message = mail_template.body_html

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': ikkama_record.employee_id.work_email,
            })
            mail.send()

        return True
    def ikkama_cancel(self):
        self.state = 'cancel'
        for ikkama_record in self:
            template_values = {
                'name': 'IKKAMA CANCEL',
                'subject': 'IKKAMA CANCEL',
                'body_html': """
                    <div style="font-family: Arial, sans-serif; max-width: 600px;">
                        <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                            <strong> Your IKKAMA request has been cancelled.Please send request again </strong>
                        </p>

                        <p style="text-align: left; font-size: 16px; color: #333; margin-top: 20px;">
                            Sincerely,
                        </p>
                        <p>
                            Human resource manager
                        </p>
                    </div>
                    """,
                'model_id': self.env.ref('tf_probation.model_ikkama').id,
            }
            email_template = self.env['mail.template'].create(template_values)
            mail_template = self.env['mail.template'].browse(email_template.id)

            # Render the email content with specific values
            rendered_message = mail_template.mail_template.body_html

            # Create and send the email with attachment
            mail = self.env['mail.mail'].create({
                'subject': mail_template.subject,
                'body_html': rendered_message,
                'email_from': self.env.user.email,
                'email_to': ikkama_record.employee_id.work_email,
            })
            mail.send()

        return True

class DocumentLine(models.Model):
    _name = 'documents.line'

    document_id = fields.Many2one('ikkama')
    document = fields.Char(string='Document')
    attachment = fields.Binary('Document', copy=False)
    # def action_send_mail(self):
    #     mail_template = self.env.ref(
    #         'tf_probation.email_probation_temp')  # Replace 'your_module' and 'mail_template_id' with actual values
    #     mail_template.send_mail(self.id)
    #
    #     return True


class HrEmployeeInherited(models.Model):
    _inherit = 'hr.employee'

    is_submitted = fields.Boolean(string='Reliving letter is not submitted')
    date_creation_prob = fields.Date()
    date_creation_ter = fields.Date()
    date = fields.Date()
    prob_date = fields.Date()
    text1 = fields.Text()
    prob_text1 = fields.Text()
    text2 = fields.Text()
    text3 = fields.Text()
    attachment = fields.Binary('Document', copy=False)
    attachment1 = fields.Binary('Document', copy=False)
    probation_status = fields.Selection([
        ('completed','Completed'),
        ('terminated', 'Terminated')],
        string='Probation Status'
    )
    identity_status = fields.Selection([
        ('received','Recevied'),
        ('lost', 'Lost'),
        ('not_received','Not Received')],
        string='Identity Card Status'
    )
    identity_no = fields.Char(string='Identity Card NO:')



    def action_send_mail(self):
        template_values = {}
        for employee in self:
            if employee.probation_status == 'completed':
                template_values = {
                    'name': 'COMPLETION OF PROBATIONARY PERIOD',
                    'subject': 'COMPLETION OF PROBATIONARY PERIOD',
                    'body_html': """
                                <div style="font-family: Arial, sans-serif; max-width: 600px;">
                                    <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                        <strong>COMPLETION OF PROBATIONARY PERIOD</strong>
                                    </p>
                                    <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                        <strong>Date %s,</strong>
                                    </p>
                                    <p style="text-align: left; font-size: 18px; color: #333; margin-bottom: 20px;" >
                                        <b>Dear %s,</b>
                                    </p>
                                    <br/>
                                    <br/>
                                    <p>
                                        I refer your appointment on probation effective from %s
                                        to the position of, <b>%s</b> I am pleased to advise that you have successfully completed the required probationary period, and hereby confirm your appointment.
                                        I would like to take this opportunity to offer you my congratulations and wish you a continuing and rewarding association with the agency.
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
                            """ % (employee.date_creation_prob,employee.name, employee.prob_date, employee.prob_text1),
                    'model_id': self.env.ref('hr.model_hr_employee').id,
                    # Replace 'hr' and 'model_hr_employee' with your actual module and model names
                }
                email_template = self.env['mail.template'].create(template_values)
                mail_template = self.env['mail.template'].browse(email_template.id)

                # Render the email content
                rendered_message = mail_template.body_html

                # Create and send the email with attachment
                attachment_data = {
                    'name': 'Completion_Letter.html',
                    'datas': base64.b64encode(rendered_message.encode('utf-8')),
                    'res_model': 'mail.mail',
                    'res_id': 0,
                }

                mail = self.env['mail.mail'].create({
                    'subject': mail_template.subject,
                    'body_html': rendered_message,
                    'email_from': self.env.user.email,  # Use the actual sender email
                    'email_to': employee.parent_id.work_email,
                    'attachment_ids': [(0, 0, attachment_data)],
                    # Add more fields as needed
                })
                mail.send()


            elif employee.probation_status == 'terminated':
                template_values = {
                    'name': 'Employee Termination under Penalty Procedure Form',
                    'subject': 'Employee Termination under Penalty Procedure Form',
                    'body_html': """
                        <div style="font-family: Arial, sans-serif; max-width: 600px;">
                            <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                <strong>Employee Termination under Penalty Procedure Form</strong>
                            </p>
                            <br/>
                            <p style="text-align: center; font-size: 18px; color: #333; margin-bottom: 20px;">
                                <strong>Date:%s,</strong>
                            </p>
                            <br/>
                            <p style="text-align: left; font-size: 18px; color: #333; margin-bottom: 20px;" >
                                Dear Sir,
                            </p>
                            <br/>
                            <br/>
                            <p>
                                After reviewing your performance report and penalty procedure issued against you by the
                                investigation committee on <b>%s</b>
                                corresponding to <b>%s</b> we regret to inform you that employment with the company
                                shall be terminated
                                effective <b>%s</b>, corresponding to,<b>%s</b>
                            </p>

                            <p>
                                Please meet HR department at your earliest to finalize the legal settlement procedures
                            </p>
                            <p>
                                Wish you success and Better Carrier
                            </p>
                            <br/>
                            <br/>
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
                    """ % (employee.date_creation_ter,employee.date, employee.text1,employee.text2,employee.text3),
                    'model_id': self.env.ref('tf_probation.model_hr_employee').id,
                    # Replace 'tf_probation' and 'model_hr_employee' with your actual module and model names
                }
                email_template = self.env['mail.template'].create(template_values)
                mail_template = self.env['mail.template'].browse(email_template.id)

                # Render the email content
                rendered_message = mail_template.body_html

                # Create and send the email with attachment
                attachment_data = {
                    'name': 'Completion_Letter.html',
                    'datas': base64.b64encode(rendered_message.encode('utf-8')),
                    'res_model': 'mail.mail',
                    'res_id': 0,
                }

                mail = self.env['mail.mail'].create({
                    'subject': mail_template.subject,
                    'body_html': rendered_message,
                    'email_from': self.env.user.email,  # Use the actual sender email
                    'email_to': employee.parent_id.work_email,
                    'attachment_ids': [(0, 0, attachment_data)],
                    # Add more fields as needed
                })
                mail.send()


            # Create the email template

        return True

    def action_send_ikkama(self):
        ikkama_record = self.env['ikkama'].create({
            'employee_id': self.id,
            # Add other default values if needed
        })

        view_id = self.env.ref('tf_probation.ikkama_form').id



        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Additional KM Form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'ikkama',
            'target': 'current',
            'res_id': ikkama_record.id,  # Pass the ID of the newly created record
            'context': {
                 'default_employee_id': self.id,
            }
        }
    def smart_ikkama(self):
        self.ensure_one()
        all_child = self.with_context(active_test=False).search([('id', 'in', self.ids)])

        action = self.env["ir.actions.act_window"]._for_xml_id("tf_probation.ikkama_action")
        action['domain'] = [
            ('employee_id', 'in', all_child.ids)
        ]
        action['context'] = {'search_default_employee_id': self.id}
        return action




class HrContractInherited(models.Model):
    _inherit = 'hr.contract'

    probation_expiery = fields.Date(string='Probation Expiry Date', compute='_compute_probation_expiry', store=True)
    contract_start_date = fields.Date(string='Contract Start Date', required=True, default=fields.Date.today())

    @api.depends('date_start')
    def _compute_probation_expiry(self):
        for record in self:
            if record.date_start:
                probation_period = relativedelta(months=3)
                record.probation_expiery = record.date_start + probation_period
