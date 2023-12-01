# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 seeroo IT SOLUTIONS PVT.LTD(<http://www.seeroo.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'UAA Dashboard',
    'version': '1.0',
    'category': 'Website/Website',
    'summary': 'Module that contains Dashboard views for UAA project.',
    'description': """Module that contains Dashboard views for UAA project.""",
    'external_dependencies': {
        'python': ['pandas'],
    },
    'depends': ['web',
                'sr_uaa_main'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_view.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'sr_uaa_dashboard/static/lib/dataTables/datatables.min.css',
            'sr_uaa_dashboard/static/lib/dataTables/buttons.dataTables.min.css',
            'sr_uaa_dashboard/static/src/css/hrms_dashboard.css',
            'sr_uaa_dashboard/static/src/css/dashboard.css',
            'sr_uaa_dashboard/static/src/js/dashboard.js',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
            'sr_uaa_dashboard/static/src/xml/dashboard.xml',
        ],
        'web.qunit_suite_tests': [
            'analytic/static/tests/*.js',
        ],
    },
    # 'qweb': ["static/src/xml/dashboard.xml", ],
    'installable': True,
    'auto_install': False,
    'author': 'Seeroo IT Solutions',
    'website': 'https://www.seeroo.com',
}
