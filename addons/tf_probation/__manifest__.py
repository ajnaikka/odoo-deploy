# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'TF probation',
    'version': '1.2',
    'summary': 'TF probation',
    'sequence': -100,
    'description': """TF probation""",
    'category': 'hr',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['base','hr','mail','hr_contract','contacts','tf_employee_referral'],
    'data': [
          'data/data.xml',
          'security/ir.model.access.csv',
          'security/security.xml',
          'views/probation_penalty.xml',
          # 'views/report.xml'
    ],
    'demo': [],
    'module_type': 'official',
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}