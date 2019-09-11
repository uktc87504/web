# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.tools import pycompat

import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    #pricelist_rule_id = fields.Many2one('product.pricelist.item', string='Pricelist Rule', compute='_compute_product_price_rule')
    pricelist_code = fields.Char('Code', translate=True, compute='_compute_product_price_rule')

    def _compute_product_price_rule(self):
        pricelist_id_or_name = self._context.get('pricelist')
        pricelist_item = {}
        if pricelist_id_or_name:
            pricelist = None
            partner = self._context.get('partner', False)
            quantity = self._context.get('quantity', 1.0)

            # Support context pricelists specified as display_name or ID for compatibility
            if isinstance(pricelist_id_or_name, pycompat.string_types):
                pricelist_name_search = self.env['product.pricelist'].name_search(pricelist_id_or_name, operator='=',
                                                                                  limit=1)
                if pricelist_name_search:
                    pricelist = self.env['product.pricelist'].browse([pricelist_name_search[0][0]])
            elif isinstance(pricelist_id_or_name, pycompat.integer_types):
                pricelist = self.env['product.pricelist'].browse(pricelist_id_or_name)

            if pricelist:
                quantities = [quantity] * len(self)
                partners = [partner] * len(self)
                pricelist_item = pricelist.price_rule_get_multi(list(pycompat.izip(self, quantities, partners)))

        for product in self:
            rule_id = pricelist_item.get(product.id) and pricelist_item.get(product.id).get(pricelist.id)[1]
            if rule_id:
                pricelist_code = self.env['product.pricelist.item'].browse([rule_id])
                if pricelist_code:
                    product.pricelist_code = pricelist_code.code
