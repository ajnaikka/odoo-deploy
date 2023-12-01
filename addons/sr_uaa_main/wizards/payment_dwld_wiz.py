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

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError


class PaymentDownloadWizard(models.TransientModel):
    _name = 'payment.download.wizard'
    _description = 'Payment Download Wizard'

    message = fields.Char(string='Message', default='Please click a button to continue!!!')

    def action_download_payment_receipt(self):
        quotation_id = self.env['sale.order'].browse(self._context.get("active_id"))
        if quotation_id.invoice_ids:
            if quotation_id.invoice_ids.payment_id:
                payment_id = quotation_id.invoice_ids.payment_id
                return self.env.ref('sr_uaa_main.action_report_payment_receipt_uaa'). \
                    report_action(payment_id.id)
            else:
                payment_transaction_id = self.env['payment.transaction'].search(
                    [('invoice_ids', 'in', quotation_id.invoice_ids.ids), ('state', '=', 'done')], limit=1)

                if not payment_transaction_id:
                    payment_account_id = self.env['account.payment'].search(
                        [('reconciled_invoice_ids', 'in', quotation_id.invoice_ids.ids), ('state', '=', 'posted'),
                         ('ref', '=',  quotation_id.invoice_ids.name)], limit=1)

                    if payment_account_id:
                        return self.env.ref('sr_uaa_main.action_report_payment_receipt_uaa'). \
                            report_action(payment_account_id.id)

                if payment_transaction_id:
                    return self.env.ref('sr_uaa_main.action_report_payment_transaction_uaa'). \
                        report_action(payment_transaction_id.id)
        else:
            raise UserError(_('Invoice is not generated for this Enquiry!!!'))

    def action_send_payment_receipt(self):
        for record in self:
            record = record.sudo()
            self.ensure_one()
            quotation_id = self.env['sale.order'].browse(self._context.get("active_id"))
            report_template_id = ' '
            if quotation_id.invoice_ids:
                email_to = quotation_id.partner_invoice_id and quotation_id.partner_invoice_id.email or ''
                if quotation_id.invoice_ids.payment_id:
                    payment_id = quotation_id.invoice_ids.payment_id
                    report_template_id = self.env.ref('sr_uaa_main.action_report_payment_receipt_uaa')._render_qweb_pdf(payment_id.id)
                else:
                    payment_transaction_id = self.env['payment.transaction'].sudo().search(
                        [('invoice_ids', 'in', quotation_id.invoice_ids.ids), ('state', '=', 'done')], limit=1)

                    if not payment_transaction_id:
                        payment_account_id = self.env['account.payment'].sudo().search(
                            [('reconciled_invoice_ids', 'in', quotation_id.invoice_ids.ids), ('state', '=', 'posted'),
                             ('ref', '=',  quotation_id.invoice_ids.name)], limit=1)

                        if payment_account_id:
                            report_template_id = self.env.ref('sr_uaa_main.action_report_payment_receipt_uaa')._render_qweb_pdf(payment_account_id.id)

                    if payment_transaction_id:
                        report_template_id = self.env.ref('sr_uaa_main.action_report_payment_transaction_uaa')._render_qweb_pdf(payment_transaction_id.id)

                if report_template_id:
                    template = self.env.ref('sr_uaa_main.email_template_payment_receipt')
                    if template:
                        if record:
                            body_html = '''<p>Dear ''' + str(quotation_id.traveler_name) + ''',</p>
                                                             <br/><p>Please refer the attached payment receipt.</p>
                                                                                            '''
                            body_html += self.env.ref("sr_uaa_main.uaa_payment_receipt_mail").body or ''
                            body_html += '''
                                           <br/>
                                           <p>Thanks & Regards,</p>
                                           <p>''' + str(self.env.user.partner_id.name) + '''</p>
                                           '''
                            template.body_html = body_html
                            # template.email_to = email_to
                            template.partner_to = quotation_id.partner_id.id
                            template.subject = "Payment Receipt | Universal Airport Assistance"
                            # report_template_id = self.env.ref('sr_uaa_main.action_report_payment_receipt_uaa')._render_qweb_pdf(payment_id.id)
                            data_record = base64.b64encode(report_template_id[0])
                            ir_values = {
                                'name': "Payment Receipt",
                                'type': 'binary',
                                'datas': data_record,
                                'store_fname': "Payment Receipt.pdf",
                                'mimetype': 'application/pdf',
                            }
                            attachment_ids = []
                            data_id = self.env['ir.attachment'].create(ir_values)
                            attachment_ids = [(6, 0, [data_id.id])]


                            ctx = {
                                'default_model': 'sale.order',
                                'default_res_id': quotation_id.id,
                                'default_use_template': bool(template),
                                'default_template_id': template.id,
                                'default_composition_mode': 'comment',
                                'mark_so_as_sent': True,
                                'custom_layout': "mail.mail_notification_paynow",
                                'force_email': True,
                                'default_attachment_ids': attachment_ids
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
