# -*- coding: utf-8 -*-
{
    'name': "T-Force HR Recruitment",

    'summary': "Processing Applicants",

    'description': """
        Processing Applicants
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "https://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Recruitment',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/hr_recruitment_stage_view.xml',
        'wizard/contract_email_view.xml',
        'views/hr_applicant_view.xml',
    ],
    "license": "LGPL-3",
}

