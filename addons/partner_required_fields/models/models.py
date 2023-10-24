# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.model_create_single
    def create(self, vals):
        if not self.env.context.get('flag_create_partner'):
            if 'street' not in vals or 'street2' not in vals or 'city' not in vals or 'state_id' not in vals:
                raise UserError(_('Please provide full address.'))
            if 'country_id' not in vals or 'zip' not in vals:
                raise UserError(_('Please provide full address.'))
            if 'phone' not in vals:
                raise UserError(_('Please provide phone number.'))
            if 'vat' not in vals:
                raise UserError(_('Please provide GSTIN.'))
            if not vals['street'] or not vals['street2'] or not vals['city'] or not vals['state_id'] or \
                    not vals['country_id'] or not vals['zip']:
                raise UserError(_('Please provide full address.'))
            if not vals['phone']:
                raise UserError(_('Please provide phone number.'))
            if not vals['vat']:
                raise UserError(_('Please provide GSTIN.'))
        context = dict(self.env.context)
        if 'flag_create_partner' in context:
            del context['flag_create_partner']

        self.env.context = context
        return super(ResPartner, self).create(vals)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        context = dict(self.env.context)
        context.update({
                'flag_create_partner': 1,
            })
        self.env.context = context
        return super(ResUsers, self).create(vals_list)


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def create(self, vals_list):
        context = dict(self.env.context)
        context.update({
                'flag_create_partner': 1,
            })
        self.env.context = context
        return super(ResCompany, self).create(vals_list)
