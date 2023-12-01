from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import base64
import pytz
import re
import phonenumbers

import logging

_logger = logging.getLogger(__name__)
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

DEFAULT_SERVER_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'
DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%d %H:%M'
DEFAULT_FACTURE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

regex = r'^\w+$'


class AirportEnquiry(models.Model):
    _name = 'airport.enquiry'
    _description = 'Airport Enquiry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.model
    def default_get(self, fields_list):
        res = super(AirportEnquiry, self).default_get(fields_list)
        res['verified_by'] = self.env.user.id
        res['travel_class_id'] = self.env.ref("sr_uaa_main.first_class_travel").id
        res['response_status_id'] = self.env.ref("sr_uaa_main.new_enquiry_response_status").id
        res['service_type_id'] = self.env.ref("sr_uaa_main.arrival_service_type").id
        company = self.company_id or self.env.company
        if company.partner_id.emergency_number:
            res['emergency_number'] = company.partner_id.emergency_number
        return res

    def enquiry_reminder_send_button_new(self):
        for rec in self:
            self.ensure_one()
            template = self.env.ref('sr_uaa_main.email_template_journey_reminder')
            template_id = template.id
            compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
            email_to = rec.email
            subject = 'Journey Reminder | Universal Airport Assistance'

            departure_date = False
            departure_time = False
            arrival_time = False
            arrival_date = False
            pickup_date_time = False
            if rec.service_type_id and rec.service_type_id != rec.service_type_id.is_arrival:
                departure_date = rec and (rec.departure_date_str and rec.departure_date_str.split() \
                                          and len(rec.departure_date_str.split()) > 1 \
                                          and rec.departure_date_str.split()[
                                              0] or rec.departure_date_str) or ''
                departure_time = rec and (rec.departure_date_str and rec.departure_date_str.split() \
                                          and len(rec.departure_date_str.split()) > 1 \
                                          and ' '.join(
                            rec.departure_date_str.split()[1:]) or rec.departure_date_str) or ''
                pickup_date_time = rec.pickup_date_str

            if rec.service_type_id and rec.service_type_id != rec.service_type_id.is_departure:
                arrival_date = rec and (rec.arrival_date_str and rec.arrival_date_str.split() \
                                        and len(rec.arrival_date_str.split()) > 1 and \
                                        rec.arrival_date_str.split()[
                                            0] or rec.arrival_date_str) or ''
                arrival_time = rec and (rec.arrival_date_str and rec.arrival_date_str.split() \
                                        and len(rec.arrival_date_str.split()) > 1 and ' '.join(
                            rec.arrival_date_str.split()[1:]) or rec.arrival_date_str) or ''
                pickup_date_time = rec.pickup_date_str

            vals = {
                'name': rec.traveler_name,
                'service_type': rec.service_type_id,
                'arrival_flight_no': rec.arrival_flight_number,
                'departure_flight_no': rec.departure_flight_number,
                'meeting_point': rec.meeting_point,
                'departure_date': departure_date or False,
                'departure_time': departure_time or False,
                'arrival_time': arrival_time or False,
                'arrival_date': arrival_date or False,
                'customer_mail': rec.email,
                'pickup_date_time': pickup_date_time or False,
                'uaa_services_name': rec.uaa_services_id and rec.uaa_services_id.name,
                'airport_name': rec.airport_id and rec.airport_id.name,
                'airport_code': rec.airport_id and rec.airport_id.code or '',
                'airport_country': rec.airport_id and rec.airport_id.country_id
                                   and rec.airport_id.country_id.name or '',
                'booking_number': rec.name,
                'company_phone': self.env.company and self.env.company.partner_id and self.env.company.partner_id.emergency_number or ' ',
                'company_email': self.env.company and self.env.company.email or ' ',
                'company_website': self.env.company and self.env.company.website or ' ',
                'drop_off_location': rec.drop_off_location or rec.drop_off_airport_id and
                                     rec.drop_off_airport_id.name or '',
                'pick_up_location': rec.pick_up_location or rec.pick_up_airport_id and
                                    rec.pick_up_airport_id.name or '',
            }
            print("vals", vals)

            template.write({
                'email_to': email_to,
                'subject': subject,
                'body_html': self.mail_enquiry_reminder(vals)
            })

            print("template", template)

            ctx = {
                'default_model': 'airport.enquiry',
                'default_res_id': self.id,
                'default_use_template': bool(template_id),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                # 'custom_layout': "mail.mail_notification_paynow",
                'force_email': True
            }
            print("ctx", ctx)
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
            # template.body_html = body_html

    def enquiry_reminder_send_button(self):
        for rec in self:
            if rec.meeting_point:
                rec.notified_customer = False
                rec.enquiry_reminder()
            else:
                raise UserError(_('Please Enter Meeting Point'))

    def enquiry_reminder(self):

        today = fields.Datetime.today()
        tomorrow = today + relativedelta(days=1)
        tomorrow_start = tomorrow - relativedelta(hours=2)
        tomorrow_end = tomorrow + relativedelta(hours=2)
        # airport_enq_ids = self.env['airport.enquiry'].search(
        #     [('status', '=', 'open'), ('notified_customer', '=', False),
        #      ('response_status_id', 'in',
        #       (self.env.ref(
        #           "sr_uaa_main.service_confirmed_response_status").id,
        #        self.env.ref(
        #            "sr_uaa_main.confirmation_voucher_sent_response_status").id)),
        #      ('service_date', '>=', tomorrow_start.date()),
        #      ('service_date', '<=', tomorrow_end.date())])
        airport_enq_ids = self
        if airport_enq_ids:
            for enquiry in airport_enq_ids:
                if enquiry.notified_customer:
                    continue
                departure_date = False
                departure_time = False
                arrival_time = False
                arrival_date = False
                pickup_date_time = False
                if enquiry.service_type_id and enquiry.service_type_id != enquiry.service_type_id.is_arrival:
                    departure_date = enquiry and (enquiry.departure_date_str and enquiry.departure_date_str.split() \
                                                  and len(enquiry.departure_date_str.split()) > 1 \
                                                  and enquiry.departure_date_str.split()[
                                                      0] or enquiry.departure_date_str) or ''
                    departure_time = enquiry and (enquiry.departure_date_str and enquiry.departure_date_str.split() \
                                                  and len(enquiry.departure_date_str.split()) > 1 \
                                                  and ' '.join(
                                enquiry.departure_date_str.split()[1:]) or enquiry.departure_date_str) or ''
                    pickup_date_time = enquiry.pickup_date_str

                if enquiry.service_type_id and enquiry.service_type_id != enquiry.service_type_id.is_departure:
                    arrival_date = enquiry and (enquiry.arrival_date_str and enquiry.arrival_date_str.split() \
                                                and len(enquiry.arrival_date_str.split()) > 1 and \
                                                enquiry.arrival_date_str.split()[
                                                    0] or enquiry.arrival_date_str) or ''
                    arrival_time = enquiry and (enquiry.arrival_date_str and enquiry.arrival_date_str.split() \
                                                and len(enquiry.arrival_date_str.split()) > 1 and ' '.join(
                                enquiry.arrival_date_str.split()[1:]) or enquiry.arrival_date_str) or ''
                    pickup_date_time = enquiry.pickup_date_str

                vals = {
                    'name': enquiry.traveler_name,
                    'service_type': enquiry.service_type_id,
                    'arrival_flight_no': enquiry.arrival_flight_number,
                    'departure_flight_no': enquiry.departure_flight_number,
                    'meeting_point': enquiry.meeting_point,
                    'departure_date': departure_date or False,
                    'departure_time': departure_time or False,
                    'arrival_time': arrival_time or False,
                    'arrival_date': arrival_date or False,
                    'customer_mail': enquiry.email,
                    'pickup_date_time': pickup_date_time or False,
                    'uaa_services_name': enquiry.uaa_services_id and enquiry.uaa_services_id.name,
                    'airport_name': enquiry.airport_id and enquiry.airport_id.name,
                    'airport_code': enquiry.airport_id and enquiry.airport_id.code or '',
                    'airport_country': enquiry.airport_id and enquiry.airport_id.country_id
                                       and enquiry.airport_id.country_id.name or '',
                    'booking_number': enquiry.name,
                    'company_phone': self.env.company and self.env.company.partner_id and self.env.company.partner_id.emergency_number or ' ',
                    'company_email': self.env.company and self.env.company.email or ' ',
                    'company_website': self.env.company and self.env.company.website or ' ',
                    'drop_off_location': enquiry.drop_off_location or enquiry.drop_off_airport_id and
                                         enquiry.drop_off_airport_id.name or '',
                    'pick_up_location': enquiry.pick_up_location or enquiry.pick_up_airport_id and
                                        enquiry.pick_up_airport_id.name or '',
                }
                if enquiry.meeting_point:
                    if self.mail_enquiry_reminder(vals):
                        enquiry.notified_customer = True
                        enquiry.message_post(body="Reminder Mail send successfully")

    # reminder send to customer
    def mail_enquiry_reminder(self, enquiry_vals={}):

        email_to = enquiry_vals.get('customer_mail', False)
        mail_content = """  Dear """
        mail_content += enquiry_vals.get('name', 'Customer') + """, <br/> """
        # mail_content += """<br/>Service Reminder <br/><br/>"""
        if enquiry_vals and email_to:
            name = enquiry_vals.get('name', '')
            service_type = enquiry_vals.get('service_type', False)
            arrival_flight_no = enquiry_vals.get('arrival_flight_no', '')
            departure_flight_no = enquiry_vals.get('departure_flight_no', '')
            arrival_time = enquiry_vals.get('arrival_time', '')
            arrival_date = enquiry_vals.get('arrival_date', '')
            departure_date = enquiry_vals.get('departure_date', '')
            departure_time = enquiry_vals.get('departure_time', '')
            uaa_services_name = enquiry_vals.get('uaa_services_name', '')
            airport_name = enquiry_vals.get('airport_name', '')
            airport_code = enquiry_vals.get('airport_code', '')
            airport_country = enquiry_vals.get('airport_country', '')
            booking_number = enquiry_vals.get('booking_number', '')
            company_phone = enquiry_vals.get('company_phone', '')
            company_email = enquiry_vals.get('company_email', '')
            company_website = enquiry_vals.get('company_website', '')
            drop_off_loc = enquiry_vals.get('drop_off_location', '')
            pick_up_loc = enquiry_vals.get('pick_up_location', '')
            meeting_point = enquiry_vals.get('meeting_point', '')
            pickup_date_time = enquiry_vals.get('pickup_date_time', '')

            parm_pool = self.env['ir.config_parameter'].sudo()
            base_url = parm_pool.get_param('web.base.url', default='https://localhost:8069')

            mail_content += """<div style="width:800px; max-width:100%; margin:0 auto 0 0"><div style="width:100%;text-align:center;">"""
            mail_content += """   <img style="max-height:100px;max-width: 230px;"
                 src='"""
            mail_content += str(base_url + '/sr_uaa_main/static/src/images/logo.png')
            mail_content += """'/>
            </div>


            """
            mail_content += """
            <div style="width:99%; border: 1px solid #0eb4df; border-right: 1px solid #0eb4df!important; border-color:#0eb4df;">
                        <div class="row" style="width:100%; border:0;">
                        <table style="width:100%;border:0;">
                            <tr style="height:50px;border:0;background-color:#0eb4df;">
                            <!--<tr style="height:50px;background-color:#0eb4df;">-->
                                <td style="text-transform: uppercase;color:white;font-size:30px;padding-left:13px; border:0; border-bottom:0; text-align:center"> <b>""" + \
                            uaa_services_name + """
                                    REMINDER</b>
                                </td>
                            </tr> 
                            <tr style="height:50px;background-color:#ecf0f1; border:0;">
                                <td width="80%"
                                    style="text-align:left;padding:15px;">  We look forward to providing service for your upcoming journey. Please go through the journey
                                    details below :
                                </td>
                            </tr>
                        </table>
                    </div>

                    <div class="row" style="border:0; border-top:0;">
                        <table style="width:100%;border:0; border-top:0;">
                            <tr style="height:30px;border:0;">
                                <td width="50%"
                                    style="padding-left:13px;line-height: 30px;border:0;">Booking Number
                                </td>
                                <td width="50%" style="padding-left:13px;line-height: 30px;">#""" + booking_number + """
                                </td>
                            </tr> 
                            <tr style="height:30px;border:0;background-color:#ECF0F1;">
                                <td width="50%"
                                    style="padding-left:13px;line-height: 30px;border:0;
                                    background-color:#ECF0F1;">Passenger Name
                                </td>
                                <td width="50%" style="padding-left:13px;line-height: 30px;background-color:#ECF0F1;">
                                 """ + name + """
                                </td>
                            </tr> """

            if arrival_date:
                mail_content += """


                                <tr style="height:30px;border:0;">
                                    <td style="padding-left:13px;line-height: 30px;border:0;width:50%">
                                    Arrival Date
                                    </td>
                                    <td style="padding-left:13px;line-height: 30px;width:50%">   """ \
                                + arrival_date + """
                                    </td>
                                </tr>

                                 <tr style="height:30px;border:0;background-color:#ECF0F1!important;">
                                    <td style="padding-left:13px!important;line-height: 30px!important;background-color:#ECF0F1!important;width:50%;">
                                  Arrival Details (flight no & time)
                                    </td>
                                    <td style="padding-left:13px;line-height: 30px; background-color:#ECF0F1;width:50%"> 
                                    """ + arrival_flight_no + """ @ """ + arrival_time + """ Hrs
                                    </td>
                                </tr> """

            if departure_date:
                mail_content += """
                                <tr style="height:30px;border:0;">
                                    <td style="padding-left:13px;line-height: 30px;border:0; width:50%">Departure Date
                                    </td>
                                    <td style="padding-left:13px;line-height: 30px; width:50%">   """ \
                                + departure_date + """
                                    </td>
                                </tr>
                                 <tr style="height:30px;border:0;background-color:#ECF0F1;">
                                    <td 
                                        style="padding-left:13px;line-height: 30px;border:0;
                                        background-color:#ECF0F1;width:50%">Departure Details (flight no & time)
                                    </td>
                                    <td  style="padding-left:13px;line-height: 30px;border:0;
                                    background-color:#ECF0F1;"> """ + departure_flight_no + """ @ """ + departure_time + """ Hrs</td>
                                </tr> """

            mail_content += """
                             <tr style="height:30px;border:0;">
                                <td style="padding-left:13px;line-height: 30px;border:0;width:50%">Airport
                                </td>
                                <td style="padding-left:13px;line-height: 30px;width:50%"> """ + \
                            str(airport_name + ''' (''' + airport_code + ''') ''' + ''' / ''' + airport_country) + """
                                </td>
                            </tr> """

            if pick_up_loc:
                mail_content += """
                                 <tr style="height:30px;">
                                    <td style="padding-left:13px;line-height: 30px;background-color:#ECF0F1;">Pick Up Location
                                    </td>
                                    <td style="padding-left:13px;line-height: 30px;background-color:#ECF0F1;width:50%">
                                     """ + pick_up_loc + """
                                    </td>
                                </tr> """

            if drop_off_loc:
                mail_content += """
                                 <tr style="height:30px;">
                                    <td style="padding-left:13px;line-height: 30px;width:50%">Drop Off Location
                                    </td>
                                    <td style="padding-left:13px;line-height: 30px;width:50%">   """ \
                                + drop_off_loc + """
                                    </td>
                                </tr> """

            if meeting_point:
                mail_content += """
                                <tr style="height:30px;">
                                   <td width="50%"
                                        style="padding-left:13px;line-height: 30px;
                                    background-color:#ECF0F1;">Meeting Point
                                   </td>
                                   <td width="50%" style="padding-left:13px;line-height:30px;background-color:#ECF0F1;"> 
                                   """ + meeting_point + """
                                    </td>
                                </tr> """

            if pickup_date_time:
                mail_content += """
                            <tr style="height:30px;">
                               <td width="50%"
                                    style="padding-left:13px;line-height: 30px;">Pickup Date-Time
                               </td>
                               <td width="50%" style="padding-left:13px;line-height: 30px;"> 
                               """ + pickup_date_time + """
                                </td>
                            </tr> """

            mail_content += """
                        </table>


                        <table style="background-color:#0eb4df;border:none !important;color:white; line-height:2; width:100%; border: 1px solid #ecf0f1; border-top:0;"
                               cellspacing="0" cellpadding="0">
                                    <tbody>
                                            <tr>
                                                <td colspan="3"  style="border:none !important;width:100%;text-align:center">
                                                    <b><u><span>
                                                    IMPORTANT THINGS TO REMEMBER</span></u></b>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="border:none !important;width:50%;text-align:right;padding-right:20px;">
                                                    <span style=" margin-left: 10px;  width: 120px; display: inline-block; text-align: left; font-size: 12px;">* Passport/visa</span>
                                                </td>
                                                <td style="border:none !important;width:50%;">
                                                    <span style="font-size: 12px;">* Ticket copies</span></td>
                                            </tr>
                                             <tr>
                                                <td style="border:none !important;width:50%;text-align:right;padding-right:20px;">
                                                    <span style="    margin-left: 10px;  width: 120px;  display: inline-block;  text-align: left;font-size: 12px;">* Id cards</span>
                                                </td>
                                                <td style="border:none !important;width:50%;">
                                                    <span style="font-size: 12px;">* Insurance document</span></td>
                                            </tr>
                                             <tr>
                                                <td style="border:none !important;width:50%;text-align:right;padding-right:20px;">
                                                    <span style="margin-left: 10px; width: 120px; display: inline-block; text-align: left; font-size: 12px;">* Debit/credit cards</span>
                                                </td>
                                                <td style="border:none !important;width:50%;">
                                                    <span style="font-size: 12px;">* Medicines & charger</span></td>
                                            </tr>

                                    </tbody>

                        </table>
                    </div>
                    <div style="border: 1px solid #ecf0f1; border-top:0;">

                     <div class="row" style=";border: 1px solid #ecf0f1; border-top:0;">
                     <table style="background:#ecf0f1;border:none !important;width:100%;text-align:center !important;border: 1px solid #ecf0f1; border-top:0;">
                     <tr style="border-right: 1px solid #ddd;border-left: 1px solid #ddd;
                                border-bottom: 1px solid #ecf0f1">
                                <td style="text-align:center; "><b>Have a pleasant & Safe Journey…</b>
                                </td>
                            </tr>
                                            </table>
                                            </div>
                     <div class="row" style="">
                     <table style="background:#ecf0f1;border:none !important; line-height:1" width="100%">
                             <tr>
                                <td style="text-align:center;"><b>Emergency contact:</b>
                                <b>""" + company_phone + """</b>
                                </td>
                            </tr>
                            <tr>
                                 <td 
                                    style="color:#0eb4df;text-align:center">
                                   <u><b>""" + company_email + """ </b></u>
                                </td>
                            </tr>   
                            <tr>
                                 <td 
                                    style="font-color:black;text-align:center;padding-bottom:5px">
                                     <u>""" + company_website + """</u>
                                </td>
                            </tr>
                                            </table>
                                            </div>

                            </div>
                            </div>

                              """

            main_content = {
                'subject': _('Journey Reminder'),
                'email_from': self.env.company and self.env.company.partner_id and self.env.company.partner_id.email or '',
                'body_html': mail_content,
                'email_to': email_to,
            }
            mail_id = self.env['mail.mail'].create(main_content)
            mail_id.send()
            return True
        return False

    def enquiry_expiry(self):
        now = datetime.now()
        now_date = now.strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.today() + timedelta(days=-1)
        # if self.departure_date:
        #     domain = [('departure_date', '<=', today),
        #               ('status', '=', 'open')]
        # else:
        domain = [('service_date', '<=', today),
                  ('status', '=', 'open')]

        enquiry = self.env['airport.enquiry'].sudo().search(domain)
        # enquiry = self.env['airport.enquiry'].sudo().search([('service_date', '<=', now_date),
        #                                                      ('status', '=', 'open')])
        for rec in enquiry:
            if rec.status == 'open':
                rec.status = 'close'

    def send_enquiry_details(self):
        today = fields.Date.today()
        tomorrow = today + relativedelta(days=1)
        enquiry_ids = self.env['airport.enquiry'].sudo().search(
            [('status', '=', 'open'), ('response_status_id', '=', (self.env.ref(
                "sr_uaa_main.confirmation_voucher_sent_response_status").id)),
             ('service_date', '>=', '%s 00:00:00' % tomorrow),
             ('service_date', '<=', '%s 23:59:59' % tomorrow)])
        if enquiry_ids:
            enquiry_list = []

            for enquiry in enquiry_ids:
                vals = {
                    'name': enquiry.name,
                    'traveler_name': enquiry.traveler_name,
                    'airport_name': enquiry.airport_id.name,
                    'airport_code': enquiry.airport_id and enquiry.airport_id.code or '',
                    'airport_country': enquiry.airport_id and enquiry.airport_id.country_id
                                       and enquiry.airport_id.country_id.name or '',
                    'service_type': enquiry.service_type_id,
                    'service_date': enquiry.service_date,
                    'response_status': enquiry.response_status_id.name,
                    'enquiry_status': enquiry.status,
                    'enquiry': enquiry,
                }
                enquiry_list.append(vals)
            if enquiry_list:
                self.mail_enquiry_details(self.env.company, enquiry_list, tomorrow)

    def mail_enquiry_details(self, company_id, enquiry_list=[], tomorrow=''):
        company_email = ''
        if company_id:
            company_email = company_id.email
        email_to = company_email
        mail_content = """  Dear Team,
                        <br/>
                        Confirmed service details of """
        mail_content += str(tomorrow.strftime("%d/%m/%Y"))
        mail_content += """ as follows <br/><br/>"""

        if enquiry_list and email_to:
            mail_content += '''
                <table border=1 style="font-color:black">
                    <tr>
                        <td align="center">
                            <b>Booking Number</b>
                        </td>
                        <td align="center">
                            <b>Name of the Traveller</b>
                        </td>
                        <td align="center">
                            <b>Airport Name</b>
                        </td> 
                        <td align="center">
                           <b> Service Type</b>
                        </td> 
                        <td align="center">
                            <b>Service Date</b>
                        </td> 
                        <td align="center">
                           <b> Response Status</b>
                        </td>
                        <td align="center">
                            <b>Enquiry Status</b>
                        </td>
                    </tr>'''

            for item in enquiry_list:
                name = item.get('name', '')
                traveler_name = item.get('traveler_name', '')
                airport_name = item.get('airport_name', '')
                airport_code = item.get('airport_code', '')
                airport_country = item.get('airport_country', '')
                service_type = item.get('service_type', False)
                service_date = item.get('service_date', 0)
                response_status = item.get('response_status', '')
                enquiry_status = item.get('enquiry_status', '')
                enquiry = item.get('enquiry', False)
                mail_content += '''<tr>'''

                mail_content += '''<td align="center"><span>#</span>%s</td>''' % name
                mail_content += '''<td align="center">%s</td>''' % traveler_name
                mail_content += '''<td align="center">%s</td>''' % \
                                str(airport_name + ''' (''' + airport_code + ''') ''' + ''' / ''' + airport_country)
                mail_content += '''<td align="center">%s</td>''' % str(service_type and service_type.name or '')
                if service_type.is_arrival or service_type.is_transit:
                    mail_content += '''<td align="center">%s</td>''' % enquiry.arrival_date_str
                elif service_type.is_departure or service_type.is_transit:
                    mail_content += '''<td align="center">%s</td>''' % enquiry.departure_date_str
                else:
                    mail_content += '''<td align="center"></td>'''
                mail_content += '''<td align="center">%s</td>''' % response_status
                mail_content += '''<td align="center">%s</td>''' % enquiry_status
                mail_content += '''</tr>'''

            mail_content += '''</table>'''

            main_content = {
                'subject': _("Tomorrow service's Details"),
                'email_from': self.env.company and self.env.company.partner_id and self.env.company.partner_id.email or '',
                'body_html': mail_content,
                'email_to': email_to,
            }
            mail_id = self.env['mail.mail'].create(main_content)
            mail_id.send()
        return True

    @api.depends('estimated_service_fee',
                 'company_currency_id',
                 'total_estimated_service_fee')
    def number_to_words(self):
        for record in self:
            amount = ""
            if record.company_currency_id:
                amount = record.company_currency_id.amount_to_text(record.total_estimated_service_fee)
            record.estimated_service_fee_words = amount

    @api.depends('adults_count', 'children_count', 'infants_count')
    def compute_total_travelers(self):
        for record in self:
            record.travelers_count = (record.adults_count or 0) + (record.children_count or 0) \
                                     + (record.infants_count or 0)

    @api.depends('country_id')
    def get_country_code(self):
        for record in self:
            if record.country_id:
                record.country_code = '+' + str(record.country_id.phone_code)

    @api.depends('quotation_id', 'quotation_id.invoice_count', 'invoice_ids')
    def compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)
            if record.invoice_count > 0:
                record.invoice_created = True
            else:
                record.invoice_created = False

    @api.depends('quotation_id', 'quotation_id.invoice_count',
                 'quotation_id.invoice_ids',
                 'sale_order_ids', 'sale_order_ids.invoice_ids')
    def get_invoice_id(self):
        for record in self:
            for quotation_id in record.sale_order_ids:
                if quotation_id.create_quotation_bool_0:
                    if quotation_id.mapped('invoice_ids'):
                        record.invoice_created = True
                        record.invoice_id = quotation_id.mapped('invoice_ids')[-1]

    @api.depends('service_type_id',
                 'departure_date',
                 'arrival_date',
                 'arrival_date_str',
                 'departure_date_str')
    def compute_service_date(self):
        for rec in self:
            services_on = ''
            # service_date = rec.service_date
            arrival_date = rec.arrival_date_str or ''
            departure_date = rec.departure_date_str or ''
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    if arrival_date:
                        services_on = str(arrival_date)
                        # service_date = rec.arrival_date
                elif rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    if departure_date:
                        services_on = str(departure_date)
                        # service_date = rec.departure_date
                elif rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    if arrival_date and departure_date:
                        if arrival_date != departure_date:
                            services_on = str(arrival_date) + ' and ' + str(departure_date)
                            # service_date = rec.arrival_date
                        else:
                            services_on = str(arrival_date)
                            # service_date = rec.arrival_date
            rec.services_on = services_on
            # rec.service_date = service_date

    @api.depends('invoice_id',
                 'invoice_id.invoice_payments_widget',
                 'invoice_id.amount_residual',
                 'invoice_id.amount_total',
                 'invoice_id.amount_total',
                 'invoice_id.move_type',
                 'invoice_id.payment_state',
                 'invoice_count')
    def get_payment_status(self):
        for rec in self:
            payment_status = 'not_paid'
            payment_done = False
            invoice_payments_widget = False
            payment_amount = 0
            pay_ser_category = False
            if rec.invoice_id:
                # if rec.invoice_id.payment_id:
                invoice_payments_widget = rec.invoice_id.invoice_payments_widget
                payment_amount = rec.invoice_id.amount_total - rec.invoice_id.amount_residual
                payment_status = rec.invoice_id.payment_state
                if rec.invoice_id.payment_state == 'paid' and rec.invoice_id.move_type in (
                        'out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
                    payment_done = True
                if rec.invoice_id.invoice_line_ids and rec.invoice_id.invoice_line_ids[0] and \
                        rec.invoice_id.invoice_line_ids[0].product_id:
                    pay_ser_category = rec.invoice_id.invoice_line_ids[0].product_id.id
            rec.write({
                'payment_status': payment_status,
                'payment_done': payment_done,
                'invoice_payments_widget': invoice_payments_widget,
                'payment_amount': payment_amount,
                'estimated_service_fee': payment_amount,
                'service_category_id': pay_ser_category,
            })

    @api.depends('invoice_ids',
                 'invoice_ids.amount_residual',
                 'invoice_ids.amount_total',
                 'invoice_ids.amount_total',
                 'invoice_ids.move_type',
                 'invoice_ids.payment_state',
                 'invoice_count')
    def total_get_payment_status(self):
        for rec in self:
            payment_amount = 0
            for invoice_id in rec.invoice_ids:
                payment_amount += invoice_id.amount_total - invoice_id.amount_residual
            rec.total_estimated_service_fee = payment_amount

    @api.depends('travel_class_id', 'uaa_services_id')
    def get_class_of_travel(self):
        for rec in self:
            class_of_travel = False
            if rec.uaa_services_id == self.env.ref('sr_uaa_main.meet_greet_airport_service_name'):
                if rec.travel_class_id:
                    if rec.travel_class_id == self.env.ref("sr_uaa_main.economy_class_travel"):
                        class_of_travel = 'economy'
                    if rec.travel_class_id == self.env.ref("sr_uaa_main.first_class_travel"):
                        class_of_travel = 'first_class'
                    if rec.travel_class_id == self.env.ref("sr_uaa_main.premium_economy_class_travel"):
                        class_of_travel = 'premium_economy'
                    if rec.travel_class_id == self.env.ref("sr_uaa_main.business_class_travel"):
                        class_of_travel = 'business_class'
            rec.class_of_travel = class_of_travel

    @api.depends('uaa_services_id')
    def get_uaa_services(self):
        for rec in self:
            rec.services = False
            if rec.uaa_services_id:
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services"):
                    rec.services = 'meet_assist'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_hotel_services"):
                    rec.services = 'airport_hotel'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_lounge_services"):
                    rec.services = 'airport_lounge'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    rec.services = 'airport_transfer'

    @api.depends('service_type_id')
    def get_service_type(self):
        for rec in self:
            rec.service_type = False
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    rec.service_type = 'arrival'
                if rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    rec.service_type = 'departure'
                if rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    rec.service_type = 'transit'

    def compute_quotation_count(self):
        quotation_id = []
        for record in self:
            quotation_ids = self.env['sale.order'].search([('enquiry_id', '=', record.id)])
            record.quotation_count = quotation_ids and len(quotation_ids.ids) or 0
            for id in quotation_ids:
                quotation_id.append(id.id)
            record.quotation_ids = [(6, 0, quotation_id)]

    @api.depends('quotation_id',
                 'quotation_id.state',
                 'payment_done',
                 'payment_received',
                 'invoice_id',
                 'invoice_id.payment_state',
                 'invoice_id.move_type',
                 'invoice_id.amount_residual',
                 'resp_status_change',
                 'response_status',
                 'modify_enquiry')
    def get_response_status(self):
        for rec in self:
            response_status_id = self.env.ref("sr_uaa_main.new_enquiry_response_status").id
            response_status = 'new_enquiry'
            if rec.quotation_id:
                if rec.quotation_id.state != 'draft':
                    response_status_id = self.env.ref("sr_uaa_main.payment_link_sent_response_status").id
                    response_status = 'payment_link_send'
            if rec.payment_received:
                response_status_id = self.env.ref("sr_uaa_main.payment_received_response_status").id
                response_status = 'payment_received'
            if rec.payment_done:
                response_status_id = self.env.ref("sr_uaa_main.payment_completed_response_status").id
                response_status = 'payment_completed'

            if rec.response_status == 'service_completed':
                response_status_id = self.env.ref("sr_uaa_main.service_completed_response_status").id
                response_status = 'service_completed'

            if rec.response_status == 'unfortunate_mail':
                response_status_id = self.env.ref("sr_uaa_main.unfortunate_mail_response_status").id
                response_status = 'unfortunate_mail'

            if rec.response_status == 'service_not_rendered_refunded':
                response_status_id = self.env.ref("sr_uaa_main.service_not_rendered_refunded_response_status").id
                response_status = 'service_not_rendered_refunded'

            if rec.response_status == 'service_not_rendered_not_refunded':
                response_status_id = self.env.ref("sr_uaa_main.service_not_rendered_not_refunded_response_status").id
                response_status = 'service_not_rendered_not_refunded'

            if rec.invoice_id:
                if rec.invoice_id.payment_state == 'paid' and rec.invoice_id.move_type in (
                        'out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
                    if rec.invoice_id.amount_residual == 0:
                        # response_status_id = self.env.ref("sr_uaa_main.service_confirmed_response_status").id
                        response_status_id = self.env.ref("sr_uaa_main.payment_completed_response_status").id
                        response_status = 'payment_completed'
            if rec.resp_status_change == 'send_service_req':
                response_status_id = self.env.ref("sr_uaa_main.service_request_sent_response_status").id
                response_status = 'send_service_req'

            if rec.resp_status_change == 'confirm_service':
                response_status_id = self.env.ref("sr_uaa_main.service_confirmed_response_status").id
                response_status = 'confirm_service'

            if rec.resp_status_change == 'confirmation_voucher_send':
                response_status_id = self.env.ref("sr_uaa_main.confirmation_voucher_sent_response_status").id
                response_status = 'confirmation_voucher_send'

            if rec.resp_status_change == 'unfortunate_mail':
                response_status_id = self.env.ref("sr_uaa_main.unfortunate_mail_response_status").id
                response_status = 'unfortunate_mail'

            if rec.resp_status_change == 'cancelled':
                response_status_id = self.env.ref("sr_uaa_main.cancelled_response_status").id
                response_status = 'cancelled'
                rec.write({
                    'status': 'close'
                })
            rec.write({
                'response_status_id': response_status_id or False,
                'response_status': response_status or False,
            })

    name = fields.Char('Booking Number', readonly=True, default='NEW')
    notified_customer = fields.Boolean('Notified Customer', default=False, readonly=False)
    invoice_id = fields.Many2one('account.move', 'Invoice Number',
                                 compute="get_invoice_id",
                                 store=True, readonly=True)
    # invoice_number = fields.Char('Invoice Number')
    airport_id = fields.Many2one('admin.airport', 'Airport Name')
    lounge_name = fields.Char('Lounge Name', )
    service_type = fields.Selection([('arrival', 'Arrival Service'),
                                     ('departure', 'Departure Service'),
                                     ('transit', 'Transit Service')],
                                    string='Service Type', compute="get_service_type", store=True)
    service_type_id = fields.Many2one('airport.service.type', 'Service Type')
    country_id = fields.Many2one('res.country', 'Country')
    country_code = fields.Char('Country Phone Code', compute="get_country_code", store=True)

    services = fields.Selection([('meet_assist', 'Meet & Assist'),
                                 ('airport_hotel', 'Airport Hotel'),
                                 ('airport_lounge', 'Airport Lounge'),
                                 ('airport_transfer', 'Airport Transfer')
                                 ], string='Service', compute='get_uaa_services', store=True)
    resp_status_change = fields.Selection([('send_service_req', 'Send Service Request'),
                                           ('confirm_service', 'Confirm Service'),
                                           ('confirmation_voucher_send', 'Confirmation Voucher Sent'),
                                           ('unfortunate_mail', 'Unfortunate Mail'),
                                           ('cancelled', 'Cancelled')], string='Response Status Change')
    response_status = fields.Selection([('new_enquiry', 'New Enquiry'),
                                        ('payment_link_send', 'Quotation Sent'),
                                        ('additional_payment_link_send', 'Additional Quotation Sent'),
                                        ('payment_completed', 'Payment Completed'),
                                        ('payment_received', 'Payment Completed'),
                                        ('confirm_service', 'Service Confirmed'),
                                        ('send_service_req', 'Service Requested'),
                                        ('service_completed', 'Service completed'),
                                        ('service_not_rendered_refunded', 'Service not rendered and refunded'),
                                        ('service_not_rendered_not_refunded', 'Service not rendered and not refunded'),
                                        ('confirmation_voucher_send', 'Confirmation Voucher Sent'),
                                        ('unfortunate_mail', 'Unfortunate Mail'),
                                        ('cancelled', 'Cancelled')], string='Response Status',
                                       compute='get_response_status', store=True)
    can_response_status = fields.Selection([('new_enquiry', 'New Enquiry'),
                                            ('payment_link_send', 'Quotation Sent'),
                                            ('additional_payment_link_send', 'Additional Quotation Sent'),
                                            ('payment_completed', 'Payment Completed'),
                                            ('payment_received', 'Payment Completed'),
                                            ('confirm_service', 'Service Confirmed'),
                                            ('send_service_req', 'Service Requested'),
                                            ('service_completed', 'Service completed'),
                                            ('service_not_rendered_refunded', 'Service not rendered and refunded'),
                                            ('service_not_rendered_not_refunded',
                                             'Service not rendered and not refunded'),
                                            ('confirmation_voucher_send', 'Confirmation Voucher Sent'),
                                            ('unfortunate_mail', 'Unfortunate Mail'),
                                            ('cancelled', 'Cancelled')],
                                           string='Canceled Time Response Status')

    uaa_services_id = fields.Many2one('uaa.services', 'Service')

    services_ids = fields.Many2many('airport.service.name', 'airport_enquiry_service_rel', 'enquiry_id',
                                    'service_id', string="Services")
    class_of_travel = fields.Selection([('economy', 'Economy'),
                                        ('premium_economy', 'Premium Economy'),
                                        ('business_class', 'Business Class'),
                                        ('first_class', 'First Class'),
                                        ],
                                       string='Class of Travel', compute="get_class_of_travel", store=True)
    travel_class_id = fields.Many2one('travel.class', 'Class of Travel')
    departure_flight_number = fields.Char('Departure Flight Number')
    departure_date = fields.Datetime('Departure Date')  # DON't USE THIS FIELD
    departure_date_str = fields.Char('Departure Date')
    pickup_date = fields.Datetime('Pickup Date')  # DON't USE THIS FIELD
    pickup_date_str = fields.Char('Pickup Date')
    arrival_flight_number = fields.Char('Arrival Flight Number')
    arrival_date = fields.Datetime('Arrival Date')  # DON't USE THIS FIELD
    arrival_date_str = fields.Char('Arrival Date')
    entry_time = fields.Char('Entry Time')

    travelers_count = fields.Integer('No. of Travellers', store=True, compute="compute_total_travelers", readonly=True)
    adults_count = fields.Integer('No. of Adults', default=0)
    infants_count = fields.Integer('No. of Infants', default=0)
    luggage_count = fields.Integer('No. of luggage', default=0)
    children_count = fields.Integer('No. of Children (2-12 Years)', default=0)
    hours_count = fields.Float('No. of hours of stay', default=0.00)

    traveler_name = fields.Char('Name of the Traveller', required=True)
    email = fields.Char('Email', required=True)
    contact_number = fields.Char('Contact No')
    add_contact_number = fields.Char('Additional Contact No')
    drivers_contact_number = fields.Char('Driver Contact No')
    enquiry_receive_date = fields.Date('Enquiry Receive Date')
    request_date = fields.Date('Request Date', default=fields.Date.today, readonly=True)
    service_date = fields.Date('Service Date', required=True,
                               index=True, tracking=3,
                               track_visibility='onchange')
    services_on = fields.Char('Services on', compute="compute_service_date", store=True)

    need_wheelchair = fields.Boolean('Need Wheelchair')
    is_booked = fields.Boolean('Is Booked')
    wheelchair_count = fields.Integer('No. of Wheelchair', default=1)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one("res.currency", string='Currency',
                                          default=lambda self: self.env.company.currency_id.id)

    status = fields.Selection([('new', 'New'),
                               ('open', 'Open'),
                               ('close', 'Closed')],
                              string='Enquiry Status',
                              default='new',
                              index=True, tracking=3,
                              track_visibility='onchange')

    can_status = fields.Selection([('new', 'New'),
                                   ('open', 'Open'),
                                   ('close', 'Closed')],
                                  string='Cancelled Enquiry Status', )

    status_comment_ids = fields.One2many('enquiry.status', 'airport_enquiry_id', 'Enquiry Status')
    customer_message = fields.Text('Customer Message')
    verified_by = fields.Many2one('res.users', 'Verified By')
    estimated_service_fee = fields.Float('Service Fee', default=0.00,
                                         compute="get_payment_status", store=True)
    total_estimated_service_fee = fields.Float('Total Service Fee', default=0.00,
                                               compute="total_get_payment_status", store=True)
    estimated_service_fee_words = fields.Char('Service Fee (in words)',
                                              readonly=True,
                                              store=True, compute="number_to_words")
    payment_done = fields.Boolean('Payment Done', default=False, compute="get_payment_status", store=True)
    payment_received = fields.Boolean('Payment Received', default=False)
    payment_status = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", readonly=True, copy=False, tracking=True,
        compute="get_payment_status", store=True)
    invoice_payments_widget = fields.Text(groups="account.group_account_invoice,account.group_account_readonly",
                                          compute="get_payment_status", store=True)
    payment_amount = fields.Monetary(string='Amount Paid', currency_field='company_currency_id', readonly=True,
                                     compute="get_payment_status", store=True)

    response_status_id = fields.Many2one('response.status.name', string="Response Status",
                                         compute="get_response_status", store=True)
    can_response_status_id = fields.Many2one('response.status.name',
                                             string="Cancelled time Response Status",
                                             copy=False, default=False)

    sale_order_ids = fields.One2many('sale.order', 'enquiry_id', string='Quotations')
    quotation_id = fields.Many2one('sale.order', string="Quotation")
    quotation_count = fields.Integer(string="Quotation Count", compute="compute_quotation_count")

    invoice_ids = fields.One2many('account.move', 'enquiry_id', string="Invoices")
    invoice_count = fields.Integer(string="Invoice Count", compute="compute_invoice_count", store=True)
    invoice_created = fields.Boolean(string="Invoice Created")
    response_bool = fields.Boolean(string="Response Bool", default=False)

    enquiry_partner_id = fields.Many2one('res.partner', string="Partner")

    pick_up_airport_id = fields.Many2one('admin.airport', 'Pick Up Location')
    drop_off_airport_id = fields.Many2one('admin.airport', 'Drop Off Location')
    pick_up_location = fields.Char('Pick Up Location')
    drop_off_location = fields.Char('Drop Off Location')
    service_provider_book_number = fields.Char('Service Provider Booking Number')
    services_charges_ids = fields.One2many('enquiry.service.line', 'enquiry_id', string="Service Charges")
    spp_status = fields.Boolean('Service provider Payment', default=False, store=True)

    cancel_reason = fields.Text(string='Cancel Reason')
    cancel_date = fields.Date(string='Cancel Date')
    emergency_number = fields.Char('Emergency Contact')
    status_history_ids = fields.One2many('status.history.line', 'enquiry_id')
    service_category_id = fields.Many2one('product.product', string='Service Category')
    today = fields.Datetime.today()
    modify_enquiry = fields.Boolean('Modify', default=True)
    cancel_records = fields.Boolean('Cancel', default=False)
    new_qtc_records = fields.Boolean('Cancel', default=False)
    booking_ref_no = fields.Char('Booking Reference No')
    quotation_ids = fields.Many2many('sale.order', 'sale_order_rel', 'enquiry_id',
                                     'quotation_enq_id', string="Quotation", compute="compute_quotation_count")
    meeting_point = fields.Char('Meeting Point')

    created_timezone = fields.Char('TimeZone')  # DON't USE THIS FIELD
    cancel_new = fields.Boolean(string='Cancel in New Status',
                                copy=False, default=False)

    def change_date_to_string(self):
        enquiry_ids = self.env['airport.enquiry'].sudo().search([])
        count_total = len(enquiry_ids.ids)
        count = 0
        for enquiry_id in enquiry_ids:
            count += 1
            _logger.info('Import %s -> %s', count, count_total)
            if enquiry_id.arrival_date:
                enquiry_id.arrival_date_str = self.convert_local_time_to_utc(enquiry_id, enquiry_id.arrival_date)
            if enquiry_id.departure_date:
                enquiry_id.departure_date_str = self.convert_local_time_to_utc(enquiry_id, enquiry_id.departure_date)

    # @api.onchange("email")
    # def _onchange_email(self):
    #     for rec in self:
    #         if self.email:
    #             enq_id = self.env['airport.enquiry'].search([('name', '=', rec.name)])
    #             partner_id = self.env['res.partner'].sudo().search([
    #                 ('email', '=', self.email),
    #                 ('account_type', '=', 'privilege_customer'),
    #             ], limit=1)
    #             quotation_ids = self.env['sale.order'].search([('enquiry_id', '=', enq_id.id)])
    #             if quotation_ids:
    #                 for quotation in quotation_ids:
    #                     if partner_id:
    #                         quotation.partner_id = partner_id.id
    #                         enq_id.enquiry_partner_id = partner_id.id
    #                     else:
    #                         quotation.partner_id.email = self.email

    @api.constrains('traveler_name', 'contact_number', 'add_contact_number', 'arrival_date', 'departure_date',
                    'arrival_flight_number', 'departure_flight_number', 'email')
    def validation(self):
        regex_pattern = r'(?<![\dA-Z])(?!\d{2})[A-Z\d]{2}\s?\d{1,4}(?!\d)'
        regex_email = re.compile(
            r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")

        for rec in self:
            # if rec.traveler_name:
            #     name = rec.traveler_name.split(' ')
            #     for txt in name:
            #         if not txt.isalpha():
            #             raise UserError(_('Invalid Traveller Name'))

            # if rec.contact_number and rec.country_code:
            #     pn_number = str(rec.country_code + rec.contact_number)
            #     my_number = phonenumbers.parse(pn_number)
            #     if not phonenumbers.is_valid_number(my_number):
            #         raise UserError(_('Invalid Contact No.'))
            #
            # if rec.add_contact_number and rec.country_code:
            #     pn_number = str(rec.country_code + rec.add_contact_number)
            #     my_number = phonenumbers.parse(pn_number)
            #     if not phonenumbers.is_valid_number(my_number):
            #         raise UserError(_('Invalid Additional Contact No.'))

            if rec.email:
                if not re.fullmatch(regex_email, rec.email):
                    raise UserError(_('Invalid Email Address'))

            # if rec.arrival_date:
            #     if rec.arrival_date < self.today:
            #         raise ValidationError(_("Invalid Arrival Date : "
            #                                 "The date must be larger than or equal to today's date"))

            # if rec.departure_date:
            #     if rec.departure_date < self.today:
            #         raise ValidationError(_("Invalid Departure Date: "
            #                                 "The date must be larger than or equal to today's date"))

            # if rec.arrival_flight_number:
            #     if not re.fullmatch(regex_pattern, rec.arrival_flight_number):
            #         raise ValidationError(_("Invalid Arrival Flight No."))
            #
            # if rec.departure_flight_number:
            #     if not re.fullmatch(regex_pattern, rec.departure_flight_number):
            #         raise ValidationError(_("Invalid Departure Flight No."))

    def find_duplicate_enquiry(self, vals):
        service_date = vals.get('service_date', '')
        traveler_name = vals.get('traveler_name', '')
        email = vals.get('email', '')
        service_type_id = vals.get('service_type_id', '')
        # request_date = vals.get('request_date')
        airport_id = vals.get('airport_id', '')
        if service_date and isinstance(service_date, str):
            service_date = datetime.strptime(service_date, "%Y-%m-%d").date()
        elif service_date:
            service_date = service_date.date()
        if service_date and traveler_name and email and \
                service_type_id and airport_id:
            dom = [
                ('service_date', '=', service_date),
                ('traveler_name', '=', traveler_name),
                ('email', '=', email),
                ('service_type_id', '=', service_type_id),
                # ('request_date', '=', request_date),
                ('airport_id', '=', airport_id),
            ]
            enq_ids = self.search(dom)
            if enq_ids:
                raise UserError(_('Enquiry is already booked, Booking no %s: Please contact %s' % (enq_ids[0].name,
                                                                                                   self.env.company.email or self.env.company.name)))

    @api.model
    def create(self, vals_list):
        self.find_duplicate_enquiry(vals_list)
        # ('name', '=', vals_list.get('traveler_name')),
        partner_id = self.env['res.partner'].sudo().search([
            ('email', '=', vals_list.get('email')),
            ('mobile', '=', vals_list.get('contact_number')),
            ('account_type', '=', 'privilege_customer'),
        ])
        if partner_id:
            vals_list.update({
                'enquiry_partner_id': partner_id.id
            })

        # if vals_list.get('services') != 'meet_assist':
        #     services_id = self.env.ref('sr_uaa_main.general_airport_service_name')
        #     services_ids = []
        #     if services_id:
        #         services_ids.append(services_id.id)
        #     vals_list['services_ids'] = [(6, 0, services_ids)]
        if not vals_list.get('created_timezone', False):
            vals_list.update({
                'created_timezone': self.env.context.get("tz") or self.env.user.sudo().tz or "UTC"
            })

        if vals_list.get('uaa_services_id', False):
            if vals_list.get('uaa_services_id') == self.env.ref("sr_uaa_main.airport_transfer_services").sudo().id:
                if vals_list.get('service_type_id', False):
                    if vals_list.get('service_type_id') == self.env.ref("sr_uaa_main.arrival_service_type").sudo().id:
                        if vals_list.get('pick_up_airport_id', False):
                            vals_list.update({
                                'airport_id': int(vals_list.get('pick_up_airport_id')),
                            })
                    if vals_list.get('service_type_id') == self.env.ref("sr_uaa_main.departure_service_type").sudo().id:
                        if vals_list.get('drop_off_airport_id', False):
                            vals_list.update({
                                'airport_id': int(vals_list.get('drop_off_airport_id')),
                            })
        vals_list.update({
            'name': self.env['ir.sequence'].sudo().next_by_code('airport.bookings'),
            'modify_enquiry': False
        })

        # if vals_list.get('service_date', False):
        #     if datetime.strptime(str(vals_list.get('service_date')), '%Y-%m-%d').date() < fields.Date.today():
        #         raise UserError(_(
        #             "Service Date should be greater than today"))
        res = super(AirportEnquiry, self).create(vals_list)

        res.create_status_history(vals_list)

        template = self.env.ref('sr_uaa_main.email_template_thankyou_mail')
        parm_pool = self.env['ir.config_parameter'].sudo()
        base_url = parm_pool.get_param('web.base.url', default='https://localhost:8069')
        if template and res.email:
            description = """
        <table border="0" style="width:100%">
    <tbody>
        <tr>
            <td style="background-color: rgb(14, 180, 223)">
            <div style="background-color: rgb(14, 180, 223); float: left; padding: 20px; text-align: left"><a
                        href='"""
            description += self.env.company.website or ''
            description += """' target="_blank" rel="noreferrer">
                                    <img src='"""
            description += str(base_url + '/sr_uaa_main/static/src/images/new_logo.png')
            description += """'
                                alt=' """

            description += self.env.company.name or ''
            description += """' style="width: 150px"/></a></div>
                <div
                    style="background-color: rgb(14, 180, 223); float: right; padding: 30px 20px 20px 0px; text-align: right">
                    <h1
                        style="font-size: 18px; margin: 0px; font-family: Roboto, sans-serif; font-weight: 400; color: rgb(255, 255, 255); letter-spacing: 1px">
                        Booking ID : """
            description += res.name
            description += """</h1>
                </div>
            </td>
        </tr>
        <tr style="background-color:rgb(217,221,222);color:rgb(33,37,41);">
                    <td style="padding-left: 20px;">
                    <div style = "margin-top: 10px !important;">
                        """
            description += """
                    <h2><b>Dear """
            description += res.traveler_name + ","
            description += """</b></h2>
                    """
            description += self.env.ref("sr_uaa_main.uaa_thank_you_mail").body or ''
            description += """
                    </div>
                    </td>
        </tr>
        <tr>
            <td
                style="padding: 10px; background-color: rgb(14, 180, 223); vertical-align: top; border-width: 0px 1px 1px; border-right-style: solid; border-bottom-style: solid; border-left-style: solid; border-right-color: rgb(14, 180, 223); border-bottom-color: rgb(14, 180, 223); border-left-color: rgb(14, 180, 223); text-align: center">
                <h1
                    style="font-size: 14px; margin-top: 10px; font-family: Roboto, sans-serif; font-weight: 400; color: rgb(255, 255, 255); letter-spacing: 1px">
                    Visit<span class="v1Apple-converted-space">&nbsp;</span><a
                        href='"""
            description += self.env.company.website or ''
            description += """'target="_blank"
                                rel="noreferrer">"""
            description += self.env.company.website or ''
            description += """</a></h1>
                        <p
                            style="font-size: 14px; font-family: Roboto, sans-serif; font-weight: 400; letter-spacing: 2px; margin: 0px 0px; color: rgb(255, 255, 255)">
                            For any feedback, please email us:<span class="v1Apple-converted-space">&nbsp;</span><a
                                href="mailto:'"""
            description += "service@mailuaa.com"
            description += """'"
                                style="color: rgb(255, 255, 255); display: inline-block; text-decoration: none"
                                onclick="return rcmail.command('compose','service@universalairportassistance.com',this)"
                                rel="noreferrer">"""
            # description += self.env.company.email or ''
            description += "service@mailuaa.com"
            description += """</a></p>
            </td>
        </tr>
    </tbody>
</table>
                    """

            template.write({
                'body_html': description,
                'email_to': res.email or '',
                'email_from': self.env.company and self.env.company.partner_id and self.env.company.partner_id.email or '',

            })
            mail_id = template.sudo().send_mail(res.id, force_send=True)
            res.message_post(body="Thankyou Mail send successfully")

        res.send_enquiry_mail_to_company()

        return res

    def write(self, vals):
        uaa_services_id = vals.get('uaa_services_id') or (self.uaa_services_id and self.uaa_services_id.id) or False
        if uaa_services_id:
            if uaa_services_id != self.env.ref("sr_uaa_main.meet_greet_services").sudo().id:
                services_id = self.env.ref('sr_uaa_main.general_airport_service_name')
                services_ids = []
                if services_id:
                    services_ids.append(services_id.id)
                vals['services_ids'] = [(6, 0, services_ids)]
        # if vals.get('uaa_services_id',False) or vals.get('service_type_id',False):
        service_type_id = vals.get('service_type_id') or (self.service_type_id and self.service_type_id.id) or False
        # uaa_service_id = vals.get('uaa_services_id') or (self.uaa_services_id and self.uaa_services_id.id) or False
        if service_type_id and uaa_services_id:
            if uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services").sudo().id:
                airport_id = False
                if service_type_id == self.env.ref("sr_uaa_main.arrival_service_type").sudo().id:
                    airport_id = vals.get('pick_up_airport_id') or (
                            self.pick_up_airport_id and self.pick_up_airport_id.id) or False
                elif service_type_id == self.env.ref("sr_uaa_main.departure_service_type").sudo().id:
                    airport_id = vals.get('drop_off_airport_id') or (
                            self.drop_off_airport_id and self.drop_off_airport_id.id) or False
                vals.update({
                    'airport_id': airport_id
                })

        if 'response_status_id' in vals.keys() or 'status' in vals.keys():
            self.create_status_history(vals)

        if vals.get('traveler_name'):
            sale_ids = self.env['sale.order'].search([('enquiry_id', '=', self.id)])
            for line in sale_ids:
                line.traveler_name = vals.get('traveler_name')

        #####Commented for now, need to send and modfiy the enquiry details
        # if vals.get('modify_enquiry') and self.quotation_id and self.invoice_id:
        #     self.action_cancel_quotation_and_invoice()
        #     self.quotation_id = False
        #     self.invoice_id = False
        #     self.payment_received = False
        #     self.payment_done = False
        #     self.response_status = False
        #     self.resp_status_change = False

        res = super(AirportEnquiry, self).write(vals)
        params = vals.keys()
        modify_list = ['traveler_name', 'email', 'contact_number',
                       'service_type_id', 'services_ids', 'airport_id',
                       'travel_class_id', 'departure_flight_number',
                       'departure_date_str', 'arrival_date_str', 'modify_enquiry',
                       'arrival_flight_number', 'adults_count',
                       'children_count', 'infants_count', 'luggage_count',
                       'children_count', 'travelers_count', 'wheelchair_count']
        if vals.get('modify_enquiry'):
            if list(set(params).intersection(modify_list)):
                self.send_enquiry_mail_to_company(from_write=True)

        # if self.service_date:
        #     if self.service_date < fields.Date.today():
        #         raise UserError(_(
        #             "Service Date should be greater than today"))
        return res

    # def action_confirm(self):
    #     self.write({'status': 'confirm'})

    def get_booking_confirmation_sequence(self):
        booking_sequence = ''
        for rec in self:
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    booking_sequence = '#UA'
                elif rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    booking_sequence = '#UD'
                elif rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    booking_sequence = '#UT'
            booking_sequence += f"{rec.create_date.month:02}"
            if rec.name:
                sequence_code = ''.join(ch for ch in rec.name if ch.isdigit())
                booking_sequence += sequence_code

            return booking_sequence

    def change_status_to_cancel(self):
        for rec in self:
            rec.resp_status_change = 'cancelled'

    def change_resp_stus_to_service_req_snd(self):
        for rec in self:
            rec.resp_status_change = 'send_service_req'

    def change_resp_stus_to_unfortunate_mail(self):
        for rec in self:
            rec.resp_status_change = 'unfortunate_mail'

    def confirm_service(self):
        for rec in self:
            rec.resp_status_change = 'confirm_service'

    def confirmation_voucher_send(self):
        for rec in self:
            rec.resp_status_change = 'confirmation_voucher_send'

    def change_status_to_close(self):
        for rec in self:
            rec.status = 'close'

    def check_enquiry_close(self):
        now = datetime.now()
        now_date = now.strftime("%Y-%m-%d %H:%M:%S")
        enquiry = self.env['airport.enquiry'].sudo().search(
            [('service_date', '<', now_date), ('status', '=', 'new')])
        if enquiry:
            for rec in enquiry:
                if rec.status == 'new':
                    rec.status = 'close'

    def convert_local_time_to_utc(self, enquiry, date=False):
        display_date_result = False
        if date:
            timezone = pytz.timezone((enquiry and enquiry.created_timezone) or 'Asia/Calcutta')
            event_date = pytz.UTC.localize(fields.Datetime.from_string(date))  # Add "+hh:mm" timezone
            display_date_result = event_date.astimezone(timezone)
            display_date_result = display_date_result.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return display_date_result

    def convert_local_time_to_utc_for_xml(self, date=False, type=False):
        final_date_result = False
        date_time_obj = False
        if type and date:
            if type == 'time':
                final_date_result = date.split() and len(date.split()) > 1 \
                                    and ' '.join(date.split()[1:]) or date or ''
            elif type == 'date':
                final_date_result = date.split() and len(date.split()) > 1 \
                                    and date.split()[0] or date or ''
            else:
                final_date_result = date
        return final_date_result

    # def get_company_currency(self):
    #     for rec in self:
    #         rec.company_currency_id = self.env.company.currency_id and self.env.company.currency_id.id or False
    #         rec.number_to_words()

    def action_cancel_quotation_and_invoice(self):
        if self.quotation_id:
            self.quotation_id.action_cancel()

        if self.invoice_id:
            adv_wiz = self.env['account.move.reversal'].sudo().with_context(active_ids=[self.invoice_id.id],
                                                                            active_model='account.move').create(
                {'reason': 'cancel'})
            adv_wiz.sudo().reverse_moves()
            self.invoice_id.action_post()

            journal_id = self.env['account.move'].search([('ref', '=', self.invoice_id.name)])
            if journal_id:
                jou_wiz = self.env['account.move.reversal'].sudo().with_context(active_ids=journal_id.id,
                                                                                active_model='account.move').create(
                    {'reason': 'cancel'})
                jou_wiz.sudo().reverse_moves()
        self.new_qtc_records = True

    # if self.new_qtc_records:
    #     self.response_status = 'new_enquiry'

    def get_service_charge(self):
        for rec in self:
            service_ids = []
            if rec.uaa_services_id and rec.service_type_id:
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services") or \
                        rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_hotel_services") or \
                        rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_lounge_services"):
                    if rec.airport_id:
                        service_ids = rec.airport_id.service_line_ids. \
                            filtered(lambda line: (line.uaa_services_id == rec.uaa_services_id) and
                                                  (line.service_type_id == rec.service_type_id))
                elif rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                        if rec.pick_up_airport_id:
                            rec.airport_id = rec.pick_up_airport_id.id
                            service_ids = rec.pick_up_airport_id.service_line_ids. \
                                filtered(lambda line: (line.uaa_services_id == rec.uaa_services_id) and
                                                      (line.service_type_id == rec.service_type_id))

                    if rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                        if rec.drop_off_airport_id:
                            rec.airport_id = rec.drop_off_airport_id.id
                            service_ids = rec.drop_off_airport_id.service_line_ids. \
                                filtered(lambda line: (line.uaa_services_id == rec.uaa_services_id) and
                                                      (line.service_type_id == rec.service_type_id))

            rec.services_charges_ids = [(5, 0, 0)]
            if service_ids:
                for service in service_ids:
                    vals = {
                        'airport_id': service.airport_id and service.airport_id.id or False,
                        # 'services': service.services or False,
                        'uaa_services_id': service.uaa_services_id and service.uaa_services_id.id or False,
                        'service_type_id': service.service_type_id and service.service_type_id.id or False,
                        # 'service_type': service.service_type or False,
                        'amount': service.amount or 0.0,
                        'service_category_id': service.service_category_id and service.service_category_id.id or False,
                        'description': service.description or False,
                    }
                    rec.services_charges_ids = [(0, 0, vals)]

    def view_quotation(self):
        # view_id = self.env.ref('sale.view_order_form').id
        # context = self._context.copy()
        # return {
        #     'name': 'Quotation',
        #     'view_type': 'form',
        #     'view_mode': 'tree',
        #     'views': [(view_id, 'form')],
        #     'res_model': 'sale.order',
        #     'view_id': view_id,
        #     'type': 'ir.actions.act_window',
        #     'res_id': self.quotation_id.id,
        #     'context': context, }

        self.ensure_one()
        sale_pool = self.env['sale.order']
        action = {
            'name': _("Quotation"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'context': {'create': False},
        }
        if self.quotation_count == 1:
            quotation_ids = sale_pool.search([('enquiry_id', '=', self.id)])
            action.update({
                'view_mode': 'form',
                'res_id': quotation_ids and quotation_ids.ids[0] or False,
            })
        else:
            quotation_ids = sale_pool.search([('enquiry_id', '=', self.id)])
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', quotation_ids.ids)],
                # 'domain': [('partner_id.name', '=', self.quotation_id.partner_id.name),
                #            ('partner_id.email', '=', self.quotation_id.partner_id.email)],
            })
        return action

    def action_view_invoice(self):
        self.ensure_one()
        action = {
            'name': _("Paid Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.invoice_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': ['|', ('id', 'in', self.invoice_ids.ids), ('reversed_entry_id', 'in', self.invoice_ids.ids)],
            })
        return action

    def view_payments(self):
        action = self.env.ref('account.action_account_payments')
        result = action.read()[0]
        result['domain'] = [('enquiry_id', '=', self.id)]

        return result

    def date_time_split(self):
        arrival_date_time = self.arrival_date_str
        departure_date_time = self.departure_date_str

        arrival_date = arrival_date_time and arrival_date_time.split() and (
                len(arrival_date_time.split()) > 1 and arrival_date_time.split()[0] or arrival_date_time) or ''
        arrival_time = arrival_date_time and arrival_date_time.split() and (
                len(arrival_date_time.split()) > 1 and ' '.join(
            arrival_date_time.split()[1:]) or arrival_date_time) or ''
        departure_date = departure_date_time and departure_date_time.split() and (
                len(departure_date_time.split()) > 1 and departure_date_time.split()[
            0] or departure_date_time) or ''
        departure_time = departure_date_time and departure_date_time.split() and (
                len(departure_date_time.split()) > 1 and ' '.join(
            departure_date_time.split()[1:]) or departure_date_time) or ''

        result_dict = {
            'arrival_date': arrival_date,
            'arrival_time': arrival_time,
            'departure_date': departure_date,
            'departure_time': departure_time,
        }

        return result_dict

    def check_create_quotation(self):
        for record in self:
            if record.enquiry_partner_id:
                errorstring = ''
                if record.enquiry_partner_id.name != record.traveler_name:
                    errorstring = 'Name'
                if record.enquiry_partner_id.email != record.email:
                    if errorstring:
                        errorstring += ', '
                        errorstring += 'Email'
                    else:
                        errorstring = 'Email'
                if record.enquiry_partner_id.mobile != record.contact_number:
                    if errorstring:
                        errorstring += ', '
                        errorstring += 'Mobile'
                    else:
                        errorstring = 'Mobile'
                if errorstring:
                    errorstring = 'Mismatch in fields ' + errorstring + '. Please Change in Customers.'
                    # return {
                    #     'type': 'ir.actions.act_window',
                    #     'name': 'Warning',
                    #     'view_mode': 'form',
                    #     'res_model': 'enquiry.warning',
                    #     'context': {'create': False, 'edit': False, 'delete': False, 'default_message': errorstring,
                    #                 'default_enquiry_id': record.id,
                    #                 'default_partner_id': record.enquiry_partner_id.id},
                    #     'target': 'new',
                    # }
            record.create_quotation()
            record.quotation_id.create_quotation_bool_0 = True
            view_id = self.env.ref('sale.view_order_form').id
            context = self._context.copy()
            # if record.quotation_id:
            #     record.modify_enquiry = False
            return {
                'name': 'Quotation',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'sale.order',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': self.quotation_id.id,
                'context': context, }

    def action_view_customer(self):
        for record in self:
            if record.enquiry_partner_id:
                compose_form_id = self.env.ref("sr_uaa_main.view_partner_form_inherit").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Customer',
                    'view_mode': 'form',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'res_model': 'res.partner',
                    'res_id': record.enquiry_partner_id.id,
                    'context': {'create': False, 'edit': True, 'delete': False},
                    # 'target': 'new',
                }

    def create_quotation(self):
        for record in self:
            if record.traveler_name:
                if not record.services_charges_ids:
                    raise UserError(_('Please Update Service Charges'))
                partner_id = False

                # if not record.enquiry_partner_id:
                #     partner_id = self.env['res.partner'].sudo().search([
                #         ('name', '=', record.traveler_name),
                #         ('email', '=', record.email),
                #         ('mobile', '=', record.contact_number),
                #         ('account_type', '=', 'privilege_customer'),
                #     ])
                # else:
                #     partner_id = record.enquiry_partner_id

                if record.enquiry_partner_id:
                    partner_id = record.enquiry_partner_id

                ##Need to check
                if not partner_id:
                    partner_id = self.env['res.partner'].sudo().search([
                        ('email', '=', record.email),
                        ('account_type', '=', 'privilege_customer'),
                    ], limit=1)
                    if partner_id:
                        partner_id.write({'name': record.traveler_name,
                                          'mobile': record.contact_number or '',
                                          })
                ####Verify

                if not partner_id:
                    partner_id = self.env['res.partner'].create({
                        'name': record.traveler_name,
                        'country_id': record.country_id and record.country_id.id or False,
                        'email': record.email or '',
                        'mobile': record.contact_number or '',
                        'account_type': 'privilege_customer',
                    })
                    record.enquiry_partner_id = partner_id.id
                sale_id = self.env['sale.order'].create({
                    'partner_id': partner_id.id or False,
                    'traveler_name': record.traveler_name,
                    'services_ids': [(6, 0, record.services_charges_ids and record.services_charges_ids.ids or [])],
                    'date_order': fields.Datetime.today(),
                    'service_type_id': record.service_type_id and record.service_type_id.id or False,
                    'uaa_services_id': record.uaa_services_id and record.uaa_services_id.id or False,
                    # 'country_id': record.country_id and record.country_id.id or False,
                })
                record.quotation_id = sale_id.id
                record.modify_enquiry = False
                sale_id.enquiry_id = record.id
                # record.status = 'open'
                for ser in record.services_charges_ids:
                    line_vals = {
                        'active_check': False,
                        'service_id': ser.id,
                        'description': ser.description or False,
                        'product_id': ser.service_category_id and ser.service_category_id.product_id and ser.service_category_id.product_id.product_variant_id and ser.service_category_id.product_id.product_variant_id.id or False,
                        'price_unit': ser.amount
                    }
                    sale_id.order_line = [(0, 0, line_vals)]
                # sale_id.action_confirm()
                record.message_post(body="Quotation created successfully")
                return {
                    'type': 'ir.actions.act_window',
                    'name': sale_id.name,
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'res_id': sale_id.id,
                    'context': "{'create': False}"
                }
            else:
                raise UserError(_('Traveller Name is Empty'))

    def button_attachment(self):
        for record in self:
            domain = [('res_model', '=', self._name),
                      ('res_id', '=', record.id)]
            if record.enquiry_partner_id:
                domain = ['|', '&', ('res_model', '=', self._name), ('res_id', '=', record.id),
                          '&', ('res_model', '=', 'res.partner'), ('res_id', '=', record.enquiry_partner_id.id)
                          ]
            return {
                'name': _('Attachment'),
                'domain': domain,
                'res_model': 'ir.attachment',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'kanban,tree,form',
                'view_type': 'form',
                'help': _('''<p class="oe_view_nocontent_create">
    
                                                                Attach
                            documents of your Enquiry.</p>'''),
                'limit': 80,
                'context': "{'default_res_model': '%s', 'default_res_id': %d}"
                           % (self._name, record.id)
            }

    def action_submit(self):
        for record in self:
            record = record.sudo()
            self.ensure_one()
            cancelled_enq = self.env.ref("sr_uaa_main.cancelled_response_status")
            if record.response_status_id and cancelled_enq and \
                    record.response_status_id.id == cancelled_enq.id:
                raise UserError(_('Enquiry was cancelled'))

            for invoice in self.invoice_ids:
                if invoice.payment_state != 'paid':
                    raise UserError(_('Make all invoices paid to continue...'))

            for quotation in self.sale_order_ids:
                if quotation.state in ['send', 'sale', 'done'] and quotation.invoice_status != 'invoiced':
                    raise UserError(_('Make all invoices paid to continue...'))

            if record.services == 'airport_lounge':
                validation_errors = []

                if not record.lounge_name and not record.entry_time:
                    validation_errors.append(_('Please enter Lounge Name and Entry Time to continue...'))
                else:
                    if not record.lounge_name:
                        validation_errors.append(_('Please enter Lounge Name to continue...'))

                    if not record.entry_time:
                        validation_errors.append(_('Please enter Entry Time to continue...'))

                if validation_errors:
                    raise UserError('\n'.join(validation_errors))

            body_html = ''
            template = self.env.ref('sr_uaa_main.email_template_booking_confirmation')
            if template:
                record.is_booked = True
                if record:
                    body_html += '''<span style = "color: #000 !important;">Dear ''' + str(
                        record.traveler_name) + ''',</span>'''

                    body_html += self.env.ref("sr_uaa_main.uaa_booking_confirmation_body").body or ''

                    body_html += '''
                                                                       <br/>
                                                                       <br/>
                                                                       <p>Thanks & Regards,</p>
                                                                       <p>''' + str(self.env.user.partner_id.name) + '''</p>
                                                                       '''
                    template.body_html = body_html
                    template.email_to = record.email
                    report_template_id = self.env.ref('sr_uaa_main.email_template_booking_confirmation')
                    lang = self.env.context.get('lang')
                    booking_report = self.env.ref('sr_uaa_main.action_report_booking_confirmation')
                    data_record = base64.b64encode(
                        self.env['ir.actions.report'].sudo()._render_qweb_pdf(
                            booking_report, [self.id], data=None)[0])
                    ir_values = {
                        'name': 'Booking Confirmation ' + self.name+'.pdf',
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'pdf',
                        'res_model': 'airport.enquiry',
                    }
                    attachment_id = self.env[
                        'ir.attachment'].sudo().create(
                        ir_values)
                    # data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf('sr_uaa_main.action_report_booking_confirmation', [self.id]))
                    # ir_values = {
                    #     'name': 'Booking Confirmation' + self.name,
                    #     'type': 'binary',
                    #     'datas': data_record,
                    #     'store_fname': data_record,
                    #     'mimetype': 'application/pdf',
                    #     'res_model': 'airport.enquiry',
                    # }
                    # attachment_id = self.env[
                    #     'ir.attachment'].sudo().create(
                    #     ir_values)
                    #
                    # data_record = report_template_id[0]
                    # ir_values = {
                    #     'name': "Booking Confirmation",
                    #     'type': 'binary',
                    #     'datas': data_record,
                    #     'store_fname': data_record,
                    #     'mimetype': 'application/pdf',
                    # }
                    # data_id = self.env['ir.attachment'].create(ir_values)
                    attachment_ids = [(6, 0, [attachment_id.id])]
                    ctx = {
                        'default_model': 'airport.enquiry',
                        'default_res_id': self.id,
                        'default_use_template': bool(report_template_id),
                        'default_template_id': report_template_id.id if report_template_id else None,
                        'default_composition_mode': 'comment',
                        'default_email_layout_xmlid': 'mail.mail_notification_paynow',
                        'default_attachment_ids': attachment_ids,
                        'force_email': True,
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

        return True

    def create_status_history(self, vals):
        for record in self:
            if 'status' in vals.keys():
                description = ''
                if vals.get('status', '') != record.status:
                    description = "Status : " + dict(self._fields['status'].selection).get(
                        record.status) + " --> " + dict(self._fields['status'].selection).get(vals.get('status', ''))
                elif vals.get('status', '') == 'new':
                    description = "Status : " + dict(self._fields['status'].selection).get(record.status)
                for history in record.status_history_ids:
                    if history.description.find(description) != -1:
                        description = ''
                if description:
                    vals_create = {
                        'user_id': self.env.user and self.env.user.id or False,
                        'status_change_time': fields.Datetime.now(),
                        'description': description,
                        'enquiry_id': record.id
                    }
                    self.env['status.history.line'].sudo().create(vals_create)

            if 'response_status_id' in vals.keys():
                description = ''
                if record.response_status_id and vals.get('response_status_id', '') != record.response_status_id.id:
                    response_status_id = self.env['response.status.name'].browse(vals.get('response_status_id'))
                    description = "Response Status : " + record.response_status_id.name + " --> " + response_status_id.name
                elif vals.get('response_status_id', '') == self.env.ref("sr_uaa_main.new_enquiry_response_status").id:
                    description = "Response Status : " + self.env.ref("sr_uaa_main.new_enquiry_response_status").name
                for history in record.status_history_ids:
                    if history.description.find(description) != -1:
                        description = ''
                if description:
                    vals_create = {
                        'user_id': self.env.user and self.env.user.id or False,
                        'status_change_time': fields.Datetime.now(),
                        'description': description,
                        'enquiry_id': record.id
                    }
                    self.env['status.history.line'].sudo().create(vals_create)

    def send_enquiry_mail_to_company(self, from_write=False):
        arrival_date_time = self.arrival_date_str
        departure_date_time = self.departure_date_str

        arrival_date = arrival_date_time and arrival_date_time.split() and (
                len(arrival_date_time.split()) > 1 and arrival_date_time.split()[0] or arrival_date_time) or ''
        arrival_time = arrival_date_time and arrival_date_time.split() and (
                len(arrival_date_time.split()) > 1 and ' '.join(
            arrival_date_time.split()[1:]) or arrival_date_time) or ''
        departure_date = departure_date_time and departure_date_time.split() and (
                len(departure_date_time.split()) > 1 and departure_date_time.split()[
            0] or departure_date_time) or ''
        departure_time = departure_date_time and departure_date_time.split() and (
                len(departure_date_time.split()) > 1 and ' '.join(
            departure_date_time.split()[1:]) or departure_date_time) or ''

        pickup_date_time = self.pickup_date_str
        airport_name = False
        if self.airport_id and self.airport_id.name:
            airport_name = self.airport_id.name
            if self.airport_id.code:
                airport_name += ' (' + self.airport_id.code + ') '
            if self.airport_id.country_id and self.airport_id.country_id.name:
                airport_country = self.airport_id.country_id.name
                airport_name += ' / ' + airport_country
        enquiry_company_template = self.env.ref('sr_uaa_main.email_template_enquiry_to_company')
        if enquiry_company_template and self.env.company and self.env.company.booking_email:
            subject = 'New Enquiry  | Universal Airport Assistance'
            description = ''

            if from_write:
                subject = 'Enquiry Updated  | Universal Airport Assistance'
                description += """<span style="color:black;">Hi,</span> <br/><span style="color:black;">The below booking has been updated. Details as follows</span><br/> <br/>"""
            else:
                description += """<span style="color:black;">Hi,</span> <br/><span style="color:black;">New Service Request has been submitted, Details as follows </span><br/> <br/>"""

            description += """<span style="color:black;">Booking Number : </span>"""
            description += """<b>"""
            description += self.name
            description += """</b>"""

            description += """<br/><span style="color:black;">Name : </span>"""
            description += """<b>"""
            description += self.traveler_name
            description += """</b>"""

            description += """<br/><span style="color:black;">Email : </span>"""
            description += """<b>"""
            description += self.email
            description += """</b>"""

            if self.country_code or 0 and self.contact_number or 0:
                description += """<br/><span style="color:black;">Phone No : </span>"""
                description += """<b>"""
                description += self.country_code + " " + self.contact_number or ''
                description += """</b>"""

            if self.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                if self.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    description += """<br/><span style="color:black;">Pick Up Location : </span>"""
                    description += """<b>"""
                    description += self.pick_up_airport_id.name
                    description += " " + "(" + self.pick_up_airport_id.code + ")"
                    description += " " + "/" + " " + self.pick_up_airport_id.country_id.name
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Drop Off Location : </span>"""
                    description += """<b>"""
                    description += self.drop_off_location
                    description += """</b>"""


                if self.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    description += """<br/><span style="color:black;">Pick Up Location : </span>"""
                    description += """<b>"""
                    description += self.pick_up_location
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Drop Off Location : </span>"""
                    description += """<b>"""
                    description += self.drop_off_airport_id.name
                    description += " " + "(" + self.drop_off_airport_id.code + ")"
                    description += " " + "/" + " " + self.drop_off_airport_id.country_id.name
                    description += """</b>"""


                if self.pickup_date_str:
                    description += """<br/><span style="color:black;">Pickup Date-Time: </span>"""
                    description += """<b>"""
                    description += str(pickup_date_time)
                    description += """</b>"""

            else:
                description += """<br/><span style="color:black;">Airport Name</span><span style="color:black;"> or</span> <span style="color:black;">Code : </span>"""
                description += """<b>"""
                description += airport_name
                description += """</b>"""

            if self.uaa_services_id:
                description += """<br/><span style="color:black;">Service : </span>"""
                description += """<b>"""
                description += self.uaa_services_id.name
                description += """</b>"""

            if self.services_ids:
                description += """<br/><span style="color:black;">Service Details : </span>"""
                description += """<b>"""
                count = 0
                for service in self.services_ids:
                    a = len(self.services_ids)
                    count += 1
                    description += service.name
                    if count != a:
                        description += ","
                description += """</b>"""

            description += """<br/><span style="color:black;">Service Type : </span>"""
            description += """<b>"""
            description += self.service_type_id and self.service_type_id.name
            description += """</b>"""

            description += """<br/><span style="color:black;>Service : </span>"""
            description += """<b>"""
            description += self.uaa_services_id and self.uaa_services_id.name
            description += """</b>"""

            if self.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services"):
                description += """<br/><span style="color:black;">Class of Travel : </span>"""
                description += """<b>"""
                description += self.travel_class_id and self.travel_class_id.name
                description += """</b>"""

            if self.service_type_id:
                if self.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    description += """<br/><span style="color:black;">Arrival Flight Number : </span>"""
                    description += """<b>"""
                    description += self.arrival_flight_number
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Arrival Date : </span>"""
                    description += """<b>"""
                    description += arrival_date
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Arrival Time : </span>"""
                    description += """<b>"""
                    description += arrival_time
                    description += """</b>"""

                if self.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    description += """<br/><span style="color:black;">Departure Flight Number : </span>"""
                    description += """<b>"""
                    description += self.departure_flight_number
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Departure Date : </span>"""
                    description += """<b>"""
                    description += departure_date
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Departure Time : </span>"""
                    description += """<b>"""
                    description += departure_time
                    description += """</b>"""

                if self.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    description += """<br/><span style="color:black;">Arrival Flight Number : </span>"""
                    description += """<b>"""
                    description += self.arrival_flight_number
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Arrival Date : </span>"""
                    description += """<b>"""
                    description += arrival_date
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Arrival Time : </span>"""
                    description += """<b>"""
                    description += arrival_time
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Departure Flight Number : </span>"""
                    description += """<b>"""
                    description += self.departure_flight_number
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Departure Date : </span>"""
                    description += """<b>"""
                    description += departure_date
                    description += """</b>"""

                    description += """<br/><span style="color:black;">Departure Time : </span>"""
                    description += """<b>"""
                    description += departure_time
                    description += """</b>"""

            if self.hours_count and self.hours_count > 0:
                description += """<br/><span style="color:black;">No. of hours of stay : </span>"""
                description += """<b>"""
                description += str(self.hours_count)
                description += """</b>"""

            description += """<br/><span style="color:black;">No. of Adults  : </span>"""
            description += """<b>"""
            description += str(self.adults_count)
            description += """</b>"""

            description += """<br/><span style="color:black;">No. of Children (2-12 years) : </span>"""
            description += """<b>"""
            description += str(self.children_count)
            description += """</b>"""

            description += """<br/><span style="color:black;">No. of Infants : </span>"""
            description += """<b>"""
            description += str(self.infants_count)
            description += """</b>"""

            description += """<br/><span style="color:black;">No. of Luggage : </span>"""
            description += """<b>"""
            description += str(self.luggage_count)
            description += """</b>"""

            if self.need_wheelchair:
                description += """<br/><span style="color:black;">No. of Wheelchair : </span>"""
                description += """<b>"""
                description += str(self.wheelchair_count)
                description += """</b>"""

            if self.customer_message:
                description += """<br/><span style="color:black;">Message : </span>"""
                description += """<b>"""
                description += str(self.customer_message)
                description += """</b>"""

            email_cc = []
            email_list = []
            if self.env.company and self.env.company.booking_cc:
                email_cc = self.env.company and self.env.company.booking_cc or ''
                email_list.append(email_cc)
                email_cc = email_list and ','.join(email_list) or ''
            else:
                email_cc = email_cc
            enquiry_company_template.write({
                'body_html': description,
                'email_to': self.env.company.booking_email or '',
                'email_from': self.env.company and self.env.company.partner_id \
                              and self.env.company.partner_id.email or '',
                'email_cc': email_cc or [],
                'subject': subject or '',

            })
            mail_id = enquiry_company_template.sudo().send_mail(self.id, force_send=True)
            self.message_post(body="Enquiry Created Mail send successfully")

    def send_custom_mail(self):
        self.ensure_one()
        cancelled_enq = self.env.ref("sr_uaa_main.cancelled_response_status")
        if self.response_status_id and cancelled_enq and \
                self.response_status_id.id == cancelled_enq.id:
            raise UserError(_('Enquiry was cancelled'))

        template = self.env.ref('sr_uaa_main.custom_send_mail_template')
        template_id = template.id
        email_to = ""
        if self.email:
            email_to = self.email

        subject = ""

        sender_address = ""

        template.write({
            'email_to': email_to,
            'subject': subject,
            'email_from': sender_address
        })

        ctx = {
            'default_model': 'airport.enquiry',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'target': 'new',
            'context': ctx,
        }

    def get_name_custom_function(self):
        name = self.airport_id.name_get()
        airport_name = ''
        for _, display_name in name:
            airport_name = display_name
        return airport_name

    def reset_enquiry_new(self):
        for record in self:
            if record.cancel_new:
                response_status_id = self.env.ref("sr_uaa_main.new_enquiry_response_status").id
                response_status = 'new_enquiry'
                record.write({
                    'cancel_new': False,
                    'status': 'new',
                    'response_status_id': response_status_id,
                    'response_status': response_status,
                    'resp_status_change': False,
                })
        return True
