# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Web Widget Color",
    'category': "web",
    'version': "11.0.1.0.0",
    "author": "Rosen Vladimirov, "
              "dXFactoy Ltd., "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/rosenvladimirov/web',
    'conflicts': ['mrp'],
    'depends': ['web'],
    'data': [
        'view/web_widget_pdf_viewer.xml'
    ],
    'qweb': [
        'static/src/xml/widget.xml',
    ],
    'license': 'AGPL-3',
    'auto_install': False,
    'installable': True,
    'web_preload': True,
}
