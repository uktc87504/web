
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class ProductSetLine(models.TransientModel):
    _inherit = 'product.set.add.line'

    pricelist_rule_id = fields.Many2one('product.pricelist.item', string='Pricelist Rule')
    code = fields.Char('Code', translate=True)

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env['product.pricelist.item'].sudo()
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            self.pricelist_rule_id = rule_id
            self.code = pricelist_item.code
        return super(ProductSetLine, self)._get_real_price_currency(product, rule_id, qty, uom, pricelist_id)
