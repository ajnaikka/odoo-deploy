# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    branch_stock_transfer_request_id = fields.Many2one(
        'branch.stock.transfer.request',
        string="Branch Stock Transfer Request",
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    def button_validate(self):
        for record in self:
            if record.branch_stock_transfer_request_id and record.branch_stock_transfer_request_id.state != 'processed':
                raise UserError(_("Make sure the branch transfer request has been processed"))
            return super().button_validate()

    def action_confirm(self):
        for record in self:
            if record.branch_stock_transfer_request_id:
                if record.branch_stock_transfer_request_id.state != 'approved':
                    raise UserError(_("Make sure the branch transfer request has been approved"))
                if self.env.user.branch_id != record.location_id.transfer_request_branch_id:
                    raise AccessError(_("You don't have the permission. This request belongs to another branch"))
            return super().action_confirm()

    def action_cancel(self):
        for record in self:
            if record.branch_stock_transfer_request_id and record.branch_stock_transfer_request_id.state != 'cancel':
                raise UserError(_("Make sure the branch transfer request has been cancelled"))
        return super().action_cancel()

    def unlink(self):
        for record in self:
            if record.branch_stock_transfer_request_id:
                raise UserError(_("Make sure the branch transfer request has been deleted"))
        return super().unlink()