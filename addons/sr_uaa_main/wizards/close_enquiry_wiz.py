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


class CloseEnquiryWizard(models.TransientModel):
    _name = 'close.enquiry.wizard'
    _description = ' Close Enquiry Wizard'

    @api.model
    def default_get(self, fields):
        res = super(CloseEnquiryWizard, self).default_get(fields)
        enquiry_id = self.env['airport.enquiry'].browse(self._context.get("active_id"))
        if enquiry_id.response_status_id:
            res['response_status_id'] = enquiry_id.response_status_id
        return res

    response_status_id = fields.Many2one('response.status.name', 'Response Status')

    def action_close_enquiry(self):
        enquiry_id = self.env['airport.enquiry'].browse(self._context.get("active_id"))
        if enquiry_id:
            enquiry_id.change_status_to_close()
            enquiry_id.write({'response_status_id': self.response_status_id.id,
                              'response_status': enquiry_id.get_response_status(),
                              'status': 'close',
                              })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
