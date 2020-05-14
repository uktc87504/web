# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

class ProductAttributePrice(models.Model):
    _inherit = "product.attribute.price"

    price_extra = fields.Float(company_dependent=True)
