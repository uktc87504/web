# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Products & Pricelists Extend',
    'version': '11.0.0.1.0',
    'category': 'Sales',
    'depends': ['product'],
    'description': """
Fix the rules for pricelist.
    """,
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
