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
from odoo import api, fields, models, _, tools
from datetime import date


class CancelEnquiryWizard(models.TransientModel):
    _name = 'cancel.enquiry.wizard'
    _description = ' Cancel Enquiry Wizard'

    cancel_reason = fields.Text(string='Cancel Reason')

    def action_cancel_enquiry(self):
        enquiry_id = self.env['airport.enquiry'].browse(self._context.get("active_id"))
        if enquiry_id:
            enq_vals = {}
            if not enquiry_id.quotation_id:
                enq_vals.update({'cancel_new': True})
            old_resp_id = enquiry_id.response_status_id and \
                          enquiry_id.response_status_id.id or False
            old_resp = enquiry_id.response_status
            can_status = enquiry_id.status
            enquiry_id.change_status_to_cancel()
            enq_vals.update({'cancel_reason': self.cancel_reason or ' ',
                              'cancel_date':  date.today() or False,
                              'response_status_id': self.env.ref("sr_uaa_main.cancelled_response_status").id,
                              'response_status': 'cancelled',
                              'status': 'close',
                              'can_response_status_id': old_resp_id,
                              'can_response_status': old_resp,
                              'can_status': can_status,
                              })
            enquiry_id.write(enq_vals)
            if enquiry_id.quotation_id:
                enquiry_id.quotation_id.action_cancel()
            if enquiry_id.invoice_id:
                enquiry_id.invoice_id.button_cancel()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: