# -*- coding: utf-8 -*-
{
    'name': "Happy & Ruby User Group",

    'summary': """
        User group for Happy & Ruby""",

    'description': """
        User group for Happy & Ruby
    """,

    'author': "Loyal IT Solutions PVT LTD",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Hidden/Tools',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/user_group.xml',
    ],
    'license': 'LGPL-3',
}
