# -*- coding: utf-8 -*-

from odoo import fields, api, models, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def prepare_sale_order_line_set_data(self, sale_order_id, set, set_line, qty, set_id,
                                     max_sequence=0, old_qty=0, old_pset_qty=0, split_sets=False):
        line_values = super(SaleOrder, self).prepare_sale_order_line_set_data(sale_order_id, set, set_line, qty, set_id,
                                     max_sequence=max_sequence, old_qty=old_qty, old_pset_qty=old_pset_qty, split_sets=split_sets)
        line_values = dict(line_values, code=set_line.pricelist_rule_id.code)
        #_logger.info("GET %s" % line_values)
        return line_values


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    #pricelist_rule_id = fields.Many2one('product.pricelist.item', string='Pricelist Rule')
    code = fields.Char('Code', translate=True)

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({'code': self.code})
        return values

    @api.multi
    def _get_display_price(self, product):
        if not self.code and self.order_id.pricelist_id.discount_policy == 'with_discount':
            self.code = product.with_context(pricelist=self.order_id.pricelist_id.id).pricelist_code
        return super(SaleOrderLine, self)._get_display_price(product)

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        if not self.code and rule_id:
            self.code = rule_id.code
        return super(SaleOrderLine, self)._get_real_price_currency(product, rule_id, qty, uom, pricelist_id)
