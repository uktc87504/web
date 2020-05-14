# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Different logos",
    "version" : "11.0.2.0",
    "author" : "dXFactory Ltd.",
    'category': 'Localization',
    "description": """
Diferent logos for front, back, e-mail templates and reports
    """,
    'depends': [
        'base', 'web',
    ],
    "demo" : [],
    "data" : [
              'views/res_company_view.xml',
              'views/report_templates.xml',
              ],
    "installable": True,
}
