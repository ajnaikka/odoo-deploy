# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError, Warning
from num2words import num2words

class Bank(models.Model):
    _inherit = 'res.bank'

    iban = fields.Char('IBAN')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch = fields.Char('Branch Name')
    is_check = fields.Boolean('Active',default=False)