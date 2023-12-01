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
    'name': 'UAA Excel Reports',
    'version': '1.0',
    'category': 'Website/Website',
    'summary': 'Module that contains Excel Reports for UAA project.',
    'description': """Module that contains Excel Reports for UAA project.""",
    'depends': [
                'report_xlsx',
                'sr_uaa_main'
                ],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_menu.xml',
        'wizards/enquiry_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
    'author': 'Seeroo IT Solutions',
    'website': 'https://www.seeroo.com',
}

