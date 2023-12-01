# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 SEEROO IT SOLUTIONS PVT.LTD(<https://www.seeroo.com/>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import io


class AdditionalCharge(models.Model):
    _name = 'additional.charge.sale'
    _description = 'Additional Charge'

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one("res.currency", string='Currency', compute="get_company_currency",store=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')
    description = fields.Html('Description')
    enquiry_id = fields.Many2one('airport_enquiry','Enquiry')
    sale_id = fields.Many2one('sale.order','Sale Order',required=True)
    partner_id = fields.Many2one('res.partner','Customer',required=True)
    state = fields.Selection([
        ('sent', 'Sent'),
        ('payment_pending', 'Payment Pending'),
        ('payment_received', 'Payment Received'),
        ('payment_failed', 'Payment Failed')], string='Status')

    # @api.onchange('amount', 'description')
    # def get_additional_charge_values(self):
    #     for rec in self:
    #         if rec.amount and rec.amount > 0:
    #             amount = rec.amount
    #             description = ''
    #             if rec.description:
    #                 description = rec.description
    #             # results = {
    #             #     'amount': amount,
    #             #     'description': description}
    #             return amount
    #         # else:
    #         #     return False
    def get_payment_link(self):
        for rec in self:
            sale_id = rec.sale_id
            if sale_id:
                vals = {
                    'res_model': 'sale.order',
                    'description': 'charge-' + str(rec.id),
                    'res_id': sale_id.id or False,
                    'currency_id': rec.company_currency_id and rec.company_currency_id.id or False,
                    'partner_id': rec.partner_id and rec.partner_id.id or False,
                    'amount_max': round(rec.amount,2),
                    'amount': round(rec.amount,2),
                }
                payment_link_id = self.env['payment.link.wizard'].sudo().create(vals)
                return payment_link_id.link

    @api.depends('company_id')
    def get_company_currency(self):
        for rec in self:
            rec.company_currency_id = rec.company_id and rec.company_id.currency_id and rec.company_id.currency_id.id or False

    # def action_additional_charge_send(self):
    #
    #     template = self.env.ref('sr_uaa_main.email_template_id_additional_charge')
    #     sale_id = self.sale_id
    #     sale_id.enquiry_id.response_status_id = self.env.ref(
    #         "sr_uaa_main.additional_payment_link_sent_response_status").id
    #     if template:
    #         body_html = """
    #          Hello"""
    #         if sale_id.partner_id:
    #             body_html += ' ' + str(sale_id.partner_id.name) + ','
    #         body_html += """<br/>
    #          <br/>
    #
    #         We have processed your enquiry. Please verify your details and make payment to confirm the service<br/>
    #
    #          <br/><br/>"""
    #
    #         # if self.company_id:
    #         #     image_base64 = base64.b64decode(self.company_id.logo)
    #         #     image_data = io.BytesIO(image_base64)
    #         body_html += """<div style="width:100%;">"""
    #         body_html += """   <img style="margin-left:340px;max-height:100px;max-width: 230px;"
    #              src='/sr_uaa_main/static/src/images/logo.png'/>
    #              <div style="float: right;margin-top: 4%;">"""
    #
    #         if sale_id.name:
    #             body_html += """
    #                 <b style="text-align:center;">
    #                         <span> QUOTATION: </span>
    #                 </b>
    #             """
    #             body_html += """<b style="text-align:center;">#<span>"""
    #             body_html += str(sale_id.name)
    #             body_html += """</span>
    #                 </b>"""
    #         body_html += """</div></div>"""
    #
    #         if sale_id.enquiry_id:
    #             body_html += """
    #               <table class="uaa-main-table"
    #                style="width:100%;border: solid #4F4C4D 1px !important;" name="quotation_line_table">
    #             <thead>
    #                 <tr>
    #                     <th name="th_serv_details" style="text-align:center;border: solid #4F4C4D px !important;">
    #                         <span>Service Details</span>
    #                     </th>
    #                 </tr>
    #             </thead>
    #             <tbody class="sale_tbody">
    #                 <tr class="bg-200 o_line_section">
    #                     <td style="border: solid #4F4C4D 1px !important;width:100%;">
    #                         <table class="uaa-sub-table"
    #                                style="border:none !important;margin-left:10px;width:100%;"
    #                                cellspacing="0" cellpadding="0">
    #                             <tbody>
    #                                 <tr>
    #                                     <td style="border:none !important;width:50%;">
    #                                         <span style="margin-left: 10px;">Service</span>
    #                                     </td>
    #                                     <td style="border:none !important;width:50%;">
    #                                         <span>: </span>"""
    #             if sale_id.uaa_services_id:
    #                 body_html += """<span>"""
    #                 body_html += str(sale_id.uaa_services_id.name)
    #                 body_html += """</span>"""
    #             body_html += """
    #                 </td>
    #             </tr>
    #             <tr>
    #                 <td style="border:none !important;">
    #                     <span style="margin-left: 10px;">Service Details</span>
    #                 </td>
    #                 <td style="border:none !important;">
    #                     <span>: </span>"""
    #             count = 0
    #             for service_ids in sale_id.enquiry_id.services_ids:
    #                 if count != 0:
    #                     body_html += """<span>, </span>"""
    #                 body_html += """<span>"""
    #                 body_html += str(service_ids.name)
    #                 body_html += """</span>"""
    #                 count += 1
    #             body_html += """
    #                 </td>
    #             </tr>
    #             <tr>
    #                 <td style="border:none !important;">
    #                     <span style="margin-left: 10px;">Service Type</span>
    #                 </td>
    #                 <td style="border:none !important;">
    #                     <span>: </span>"""
    #
    #             if sale_id.service_type_id:
    #                 body_html += """<span>"""
    #                 body_html += str(sale_id.service_type_id.name)
    #                 body_html += """</span>"""
    #             body_html += """
    #                 </td>
    #             </tr>
    #
    #             """
    #             if sale_id.service_type_id and not sale_id.service_type_id.is_departure:
    #                 body_html += """<tr>
    #                                     <td style="border:none !important;">
    #                                         <span style="margin-left: 10px;">Arrival Flight
    #                                             Number
    #                                         </span>"""
    #                 body_html += """
    #                                                                 </td>
    #                                                                 <td style="border:none !important;">"""
    #                 body_html += """
    #                                                                         <span>:</span>"""
    #                 body_html += """
    #                                                                         <span>"""
    #                 body_html += str(sale_id.enquiry_id.arrival_flight_number)
    #                 body_html += """</span>
    #                                     </td>
    #                                 </tr>"""
    #
    #                 ##Arrival Date
    #                 body_html += """<tr>
    #                                     <td style="border:none !important;">
    #                                         <span style="margin-left: 10px;">Arrival Date And Time
    #                                         </span>"""
    #                 body_html += """
    #                                                                 </td>
    #                                                                 <td style="border:none !important;">"""
    #                 body_html += """
    #                                                                         <span>:</span>"""
    #                 body_html += """
    #                                                                         <span>"""
    #                 body_html += str(sale_id.convert_local_time_to_utc(sale_id.enquiry_id.arrival_date))
    #                 body_html += """</span>
    #                                     </td>
    #                                 </tr>"""
    #                 ###Arrival Date end
    #
    #             if sale_id.service_type_id and not sale_id.service_type_id.is_arrival:
    #                 body_html += """<tr>
    #                                     <td style="border:none !important;">
    #                                         <span style="margin-left: 10px;">Departure Flight
    #                                             Number
    #                                         </span>"""
    #                 body_html += """
    #                                                                 </td>
    #                                                                 <td style="border:none !important;">"""
    #                 body_html += """
    #                                                                         <span>:</span>
    #                                                                         <span>"""
    #                 body_html += str(sale_id.enquiry_id.departure_flight_number)
    #                 body_html += """</span>
    #                                     </td>
    #                                 </tr>"""
    #
    #                 # departure date added
    #                 body_html += """<tr>
    #                                     <td style="border:none !important;">
    #                                         <span style="margin-left: 10px;">Departure Date And Time
    #                                         </span>"""
    #                 body_html += """
    #                                                                 </td>
    #                                                                 <td style="border:none !important;">"""
    #                 body_html += """
    #                                                                         <span>:</span>
    #                                                                         <span>"""
    #                 body_html += str(sale_id.convert_local_time_to_utc(sale_id.enquiry_id.departure_date))
    #                 body_html += """</span>
    #                                     </td>
    #                                 </tr>"""
    #                 ####departure date ended
    #
    #             body_html += """
    #
    #                                 <tr>
    #                                     <td style="border:none !important;">
    #                                         <span style="margin-left: 10px;">Airport</span>
    #                                     </td>
    #                                     <td style="border:none !important;">
    #                                         <span>:</span>"""
    #             if sale_id.enquiry_id.services == 'meet_assist' or sale_id.enquiry_id.services == 'airport_hotel' or sale_id.enquiry_id.services == 'airport_lounge':
    #                 body_html += """
    #                                         <span>"""
    #                 if sale_id.enquiry_id.airport_id:
    #                     body_html += """
    #                                             <span>"""
    #                     body_html += str(sale_id.enquiry_id.airport_id.name) + '(' + str(
    #                         sale_id.enquiry_id.airport_id.code) + ') '
    #                     body_html += """
    #                                         </span>"""
    #                 body_html += """
    #                                         </span> """
    #             if sale_id.enquiry_id.services == 'airport_transfer':
    #                 body_html += """
    #                                 <span>"""
    #                 if sale_id.service_type_id and sale_id.service_type_id.is_arrival:
    #                     body_html += """
    #                                     <span>"""
    #                     body_html += str(sale_id.enquiry_id.pick_up_airport_id.name)
    #                     body_html += """</span>"""
    #                 if sale_id.service_type_id and sale_id.service_type_id.is_departure:
    #                     body_html += """
    #                                     <span>"""
    #                     body_html += str(sale_id.enquiry_id.drop_off_airport_id.name)
    #                     body_html += """</span>"""
    #                 body_html += """
    #                                 </span>"""
    #             body_html += """
    #                                                     </td>
    #                                                 </tr>
    #                                             </tbody>
    #                                         </table>
    #                                     </td>
    #                                 </tr>
    #                             </tbody>
    #                         </table>"""
    #             body_html += """
    #                             <br/>
    #                             <table class="table table-bordered" style="border: 1px solid #4F4C4D; text-align:left;">
    #                                 <thead>
    #                                     <tr style="border: 1px solid #4F4C4D; text-align:left;">
    #                                         <th style="border: 1px solid #4F4C4D;width: 26%;">
    #                                             <span>Service Category</span>
    #                                         </th>
    #                                         <th style="border: 1px solid #4F4C4D; text-align:left;width: 49%;">
    #                                             <span>Features</span>
    #                                         </th>
    #                                         <th style="border: 1px solid #4F4C4D; text-align:left;width: 25%;">
    #                                             <span>Service Charge</span>
    #                                         </th>
    #                                     </tr>
    #                                 </thead>
    #                                 <tbody>"""
    #             for line in sale_id.order_line:
    #                 body_html += """
    #                 <tr>
    #                     <td style="border: 1px solid #4F4C4D; text-align:left;">"""
    #                 # if line.product_id:
    #                 body_html += 'Additional Charge'
    #                 body_html += """
    #                     </td>
    #                     <td style="border: 1px solid #4F4C4D; text-align:left;">"""
    #                 if line.description:
    #                     body_html += line.description
    #                 body_html += """
    #
    #                     </td>
    #                     <td style="border: 1px solid #4F4C4D; text-align:left;">
    #                         <div style="text-align:left;">"""
    #                 body_html += str(sale_id.currency_id and sale_id.currency_id.name) + ' ' + str(line.service_price_total)
    #
    #                 body_html += """
    #                             <div style="margin: 32px 0px 32px 0px; text-align: right;">
    #                                 <a style="background-color: #0b8cc1; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;" href='"""
    #                 body_html += line.get_payment_link()
    #                 body_html += """'
    #                 >Pay Now</a>
    #                             </div>
    #                         </div>
    #                     </td>
    #                 </tr>"""
    #             body_html += """
    #                         </tbody>
    #                     </table>
    #          Thank you for your trust!<br/>
    #          Do not hesitate to contact us if you have any questions.
    #                          <br/>
    #                          <br/>
    #                         """
    #
    #         if sale_id.terms_conditions:
    #             body_html += """
    #                     <div class="col-12">
    #                         <br/>
    #                         <span><u>Terms and Conditions</u>:
    #                         </span>
    #                         <br/>"""
    #             # body_html += self.terms_conditions
    #             for cha in str(sale_id.cancellation_policy):
    #                 if cha == '\n':
    #                     body_html += """<br/>"""
    #                 else:
    #                     body_html += cha
    #             body_html += """
    #                     </div>
    #             """
    #         if sale_id.cancellation_policy:
    #             body_html += """
    #                     <div class="col-12">
    #                         <br/>
    #                         <span><u>Cancellation Policy</u>:
    #                         </span>
    #                         <br/>"""
    #             # body_html += self.cancellation_policy
    #             for cha in str(sale_id.cancellation_policy):
    #                 if cha == '\n':
    #                     body_html += """<br/>"""
    #                 else:
    #                     body_html += cha
    #             body_html += """
    #                     </div>
    #             """
    #         template.body_html = body_html
    #         template.subject = "Additional Payment Link | Universal Airport Assistance"
    #         template.report_template = self.env.ref("sr_uaa_main.action_report_additional_charge").id
    #
    #         ctx = {
    #             'default_model': 'sale.order',
    #             'default_res_id': self.sale_id.id,
    #             'default_use_template': bool(template),
    #             'default_template_id': template.id,
    #             'default_composition_mode': 'comment',
    #             'mark_so_as_sent': True,
    #             'custom_layout': "mail.mail_notification_paynow",
    #             # 'proforma': self.env.context.get('proforma', False),
    #             'force_email': True
    #             # 'model_description': self.with_context(lang=lang).type_name,
    #         }
    #         self.state = 'sent'
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'mail.compose.message',
    #             'views': [(False, 'form')],
    #             'view_id': False,
    #             'target': 'new',
    #             'context': ctx,
    #         }

class SalePaymentLink(models.TransientModel):
    _inherit = "payment.link.wizard"
    _description = "Generate Sales Payment Link"

    state = fields.Selection([('sent', 'Sent'),
                              ('payment_pending', 'Payment Pending'),
                              ('payment_received', 'Payment Received'),
                              ('payment_failed', 'Payment Failed'),
                              ], string='State', )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
