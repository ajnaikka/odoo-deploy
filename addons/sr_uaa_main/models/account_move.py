# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from datetime import time, datetime
import time
from odoo import api, fields, models, tools, _
# from odoo.exceptions import UserError, ValidationError, Warning
from num2words import num2words
import pytz

DEFAULT_SERVER_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_payment_transactions_inv(self):
        for rec in self:
            payment_transactions = self.env['payment.transaction'].search(
                [('invoice_ids', 'in', rec.id)])
            rec.pay_trans_inv_no = len(payment_transactions)

    @api.model
    def default_get(self, fields):
        res = super(AccountMove, self).default_get(fields)
        company = self.company_id or self.env.company
        if company.terms_conditions:
            res['terms_conditions'] = company.terms_conditions
        if company.cancellation_policy:
            res['cancellation_policy'] = company.cancellation_policy
        if self.enquiry_id:
            res['traveler_name'] = self.enquiry_id.traveler_name
        return res
    
    @api.depends('enquiry_id')
    def compute_move_traveler_name(self):
        for record in self:
            traveler_name = ''
            if record.enquiry_id:
                traveler_name = record.enquiry_id.traveler_name
            record.traveler_name = traveler_name
            

    enquiry_id = fields.Many2one('airport.enquiry', string="Enquiry", copy=False)
    services_ids = fields.Many2many('enquiry.service.line', 'account_serviceline_rel', 'move_id', 'service_id',
                                    string="Service Charges")

    service_type_id = fields.Many2one('airport.service.type', 'Service Type', related='enquiry_id.service_type_id',
                                      store=True, readonly=True)
    uaa_services_id = fields.Many2one('uaa.services', 'Service', related='enquiry_id.uaa_services_id', store=True,
                                      readonly=True)
    description = fields.Html('Description')

    terms_conditions = fields.Text('Terms & Conditions')
    cancellation_policy = fields.Text('Cancellation Policy')
    pay_trans_inv_no = fields.Integer(compute='_compute_payment_transactions_inv', string='Payment Transactions')
    traveler_name = fields.Char('Name of the Traveller', 
                                compute='compute_move_traveler_name', stroe=True)
                                #related='enquiry_id.traveler_name', store=True, readonly=True)

    def get_enquiry(self):
        self.ensure_one()
        if self.enquiry_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Enquiry',
                'view_mode': 'form',
                'res_model': 'airport.enquiry',
                'res_id': self.enquiry_id.id,
                'context': "{'create': False,'edit': False,'delete': False}",
                'target': 'new',
            }

    def action_invoice_payment_transactions(self):
        for rec in self:
            payment_transactions = self.env['payment.transaction'].search(
                [('invoice_ids', 'in', rec.id)])
            action = self.env.ref('payment.action_payment_transaction').read()[0]
            list_view_id = self.env.ref('payment.transaction_list').id
            form_view_id = self.env.ref('payment.transaction_form').id
            if len(payment_transactions) == 1:
                action['res_id'] = payment_transactions.ids[0]
                action['views'] = [(form_view_id, 'form')]
            else:
                action['views'] = [(list_view_id, 'tree'), (form_view_id, 'form')]
                action['domain'] = [('id', 'in', payment_transactions.ids)]
            return action


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    traveler_name = fields.Char('Name of the Traveller')

    def get_payment_receipt_values(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for rec in self:
            vals = {
                "flight_number": "",
                "travel_date": "",
                "travel_time": "",
                "arrival_flight_number": "",
                "departure_flight_number": "",
                "arrival_time": "",
                "arrival_date": "",
                "departure_date": "",
                "departure_time": "",
            }
            service_name = ""
            service_heading = ""
            booking_number = ""
            partner_name = ""
            airport_name = ""
            service_type = ""
            services = ""
            if rec.reconciled_invoice_ids:
                invoice_id = rec.reconciled_invoice_ids[0]
                if invoice_id and invoice_id.enquiry_id:
                    enquiry_id = invoice_id.enquiry_id
                    service_name = ""
                    service_heading = ""
                    if enquiry_id.quotation_id:
                        for line in enquiry_id.quotation_id.order_line:
                            if line.active_check:
                                service_name = line.description
                                if line.service_id:
                                    service_heading = line.service_id.combination
                                    break
                    if enquiry_id.service_type_id:
                        service_type = enquiry_id.service_type_id.name
                        service_type_id = enquiry_id.service_type_id
                        arrival_date = enquiry_id and (enquiry_id.arrival_date_str and enquiry_id.arrival_date_str.split() \
                                       and len(enquiry_id.arrival_date_str.split()) > 1 and \
                                       enquiry_id.arrival_date_str.split()[0] or enquiry_id.arrival_date_str) or ''
                        arrival_time = enquiry_id and (enquiry_id.arrival_date_str and enquiry_id.arrival_date_str.split() \
                                       and len(enquiry_id.arrival_date_str.split()) > 1 and ' '.join(
                            enquiry_id.arrival_date_str.split()[1:]) or enquiry_id.arrival_date_str) or ''
                        departure_date = enquiry_id and (enquiry_id.departure_date_str and enquiry_id.departure_date_str.split() \
                                         and len(enquiry_id.departure_date_str.split()) > 1 and \
                                         enquiry_id.departure_date_str.split()[0] or enquiry_id.departure_date_str) or ''
                        departure_time = enquiry_id and (enquiry_id.departure_date_str and enquiry_id.departure_date_str.split() \
                                         and len(enquiry_id.departure_date_str.split()) > 1 and ' '.join(
                            enquiry_id.departure_date_str.split()[1:]) or enquiry_id.departure_date_str) or ''
                        if enquiry_id.service_type_id.is_departure:
                            vals.update({
                                "departure_flight_number": enquiry_id.departure_flight_number or "",
                                "departure_date": departure_date,
                                "departure_time": departure_time,
                            })
                        elif enquiry_id.service_type_id.is_arrival:
                            vals.update({
                                "arrival_flight_number": enquiry_id.arrival_flight_number or "",
                                "arrival_date": arrival_date,
                                "arrival_time": arrival_time,
                            })
                        elif enquiry_id.service_type_id.is_transit:
                            vals.update({
                                "arrival_flight_number": enquiry_id.arrival_flight_number or "",
                                "arrival_date": arrival_date,
                                "arrival_time": arrival_time,
                                "departure_flight_number": enquiry_id.departure_flight_number or "",
                                "departure_date": departure_date,
                                "departure_time": departure_time,
                            })

                    else:
                        service_type = ""

                    if enquiry_id.uaa_services_id:
                        services = enquiry_id.uaa_services_id.name
                    booking_number = enquiry_id.name or ""
                    partner_name = enquiry_id.traveler_name or ""
                    airport_name = enquiry_id.airport_id and enquiry_id.airport_id.name or ""
            vals.update({
                "booking_number": booking_number or "",
                "partner_name": partner_name or "",
                "airport_name": airport_name or "",
                "services": services or "",
                "service_type": service_type or "",
                "service_heading": service_heading or "",
                "service_name": service_name or "",
                "service_type_id": service_type_id or "",
            })
            return vals

    def action_mail_send_payment_receipt(self):
        self.ensure_one()
        template = self.env.ref('sr_uaa_main.email_template_payment_receipt_new')
        template_id = template.id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        email_to = ''
        subject = 'Payment Receipt | Universal Airport Assistance'
        # attachment_ids = []
        template.write({
            'email_to': email_to,
            'subject': subject
        })
        # template.attachment_ids = [(6, 0, attachment_ids)]
        # ctx = dict(
        #     default_composition_mode='comment',
        #     default_res_id=self.id,
        #     default_model='account.payment',
        #     default_use_template=bool(template_id),
        #     default_template_id=template_id,
        #     #custom_layout='mail.mail_notification_light'
        # )
        #
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'view_id': compose_form_id,
        #     'target': 'new',
        #     'context': ctx,
        # }
        
        ctx = {
                'default_model': 'account.payment',
                'default_res_id': self.id,
                'default_use_template': bool(template_id),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "mail.mail_notification_paynow",
                'force_email': True,
                #'default_attachment_ids': attachment_ids
            }
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    service_charge_words = fields.Text('Service Charge in Words')
