# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    default_pricelist_id = fields.Many2one('product.pricelist', 'Sale Pricelist', help="This pricelist will be used, instead of the default one, for sales to the current company")
