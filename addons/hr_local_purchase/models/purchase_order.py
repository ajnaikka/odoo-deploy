# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(selection_add=[('reject', 'Rejected')])
    is_approved = fields.Boolean(default=False, string="Is RFQ Approved?", copy=False)
    cheque_attachment_id = fields.Many2many('ir.attachment', 'cheque_copy_attach_rel', 'po_id', 'cheque_attach_id', string="Cheque Copy",
                                            help='You can attach the copy of your cheque', copy=False)
    cheque_copy_sent = fields.Boolean(default=False, string="Is Cheque sent?", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group('hr_user_group.hr_group_hq_user'):
            raise AccessError(_("You don't have the access rights to create PO."))
        else:
            return super().create(vals_list)

    def send_rfq_for_hq_admin_approval(self):
        for record in self:
            hq_admin = self.env.ref('hr_user_group.hr_group_hq_admin').users
            partners = []
            for user in hq_admin:
                partners.append(user.partner_id.id)
            message = "Purchase Order created " + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="purchase.order">@' + record.name + '</a>. Please Verify and Confirm'
            record.message_post(body=message, partner_ids=partners)
            record.state = 'to approve'

    def rejected_by_admin(self):
        for record in self:
            partners = [record.user_id.partner_id.id]
            body = _(u'' + self.env.user.name + ' Rejected The PO ' + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="purchase.order">@' + record.name + '</a>. Please Check')
            record.message_post(body=body, partner_ids=partners)
            record.state = 'reject'

    def button_confirm(self):
        if not self.env.su and not self.env.user.has_group('hr_user_group.hr_group_hq_admin'):
            raise AccessError(_("You don't have the access rights to confirm PO."))
        else:
            res = super().button_confirm()
            for record in self:
                record.is_approved = True
                partners = [record.user_id.partner_id.id]
                body = _(u'' + self.env.user.name + ' Approved The PO ' + '<a href="#" data-oe-id=' + str(
                    record.id) + ' data-oe-model="purchase.order">@' + record.name + '</a>. Please Check')
                record.message_post(body=body, partner_ids=partners)
                template = self.env.ref('hr_local_purchase.email_template_approved_purchase_to_vendor', False)
                email_values = {
                    'email_from': self.env.user.email_formatted or self.company_id.email_formatted,
                }
                template.send_mail(record.id, force_send=True, email_values=email_values)
            return res

    def button_approve(self, force=False):
        if not self.env.su and not self.env.user.has_group('hr_user_group.hr_group_hq_admin'):
            raise AccessError(_("You don't have the access rights to approve PO."))
        else:
            res = super().button_approve(force=force)
            for record in self:
                record.is_approved = True
                partners = [record.user_id.partner_id.id]
                body = _(u'' + self.env.user.name + ' Approved The PO ' + '<a href="#" data-oe-id=' + str(
                    record.id) + ' data-oe-model="purchase.order">@' + record.name + '</a>. Please Check')
                record.message_post(body=body, partner_ids=partners)
                template = self.env.ref('hr_local_purchase.email_template_approved_purchase_to_vendor', False)
                email_values = {
                    'email_from': self.env.user.email_formatted or self.company_id.email_formatted,
                }
                template.send_mail(record.id, force_send=True, email_values=email_values)
            return res

    def action_send_cheque_copy(self):
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You are not allowed to send cheque copy."))
        for record in self:
            if not record.cheque_attachment_id:
                raise UserError(_("Please attach cheque copy"))
            template = self.env.ref('hr_local_purchase.email_template_cheque_copy_to_vendor', False)
            template.attachment_ids = [(4, attachment.id) for attachment in record.cheque_attachment_id]
            email_values = {
                'email_from': self.env.user.email_formatted or self.company_id.email_formatted,
            }
            template.send_mail(record.id, force_send=True, email_values=email_values)
            template.attachment_ids = [(5, 0, 0)]
            record.cheque_copy_sent = True
            partners = [record.user_id.partner_id.id]
            body = _(u'' + self.env.user.name + ' Sent cheque copy against PO' + '<a href="#" data-oe-id=' + str(
                record.id) + ' data-oe-model="purchase.order">@' + record.name + '</a>. to vendor')
            record.message_post(body=body, partner_ids=partners)

    def button_draft(self):
        self.write({'is_approved': False})
        return super().button_draft()