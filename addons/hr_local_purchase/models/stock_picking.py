# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for record in self:
            if record.purchase_id and record.purchase_id.invoice_count == 0:
                raise UserError(_("Please create vendor bill against this PO"))
            return super().button_validate()
