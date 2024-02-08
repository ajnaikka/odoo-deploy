# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'TF Exit Checklist',
    'version': '1.2',
    'summary': 'TF Exit Checklist',
    'sequence': -100,
    'description': """TF Exit Checklist""",
    'category': 'hr',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['base','hr','mail','hr_contract','contacts','tf_end_of_service','tf_approval_user_groups'],
    'data': [
          'security/ir.model.access.csv',
          'wizard/department.xml',
          'views/exit_form.xml',
    ],
    'demo': [],
    'module_type': 'official',
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}