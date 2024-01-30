from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_dis_ter_ids = fields.One2many('employee.disability.termination','related_dis_id')

    def action_business_requirement(self):

        action = {
            'name': 'Employee Business Requirement Termination',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.disability.termination',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_dis_id': self.id},

        }

        return action