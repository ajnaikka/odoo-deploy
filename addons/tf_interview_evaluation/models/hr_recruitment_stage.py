# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    interview_stage = fields.Boolean('Interview Stage', default=False)
