# -*- coding: utf-8 -*-
{
    'name': "tf_end_of_service",

    'summary': "End of Service Request",

    'description': """
    End of Service Request
        """,

    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'mail', 'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_employee.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
