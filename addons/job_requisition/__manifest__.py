# -*- coding: utf-8 -*-
{
    'name': "Job Requisition",

    'summary': "Job requisition",

    'description': """
        Job requisition
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "https://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Employees',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_recruitment', 'grading_structure'],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'data/manager_mail_template.xml',
        'data/mail_template.xml',
        'security/ir.model.access.csv',
        'security/job_security.xml',
        'wizard/manager_reject_view.xml',
        'views/hr_job_view.xml',
        'views/views.xml',
        'views/job_description_view.xml',
        'views/res_config_settings_view.xml',
    ],
    "license": "LGPL-3",
}

