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


class EnquiryWarning(models.TransientModel):
    _name = 'enquiry.warning'
    _description = 'Enquiry Warning'
    _rec_name = 'message'

    message = fields.Char('Warning')
    enquiry_id = fields.Many2one('airport.enquiry','Enquiry')
    partner_id = fields.Many2one('res.partner','Customer')

    def update_partner_record(self):
        for record in self:
            if record.partner_id:
                compose_form_id = self.env.ref("sr_uaa_main.view_partner_form_inherit").id
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Customer',
                    'view_mode': 'form',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'res_model': 'res.partner',
                    'res_id': record.partner_id.id,
                    'context': {'create': False, 'edit': True, 'delete': False},
                    'target': 'new',
                }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: