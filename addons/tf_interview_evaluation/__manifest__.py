# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Interview Evaluvation Form',
    'version': '1.2',
    'summary': 'Interview Evaluvation Form',
    'sequence': -100,
    'description': """Interview Evaluvation Form""",
    'category': 'Productivity',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['base','hr','hr_recruitment'],
    'data': [
            'security/ir.model.access.csv',
            'views/hr_recruitment_stage_view.xml',
            'views/ie.xml'

    ],
    'demo': [],
    'module_type': 'official',
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
