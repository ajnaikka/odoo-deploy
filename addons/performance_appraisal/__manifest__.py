# -*- coding: utf-8 -*-
{
    'name': "Performance Appraisal",

    'summary': "Performance appraisal",

    'description': """
        Performance appraisal
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "https://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Employees',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'loyal_employment_application_form', 'job_requisition', 'tf_approval_user_groups'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/appraisal_security.xml',
        'data/mail_template.xml',
        'views/views.xml',
    ],
    "license": "LGPL-3",
}

