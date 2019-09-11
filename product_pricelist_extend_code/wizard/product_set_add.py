
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class ProductSetLine(models.TransientModel):
    _inherit = 'product.set.add.line'

    pricelist_rule_id = fields.Many2one('product.pricelist.item', string='Pricelist Rule')

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        if rule_id:
            self.pricelist_rule_id = rule_id
        return super(ProductSetLine, self)._get_real_price_currency(product, rule_id, qty, uom, pricelist_id)
