# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
import pytz
from datetime import time, datetime

DEFAULT_SERVER_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        #ddd
        # if vals.get('sale_order_ids',[]):
        #     sale_order_ids = vals.get('sale_order_ids',[])
        #     sale_pool = self.env['sale.order'].sudo()
        #     acquirer_id = vals.get('acquirer_id', False)
        #     stripe_id = self.env.ref("payment.payment_acquirer_stripe")
        #     if type(sale_order_ids) == list:
        #         if len(sale_order_ids)>0:
        #             if len(sale_order_ids[0])>=3:
        #                 if type(sale_order_ids[0][2])== list:
        #                     sale_dom = [('id', '=', sale_order_ids[0][2])]
        #                     sale_obj = sale_pool.search(sale_dom)
        #                     if stripe_id and sale_obj and \
        #                        acquirer_id and acquirer_id==stripe_id.id:
        #                         vals.update({'reference': sale_obj.name+ ":-" + vals.get('reference')})
        res = super(PaymentTransaction, self).create(vals)
        if res.state == 'done' and res.sale_order_ids[0]:
            if res.sale_order_ids[0].order_line:
                for line in res.sale_order_ids[0].order_line:
                    if res.amount > 0:
                        if line.price_unit == res.amount:
                            line.active_check = True
        return res

    def write(self, vals):
        res = super(PaymentTransaction, self).write(vals)
        if vals.get('state', False) and vals.get('state', '') == 'done':
            self.send_payment_response_mail()
            for rec in self:
                if rec.sale_order_ids and len(rec.sale_order_ids.ids) > 0:
                    flag = False
                    already_payment = False
                    if rec.sale_order_ids[0].order_line:
                        for line in rec.sale_order_ids[0].order_line:
                            if rec.amount > 0:
                                if line.price_unit == rec.amount and not line.active_check:
                                    line.active_check = True
                                    flag = True
                                    break
                                elif line.active_check:
                                    already_payment = True
                    if flag:
                        if not already_payment:
                            rec.sale_order_ids[0].uaa_quotation_confirm()
                    rec.check_payment_received()
                rec.check_additional_charge_state()
            self.recheck_invoice_create_paid()
        return res
    
    
        
    def recheck_invoice_create_paid(self):
        for rec in self:
            adv_payment_pool = self.env['sale.advance.payment.inv'].sudo()
            #sale_order_ids = self.env['sale.order'].search([('id', '=', 361)])
            #if sale_order_ids:
            if rec.sale_order_ids and len(rec.sale_order_ids.ids) > 0:
                #sale_id = sale_order_ids[0]
                sale_id = rec.sale_order_ids[0]
                if sale_id:
                    #print ('s' * 333, sale_id)
                    invoices = sale_id.mapped('invoice_ids')
                    #print ('i' * 333, invoices)
                    if not invoices:
                        wiz = adv_payment_pool.with_context(active_ids=sale_id.ids).create({})
                        wiz.create_invoices()
                    invoices = sale_id.mapped('invoice_ids')
                    if invoices:
                        invoice_id = invoices[0]
                        if invoice_id.state=='draft':
                            invoices.action_post()
                        if invoice_id.payment_state != 'paid' and invoice_id.move_type in \
                                ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
                            wiz_invoice = self.env['account.payment.register'].sudo().with_context(
                                active_model='account.move',
                                active_ids=invoice_id.ids).create({})
                            wiz_invoice.action_create_payments()
            return True
    
    

    def check_payment_received(self):
        for rec in self:
            if rec.sale_order_ids[0] and rec.sale_order_ids[0].enquiry_id:
                enquiry = rec.sale_order_ids[0].enquiry_id
                if enquiry:
                    if enquiry.response_status_id == \
                            self.env.ref("sr_uaa_main.payment_link_sent_response_status"):
                        enquiry.payment_received = True
            return True

    def send_payment_response_mail(self):
        for record in self:
            template = self.env.ref('sr_uaa_main.email_template_payment_response')
            customer = record.sale_order_ids[0] and \
                       record.sale_order_ids[0].traveler_name or \
                       record.partner_name or ' '
            payment_amount = record.amount or 0
            currency = record.currency_id and  record.currency_id.name or ''
            payment_ref = record.reference or ''
            sale_order = record.sale_order_ids[0] and record.sale_order_ids[0].name

            description = "%s makes a %s %s payment using the payment reference %s " \
                          "against Sale Order %s." \
                          %(customer, str(payment_amount),currency,payment_ref,sale_order)

            template.write({
                'body_html': description,
                'email_to':self.env.company and self.env.company.payment_response_mail or '',
            })

            mail_id = template.with_context(with_superuser_payment=True).send_mail(record.id, force_send=True)
            return True
            

    def check_additional_charge_state(self):
        for rec in self:
            if rec.sale_order_ids[0] and rec.sale_order_ids[0].state == 'done' \
                    and rec.sale_order_ids[0].additional_charges_ids:
                additional_charge_records = rec.sale_order_ids[0].additional_charges_ids
                if additional_charge_records:
                    for add_rec in additional_charge_records:
                        if add_rec.amount == rec.amount and rec.state == 'sent':
                            add_rec.state = 'sent'
                            break
                        elif add_rec.amount == rec.amount and rec.state == 'done':
                            add_rec.state = 'payment_received'
                            break
                        elif add_rec.amount == rec.amount and rec.state in ['draft', 'pending', 'authorized']:
                            add_rec.state = 'payment_pending'
                            break
                        elif add_rec.amount == rec.amount and rec.state in ['cancel', 'error']:
                            add_rec.state = 'payment_failed'
                            break

    def get_payment_receipt_values(self):
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
            if rec.invoice_ids:
                invoice_id = rec.invoice_ids[0]
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
                                         and len(enquiry_id.departure_date_str.split()) > 1 \
                                         and enquiry_id.departure_date_str.split()[0] or enquiry_id.departure_date_str) or ''
                        departure_time = enquiry_id and (enquiry_id.departure_date_str and enquiry_id.departure_date_str.split() \
                                         and len(enquiry_id.departure_date_str.split()) > 1 \
                                         and ' '.join(enquiry_id.departure_date_str.split()[1:]) or enquiry_id.departure_date_str) or ''
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
