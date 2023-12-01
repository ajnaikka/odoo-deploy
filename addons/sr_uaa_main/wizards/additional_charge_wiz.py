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
from odoo.exceptions import UserError


class AdditionalChargeWiz(models.TransientModel):
    _name = 'additional.charge.wiz'
    _description = 'Additional Charge Wiz'

    amount = fields.Float(string='Amount',)
    description = fields.Html('Description')
    
    def create_additional_charge(self):
        for rec in self:
            record = self.env['airport.enquiry'].browse(self._context.get("active_id"))
            cancelled_enq = self.env.ref("sr_uaa_main.cancelled_response_status")
            if record.response_status_id and cancelled_enq and \
                    record.response_status_id.id == cancelled_enq.id:
                raise UserError(_('Enquiry was cancelled'))

            if record.traveler_name:
                if not record.enquiry_partner_id:
                    raise UserError(_('Please add Customer'))

                partner_id = record.enquiry_partner_id
                traveler_name = record.traveler_name

                sale_id = self.env['sale.order'].create({
                    'partner_id': partner_id.id or False,
                    'traveler_name': traveler_name or False,
                    'services_ids': [(6, 0, record.services_charges_ids and record.services_charges_ids.ids or [])],
                    'date_order': fields.Datetime.today(),
                    'service_type_id': record.service_type_id and record.service_type_id.id or False,
                    'uaa_services_id': record.uaa_services_id and record.uaa_services_id.id or False,
                    # 'country_id': record.country_id and record.country_id.id or False,
                })
                #record.quotation_id = sale_id.id #Removed newly created sale linking
                record.modify_enquiry = False
                record.quotation_id.additional_charge_bool_0 = True
                sale_id.enquiry_id = record.id
                # record.status = 'open'
                service_category_id = self.env.ref('sr_uaa_main.additional_charge_category')
                line_vals = {
                    'active_check': False,
                    'service_id': False, #ser.id,
                    'description': rec.description or False,
                    'product_id': service_category_id and \
                                  service_category_id.product_id and \
                                  service_category_id.product_id.product_variant_id and \
                                  service_category_id.product_id.product_variant_id.id or False,
                    'price_unit': rec.amount
                }
                sale_id.order_line = [(0, 0, line_vals)]
                # sale_id.action_confirm()
                record.message_post(body="Additional charge quotation created successfully")
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
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: