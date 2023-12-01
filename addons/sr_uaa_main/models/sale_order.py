# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import pytz


DEFAULT_SERVER_DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'id desc'

    def _compute_payment_transactions(self):
        for rec in self:
            payment_transactions = self.env['payment.transaction'].search(
                [('sale_order_ids', 'in', rec.id)])
            rec.pay_trans_no = len(payment_transactions)

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        company = self.company_id or self.env.company
        if company.terms_conditions:
            res['terms_conditions'] = company.terms_conditions
        if company.cancellation_policy:
            res['cancellation_policy'] = company.cancellation_policy
        return res

    enquiry_id = fields.Many2one('airport.enquiry', string="Enquiry", copy=False)
    terms_conditions = fields.Text('Terms & Conditions')
    cancellation_policy = fields.Text('Cancellation Policy')
    services_ids = fields.Many2many('enquiry.service.line', 'sale_serviceline_rel', 'sale_id', 'service_id',
                                    string="Service Charges")
    service_type_id = fields.Many2one('airport.service.type', 'Service Type', related='enquiry_id.service_type_id',
                                      store=True, readonly=True)
    uaa_services_id = fields.Many2one('uaa.services', 'Service', related='enquiry_id.uaa_services_id', store=True,
                                      readonly=True)
    # validity_date = fields.Date(string='Expiration', readonly=True, copy=False,
    #                             states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #                             default=_default_validity_date)
    validity_date_hour = fields.Datetime('Expiry Date',
                                         tracking=True, default=lambda rec: rec._default_validity_hour())

    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired")
    additional_charges_ids = fields.One2many('additional.charge.sale', 'sale_id', 'Additional Charges', readonly=True)

    # may03
    config_sale_order_validity_hours = fields.Integer(default=lambda rec: rec._default_config_validity_hour())
    send_by_mail_date = fields.Datetime('Send by mail Date')
    state = fields.Selection(selection_add=[('expiry', 'Expired')], track_visibility='onchange')
    pay_trans_no = fields.Integer(compute='_compute_payment_transactions', string='Payment Transactions')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all')
    create_quotation_bool_0 = fields.Boolean('Quotation Bool', default=False)
    additional_charge_bool_0 = fields.Boolean('Additional Charge Bool', default=False)
    traveler_name = fields.Char('Name of the Traveller', required=True)

    @api.depends('state', 'validity_date_hour', 'date_order')
    def _compute_is_expired(self):
        # res = super(SaleOrder, self)._compute_is_expired()
        today = fields.Datetime.now()
        for order in self:
            order.is_expired = order.state == 'sent' and order.validity_date_hour and order.validity_date_hour < today
        # return res

    @api.model
    def _default_validity_hour(self):
        validity_hour_str = False
        company = self.env.company
        if company.default_sale_order_validity_hours:
            today = fields.Datetime.now(self)
            validity_hour = today + relativedelta(
                hours=company.default_sale_order_validity_hours
            )
            validity_hour_str = fields.Datetime.to_string(validity_hour)
        return validity_hour_str

    # may03
    @api.model
    def _default_config_validity_hour(self):
        company = self.env.company
        if company.default_sale_order_validity_hours:
            return company.default_sale_order_validity_hours
        else:
            return None

    @api.onchange("config_sale_order_validity_hours")
    def _onchange_date_order(self):
        if self.date_order:
            # company = self.company_id or self.env.company
            # if company.default_sale_order_validity_hours:
            today = fields.Datetime.now()
            date_order = fields.Datetime.to_datetime(today)
            validity_hour = date_order + relativedelta(
                hours=self.config_sale_order_validity_hours or 0
            )

            self.validity_date_hour = fields.Datetime.to_string(validity_hour)
            
    def _send_order_confirmation_mail(self):
        '''Aviod sending sale order email from odoo bot'''
        return True
    

    @api.model
    def create(self, vals_list):
        res = super(SaleOrder, self).create(vals_list)
        res._onchange_date_order()
        if res.partner_id:
            enquiry = res.enquiry_id
            # enquiry = self.env['airport.enquiry'].sudo().search([('traveler_name', '=', res.partner_id.name),
            #                                                      ('email', '=', res.partner_id.email)], limit=1)
            if enquiry:
                #enquiry.enquiry_partner_id = res.partner_id.id
                if enquiry.traveler_name:
                    res['traveler_name'] = enquiry.traveler_name

            if res.partner_id.passport_expiry_date:
                res.partner_id._compute_is_expired()
                if res.partner_id.is_passport_expired:
                    settings_notification_mail = self.env['ir.config_parameter'].sudo().get_param(
                        'notification_mail') or False

                    if settings_notification_mail:
                        template = self.env.ref('sr_uaa_main.email_template_passport_expiry_notification')
                        description = self.env.ref("sr_uaa_main.uaa_passport_expiry_notification_body").body or ''

                        description += '''<p>Passport Number ''' + str(
                            res.partner_id.passport_number) + ''' has been Expired for Customer ''' + str(
                            res.partner_id.name) + '''.</p>
                                                                                               <br/>
                                                                                               <br/>
                                                                                               <p>Thanks & Regards,</p>
                                                                                               <p>''' + str(
                            self.env.user.partner_id.name) + '''</p>
                                                                                               '''
                        template.write({
                            'body_html': description,
                            'email_to': settings_notification_mail or '',
                            'email_from': self.env.company and self.env.company.partner_id and self.env.company.partner_id.email or '',
                        })
                        mail_id = template.sudo().send_mail(res.partner_id.id, force_send=True)
                    else:
                        raise UserError(_("Customer Passport has been expired!!"))
        return res

    def write(self, vals):
        for record in self:
            if record.state=='cancel':
                raise UserError(_("Cancelled records cannot be modified!!"))
        res = super(SaleOrder, self).write(vals)
        if vals.get('date_order'):
            self._onchange_date_order()
        if vals.get('state') == 'sent':
            if self.enquiry_id:
                self.enquiry_id.status = 'open'
        # if self.partner_id:
        #     if self.partner_id.passport_expiry_date:
        #         self.partner_id._compute_is_expired()
        #         if self.partner_id.is_passport_expired:
        #             settings_notification_mail = self.env['ir.config_parameter'].sudo().get_param(
        #                 'notification_mail') or False
        #             if settings_notification_mail:
        #                 template = self.env.ref('sr_uaa_main.email_template_passport_expiry_notification')
        #                 description = self.env.ref("sr_uaa_main.uaa_passport_expiry_notification_body").body or ''
        #
        #                 description += '''<p>Passport Number ''' + str(
        #                     self.partner_id.passport_number) + ''' has been Expired for Customer ''' + str(
        #                     self.partner_id.name) + '''.</p>
        #                                                                                        <br/>
        #                                                                                        <br/>
        #                                                                                        <p>Thanks & Regards,</p>
        #                                                                                        <p>''' + str(
        #                     self.env.user.partner_id.name) + '''</p>
        #                                                                                        '''
        #                 template.write({
        #                     'body_html': description,
        #                     'email_to': settings_notification_mail or '',
        #                     'email_from': self.env.company and self.env.company.partner_id and self.env.company.partner_id.email or '',
        #                 })
        #                 mail_id = template.sudo().send_mail(self.partner_id.id, force_send=True)
        #             else:
        #                 raise UserError(_("Customer Passport has been expired!!"))

        return res

    def uaa_quotation_confirm(self):
        for rec in self:
            check_count = 0
            if rec.enquiry_id:
                rec.enquiry_id.status = 'open'
            for line in rec.order_line:

                if line.active_check:
                    check_count += 1
                else:
                    line.unlink()

            if check_count == 0:
                raise UserError(_("Select one Service Category"))
            elif check_count > 1:
                raise UserError(_("Select only one Service Category"))
            else:
                rec.action_confirm()
                wiz = self.env['sale.advance.payment.inv'].sudo().with_context(active_ids=rec.ids).create({

                })
                wiz.create_invoices()
                invoices = self.mapped('invoice_ids')
                if len(invoices) == 1:
                    invoices.action_post()
                    if invoices.payment_state != 'paid' and invoices.move_type in \
                            ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'):
                        wiz_invoice = self.env['account.payment.register'].sudo().with_context(
                            active_model='account.move',
                            active_ids=invoices.ids).create({

                        })
                        wiz_invoice.action_create_payments()

    def action_sale_payment_transactions(self):
        for rec in self:
            payment_transactions = self.env['payment.transaction'].search(
                [('sale_order_ids', 'in', rec.id)])
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

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        self.ensure_one()
        description = ''
        for line in self.order_line:
            if line.active_check:
                description = line.description
        invoice_vals.update({
            'enquiry_id': self.enquiry_id and self.enquiry_id.id or False,
            'services_ids': [(6, 0, self.services_ids and self.services_ids.ids or [])],
            'description': description
        })
        return invoice_vals

    def get_enquiry(self):
        self.ensure_one()
        if self.enquiry_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Enquiry',
                'view_mode': 'form',
                'res_model': 'airport.enquiry',
                'res_id': self.enquiry_id.id,
                # 'domain': [('enquiry_id', '=', self.id)],
                'context': "{'create': False,'edit': False,'delete': False}",
                # 'target': 'new',
            }

    def action_additional_charge(self):
        for rec in self:
            action = self.env.ref('sr_uaa_main.action_additional_charge')
            result = action.read()[0]
            result['context'] = {
                'default_amount': 0,
                'default_company_id': self.env.company and self.env.company.id,
                'default_sale_id': rec.id,
                'default_enquiry_id': rec.enquiry_id and rec.enquiry_id.id or False,
                # 'default_partner_id': rec.partner_id and rec.partner_id.id or False,
            }
            return result

    def action_quotation_send(self):
        self.ensure_one()
        res = super(SaleOrder, self).action_quotation_send()
        # may03
        from datetime import datetime
        now = datetime.now()
        send_by_mai_date = now.strftime("%Y-%m-%d %H:%M:%S")
        if self.state == 'draft':
            self.send_by_mail_date = send_by_mai_date
            send_by_mai_date = fields.Datetime.to_datetime(send_by_mai_date)
            if self.config_sale_order_validity_hours > 0:
                expiry_date = send_by_mai_date + relativedelta(
                    hours=self.config_sale_order_validity_hours)
                #self.validity_date_hour = expiry_date
        # may03 end

        if res.get('context', False):
            ctx = res.get('context')
            if ctx.get('default_template_id'):
                template = self.env['mail.template'].browse(ctx.get('default_template_id'))
                if template:
                    body_html = """
                     Hello"""
                    if self.traveler_name:
                        body_html += ' ' + str(self.traveler_name) + ','
                    body_html += """<br/>
                     <br/>


                     We have processed your enquiry. <br/>
                     Please verify your details and make payment to confirm the service. <br/>
                    <br/><br/>"""

                    body_html += """<div style=" width:100%; margin:0;" >"""
                    body_html += """<div style="width:100%;text-align:center;">"""
                    body_html += """   <img style="max-height:100px;max-width: 230px;"
                                                         src='/sr_uaa_main/static/src/images/logo.png'/>
                                    <div style="text-align: right; margin-bottom:10px;margin-top: 10px;">
                    """

                    if self.name:
                        body_html += """
                            <b style="text-align:center;">
                                    <span> QUOTATION: </span>
                            </b>
                        """
                        body_html += """<b style="text-align:center;">#<span>"""
                        body_html += str(self.name)
                        body_html += """</span>
                            </b>"""
                    body_html += """</div></div>"""

                    if self.enquiry_id:
                        body_html += """
                          <table class="uaa-main-table"
                           style="width:100%;border: solid #4F4C4D 1px !important;padding:10px;margin: 10px 10px 10px 0;" name="quotation_line_table">
                        <thead>
                            <tr>
                                <th name="th_serv_details" style="text-align:center;border: solid #4F4C4D px !important;">
                                    <span>Service Details</span>
                                </th>
                            </tr>
                        </thead>
                        <tbody class="sale_tbody">
                            <tr class="bg-200 o_line_section">
                                <td style="border: solid #4F4C4D 1px !important;width:100%;">
                                    <table class="uaa-sub-table"
                                           style="border:none !important;width:100%;"
                                           cellspacing="0" cellpadding="0">
                                        <tbody>
                                            <tr>
                                                <td style="border:none !important;width:50%;padding-left: 10px;">
                                                    Service
                                                </td>
                                                <td style="width:2%!important; vertical-align: top;"> <span>: </span></td>
                                                <td style="border:none !important;width:49%;">
                                                    """
                        if self.uaa_services_id:
                            body_html += """<span>"""
                            body_html += str(self.uaa_services_id.name)
                            body_html += """</span>"""
                        body_html += """
                            </td>
                        </tr>
                        <tr>
                            <td style="border:none !important;padding-left: 10px;">
                                Service Details
                            </td>
                            <td style=" vertical-align: top;"> <span>: </span></td>
                            <td style="border:none !important;">
                                """
                        count = 0
                        for service_ids in self.enquiry_id.services_ids:
                            if count != 0:
                                body_html += """<span>,</span>"""
                            body_html += """<span style="word-wrap:break-word;">"""
                            body_html += str(service_ids.name)
                            body_html += """</span>"""
                            count += 1

                        body_html += """
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="border:none !important;padding-left: 10px;">
                                                        No of Passengers
                                                    </td>
                                                    <td style=" vertical-align: top; "> <span>: </span></td>
                                                    <td style="border:none !important;">
                                                       """

                        pax_count = ''
                        if self.enquiry_id.adults_count > 0:
                            if self.enquiry_id.adults_count == 1:
                                pax_count += str(self.enquiry_id.adults_count) + ' Adult'
                            if self.enquiry_id.adults_count > 1:
                                pax_count += str(self.enquiry_id.adults_count) + ' Adults'

                        if self.enquiry_id.children_count > 0:
                            if self.enquiry_id.infants_count > 0:
                                if self.enquiry_id.children_count == 1:
                                    pax_count += ' , ' + str(self.enquiry_id.children_count) + ' Child'
                                if self.enquiry_id.children_count > 1:
                                    pax_count += ' , ' + str(self.enquiry_id.children_count) + ' Children'

                            if self.enquiry_id.infants_count == 0:
                                if self.enquiry_id.children_count == 1:
                                    pax_count += ' and ' + str(self.enquiry_id.children_count) + ' Child'
                                if self.enquiry_id.children_count > 1:
                                    pax_count += ' and ' + str(self.enquiry_id.children_count) + ' Children'

                        if self.enquiry_id.infants_count > 0:
                            if self.enquiry_id.infants_count == 1:
                                pax_count += ' and ' + str(self.enquiry_id.infants_count) + ' Infant'
                            if self.enquiry_id.infants_count > 1:
                                pax_count += ' and ' + str(self.enquiry_id.infants_count) + ' Infants'

                        body_html += pax_count
                        body_html += """
                            </td>
                        </tr> 
                        <tr>
                            <td style="border:none !important;padding-left: 10px;">
                                Service Type
                            </td>
                            <td style=" vertical-align: top; "> <span>: </span></td>
                            <td style="border:none !important;">
                               """

                        if self.service_type_id:
                            body_html += """<span>"""
                            body_html += str(self.service_type_id.name)
                            body_html += """</span>"""
                        body_html += """
                            </td>
                        </tr>

                        """
                        if self.service_type_id and not self.service_type_id.is_departure:
                            body_html += """<tr>
                                                <td style="border:none !important;padding-left: 10px;">
                                                    Arrival Flight
                                                        Number
                                                    """
                            body_html += """
                                                                            </td>
                                                                            <td style=" vertical-align: top;"> <span>: </span></td>
                                                                            <td style="border:none !important;">"""
                            body_html += """
                                                                                    """
                            body_html += """
                                                                                    <span>"""
                            body_html += str(self.enquiry_id.arrival_flight_number)
                            body_html += """</span>
                                                </td>
                                            </tr>"""

                            ##Arrival Date
                            body_html += """<tr>
                                                <td style="border:none !important;padding-left: 10px;">
                                                    Arrival Date And Time
                                                    """
                            body_html += """
                                                                            </td>
                                                                            <td style=" vertical-align: top; "> <span>: </span></td>
                                                                            <td style="border:none !important;">"""
                            body_html += """
                                                                                    """
                            body_html += """
                                                                                    <span>"""
                            body_html += self.enquiry_id.arrival_date_str
                            body_html += """</span>
                                                </td>
                                            </tr>"""
                            ###Arrival Date end

                        if self.service_type_id and not self.service_type_id.is_arrival:
                            body_html += """<tr>
                                                <td style="border:none !important;padding-left: 10px;">
                                                    Departure Flight
                                                        Number
                                                    """
                            body_html += """
                                                                            </td>
                                                                            <td style=" vertical-align: top; "> <span>: </span></td>
                                                                            <td style="border:none !important;">"""
                            body_html += """

                                                                                    <span>"""
                            body_html += str(self.enquiry_id.departure_flight_number)
                            body_html += """</span>
                                                </td>
                                            </tr>"""

                            # departure date added
                            body_html += """<tr>
                                                <td style="border:none !important;padding-left: 10px;">
                                                   Departure Date And Time
                                                   """
                            body_html += """
                                                                            </td>
                                                                            <td style=" vertical-align: top; "> <span>: </span></td>
                                                                            <td style="border:none !important;">"""
                            body_html += """

                                                                                    <span>"""
                            body_html += self.enquiry_id.departure_date_str
                            body_html += """</span>
                                                </td>
                                            </tr>"""
                            ####departure date ended

                        body_html += """

                                            <tr>
                                                <td style="border:none !important;padding-left: 10px;">
                                                    Airport
                                                </td>
                                                <td style=" vertical-align: top;"> <span>: </span></td>
                                                <td style="border:none !important;">
                                                    """
                        if self.enquiry_id.services == 'meet_assist' or \
                                self.enquiry_id.services == 'airport_hotel' or \
                                self.enquiry_id.services == 'airport_lounge':
                            body_html += """
                                                    <span>"""
                            if self.enquiry_id.airport_id:
                                body_html += """
                                                        <span>"""
                                body_html += str(self.enquiry_id.airport_id.name) + '(' + str(
                                    self.enquiry_id.airport_id.code) + ') '
                                body_html += """
                                                    </span>"""
                            body_html += """
                                                    </span> """
                        if self.enquiry_id.services == 'airport_transfer':
                            body_html += """
                                            <span>"""
                            if self.service_type_id and self.service_type_id.is_arrival:
                                body_html += """
                                                <span>"""
                                body_html += str(self.enquiry_id.pick_up_airport_id.name)
                                body_html += """</span>"""
                            if self.service_type_id and self.service_type_id.is_departure:
                                body_html += """
                                                <span>"""
                                body_html += str(self.enquiry_id.drop_off_airport_id.name)
                                body_html += """</span>"""
                            body_html += """
                                            </span>"""
                        body_html += """
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>"""
                        body_html += """
                                        <br/>
                                        <table class="table table-bordered" style="border: 1px solid #4F4C4D; text-align:left;">
                                            <thead>
                                                <tr style="border: 1px solid #4F4C4D; text-align:left;">
                                                    <th style="border: 1px solid #4F4C4D;width: 26%;">
                                                        <span>Service Category</span>
                                                    </th>
                                                    <th style="border: 1px solid #4F4C4D; text-align:left;width: 47%;">
                                                        <span>Features</span>
                                                    </th>
                                                    <th style="border: 1px solid #4F4C4D; text-align:left;width: 27%;">
                                                        <span>Service Charge</span>
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody>"""
                        for line in self.order_line:
                            body_html += """
                            <tr>
                                <td style="border: 1px solid #4F4C4D; text-align:left;">"""
                            if line.product_id:
                                body_html += str(line.product_id.name)
                            body_html += """
                                </td>
                                <td style="border: 1px solid #4F4C4D; text-align:left; ul{margin:0; padding: 0 0 0 15px;}">"""
                            if line.description:
                                body_html += line.description
                            body_html += """

                                </td>
                                <td style="border: 1px solid #4F4C4D; text-align:left;">
                                    <div style="text-align:left;">"""
                            body_html += str(self.currency_id and self.currency_id.name) + ' ' + str(
                                line.service_price_total)

                            body_html += """
                                        <div style="margin: 32px 0px 32px 0px; text-align: right;">
                                            <a style="background-color: #0b8cc1; text-decoration: none; color: #fff; font-size:0.8rem; display: inline-block; border-radius: 30px; padding:6px 10px; text-align: center; white-space:nowrap;" href='"""
                            body_html += line.get_payment_link()
                            body_html += """'
                            >Pay Now</a>
                                        </div>
                                    </div>
                                </td>
                            </tr>"""
                        body_html += """
                                    </tbody>
                                </table>
                     Thank you for your trust!<br/>
                     Do not hesitate to contact us if you have any questions.
                                     <br/>
                                     <br/>
                                    """

                    if self.validity_date_hour:
                        validity_date_hour = self.enquiry_expire_date_time(self.enquiry_id, self.validity_date_hour)
                        # self.validity_date_hour.strftime('%d-%m-%Y %H:%M:%S')
                        validation_str = """
                                      <div class="col-12" style="padding:0!important; margin:0!important;">
                                          <span><b>*Payment link will expire on """ + validity_date_hour + """</b></span>"""
                        body_html += validation_str
                    if self.terms_conditions:
                        body_html += """
                                <div class="col-12" style="padding:0!important; margin:0!important;width:100%!important;">
                                <br/>
                                    <span><u>Terms and Conditions</u>:
                                    </span>
                                    <br/>"""
                        # body_html += self.terms_conditions
                        for cha in str(self.terms_conditions):
                            if cha == '\n':
                                body_html += """<br/>"""
                            else:
                                body_html += cha
                        body_html += """
                                </div>
                        """
                    if self.cancellation_policy:
                        body_html += """
                                <div class="col-12" style="padding:0!important; margin:0!important;width:100%!important;">
                                    <br/>
                                    <span><u>Cancellation Policy</u>:
                                    </span>
                                    <br/>"""
                        for cha in str(self.cancellation_policy):
                            if cha == '\n':
                                body_html += """<br/>"""
                            else:
                                body_html += cha
                        body_html += """
                                </div>
                        """
                        body_html += """</div>"""
                    template.body_html = body_html
                    template.report_template = False  # self.env.ref("sale.action_report_saleorder").id
                    template.subject = "Quotation and Payment Link | Universal Airport Assistance"

        return res

    def get_payments_view(self):
        for rec in self:
            payment = False
            payment_transactions = False
            invoice_ids = rec.mapped('invoice_ids')
            for invoice in invoice_ids:
                payment = self.env['account.payment'].search([('ref', '=', invoice.name)])
                payment_transactions = self.env['payment.transaction'].search([('sale_order_ids', 'in', rec.id), ('state','=','done')])
                if not payment:
                    payment = self.env['account.payment'].search([('ref', '=', payment_transactions.reference)])
                    if not payment and payment_transactions:
                        payment = self.env['account.payment'].search([('payment_transaction_id', '=', payment_transactions.id)])
                if payment:
                    payment.traveler_name = rec.traveler_name

            # payment = rec.invoice_ids and rec.invoice_ids.payment_id or False
            if payment:
                action = self.env.ref('account.action_account_payments').read()[0]
                form_view_id = self.env.ref('account.view_account_payment_form').id
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = payment.id or False
                action['target'] = 'new'
                return action
            else:
                raise UserError(_("No payments found!!"))

    # may03
    # @api.onchange('config_sale_order_validity_hours')
    # def onchange_config_sale_order_validity_hours(self):
    #     if self.config_sale_order_validity_hours:
    #         if self.state not in ['draft', 'cancel'] and self.send_by_mail_date:
    #             send_by_mai_date = fields.Datetime.to_datetime(self.send_by_mail_date)
    #             if self.config_sale_order_validity_hours > 0:
    #                 expiry_date = send_by_mai_date + relativedelta(
    #                     hours=self.config_sale_order_validity_hours)
    #                 self.validity_date_hour = expiry_date

    # may03
    # check order expiry by validity_date_hour reference(scheduler action)
    def check_order_expiry(self):
        from datetime import datetime
        now = datetime.now()
        now_date = now.strftime("%Y-%m-%d %H:%M:%S")
        orders = self.env['sale.order'].sudo().search([('validity_date_hour', '<=', now_date),
                                                       ('state', 'not in', ['expiry', 'cancel'])])
        for rec in orders:
            if rec.state not in ['expiry', 'cancel']:
                rec.state = "expiry"

    def change_state_to_sale_order(self):
        for rec in self:
            rec.state = 'sent'
            if rec.enquiry_id.status == 'close':
                rec.enquiry_id.status = 'open'

    def convert_local_time_to_utc(self, enquiry, date=False):
        display_date_result = False
        if date:
            timezone = pytz.timezone((enquiry and enquiry.created_timezone) or self._context.get('tz') or 'Asia/Calcutta')
            event_date = pytz.UTC.localize(fields.Datetime.from_string(date))  # Add "+hh:mm" timezone
            display_date_result = event_date.astimezone(timezone)
            display_date_result = display_date_result.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return display_date_result

    def enquiry_expire_date_time(self, enquiry, date=False):
        display_date_result = False
        if date:
            # timezone = pytz.timezone((enquiry and enquiry.created_timezone) or self._context.get('tz') or 'Asia/Calcutta')
            timezone = pytz.timezone('Asia/Calcutta')
            event_date = pytz.UTC.localize(fields.Datetime.from_string(date))  # Add "+hh:mm" timezone
            display_date_result = event_date.astimezone(timezone)
            display_date_result = display_date_result.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return display_date_result
    
    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for record in self:
            enquiry_id = record.enquiry_id or False
            can_id = self.env.ref("sr_uaa_main.cancelled_response_status").id
            if enquiry_id and can_id and enquiry_id.response_status_id and\
               enquiry_id.response_status_id.id==can_id:
                enq_val = {}
                if enquiry_id.can_response_status_id:
                    enq_val.update({'response_status_id': enquiry_id.can_response_status_id.id,})
                if enquiry_id.can_response_status:
                    enq_val.update({'response_status': enquiry_id.can_response_status,
                                    'resp_status_change': False,})
                if enquiry_id.can_status:
                    if enquiry_id.can_status=='closed':
                        enq_val.update({'status': 'open'})
                    else:
                        enq_val.update({'status': 'new'})
                enquiry_id.write(enq_val) 
        return res
    
    def unlink(self):
        for order in self:
            if order.invoice_count:
                raise UserError(_('You cannot delete an order which has been invoiced once.'))
        return super(SaleOrder, self).unlink()
    


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'service_price_total')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': 0,
                'price_total': line.service_price_total,
                'price_subtotal': line.service_price_total,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('late_booking_fee', 'discount', 'price_unit')
    def _compute_total_service_charge(self):
        for rec in self:
            total = (rec.price_unit or 0) + (rec.late_booking_fee or 0)
            if rec.discount:
                total -= (total * rec.discount / 100)
            rec.service_price_total = total
            rec.price_subtotal = total
            rec.price_total = total

    active_check = fields.Boolean(string="Check", default=False)
    service_charge = fields.Float('Service Charge', default=0.00)
    description = fields.Html('Description')
    service_id = fields.Many2one('enquiry.service.line', string="Service")
    late_booking_fee = fields.Float('Additional Charge', default=0.00)
    discount = fields.Float('Discount(%)', default=0.00)
    service_price_total = fields.Monetary(compute='_compute_total_service_charge', string='Total Service Charge',
                                          readonly=True, store=True)

    def get_payment_link(self):
        for rec in self:
            vals = {
                'res_model': 'sale.order',
                'description': rec.id,
                'res_id': rec.order_id and rec.order_id.id or False,
                'currency_id': rec.order_id and rec.order_id.currency_id and rec.order_id.currency_id.id or False,
                'partner_id': rec.order_id and rec.order_id.partner_id and rec.order_id.partner_id.id or False,
                'amount_max': rec.service_price_total,
                'amount': rec.service_price_total,
            }
            payment_link_id = self.env['payment.link.wizard'].sudo().create(vals)
            return payment_link_id.link