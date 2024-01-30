from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_bus_con_ids = fields.One2many('employee.business.requirement','related_emp_bus_id')

    def action_business_requirement(self):

        action = {
            'name': 'Employee Business Requirement Termination',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.business.requirement',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_bus_id': self.id},

        }

        return action