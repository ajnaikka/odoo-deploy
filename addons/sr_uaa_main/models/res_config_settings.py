# © 2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    notification_mail = fields.Char('Notification Mail')
    sale_order_default_validity_hours = fields.Integer(
        related="company_id.default_sale_order_validity_hours",
        readonly=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        notification_mail = params.get_param('notification_mail', default=False)
        res.update(
            notification_mail=notification_mail
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("notification_mail",
                                                         self.notification_mail)
