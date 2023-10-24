# -*- coding: utf-8 -*-
#############################################################################
#
#    Loyal IT Solutions Pvt Ltd
#
#    Copyright (C) 2023-TODAY Loyal IT Solutions Pvt Ltd(<https://www.loyalitsolutions.com>).
#    Author: Loyal IT Solutions Pvt Ltd
#
#    You can modify it under the terms of the
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#

#   The coding is built and distributed among Odoo community in order to help
#    Odoo providers and users, but WITHOUT ANY WARRANTY.
#
#   For the copy of GNU PUBLIC LICENSE, please see
#   <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'
    # For adding a check box in user settings
    can_add_contact = fields.Boolean('Can Create Contact')


# The below code checks the user has access or not. If not, it will restrict
class ResPartner(models.Model):
    _inherit = 'res.partner'

    fax = fields.Char(string="FAX", required=True)
    po_box = fields.Char(string="P.O.box", required=True)
    credit_limit = fields.Char(string="Credit Limit", required=True)
    mobile = fields.Char(string="Mobile", required=True)
    street = fields.Char(required=True)
    street2 = fields.Char(required=True)
    zip = fields.Char(change_default=True, required=True)
    city = fields.Char(required=True)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]", required=True)
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', required=True)
    vat = fields.Char(string='Tax ID', index=True,required=True,
                      help="The Tax Identification Number. Values here will be validated based on the country format. You can use '/' to indicate that the partner is not subject to tax.")

    # vat = fields.Char(string='Tax ID', index=True, help="The Tax Identification Number. Values here will be validated based on the country format. You can use '/' to indicate that the partner is not subject to tax.",required=True)

    @api.model
    def create(self, vals):
        if not self.env.user.can_add_contact:
            raise UserError("You are not authorized to create new Contact. Please contact the administrator")
        return super().create(vals)

    def write(self, vals):
        if vals.get('receipt_reminder_email') or vals.get(
                'reminder_date_before_receipt') or vals.get(
            'signup_token') or vals.get(
            'signup_type') or vals.get(
            'signup_expiration') or vals.get('tz'):
            return super().write(vals)
        else:
            if not self.env.user.can_add_contact:
                raise UserError("You are not authorized to update Contact.")
            return super().write(vals)
