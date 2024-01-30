# -*- coding: utf-8 -*-
{
    'name': "Grading Structure",

    'summary': "Grading structure",

    'description': """
        Grading structure
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "https://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Employees',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/grading_security.xml',
        'views/views.xml',
    ],
    "license": "LGPL-3",
}

