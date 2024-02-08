# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    contract_signed_stage = fields.Boolean('Contract Signed Stage', default=False)
    contract_issued_stage = fields.Boolean('Contract Issued Stage', default=False)
