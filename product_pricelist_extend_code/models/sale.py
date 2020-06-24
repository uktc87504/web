# -*- coding: utf-8 -*-

from odoo import fields, api, models, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    #def prepare_sale_order_line_set_data(self, sale_order_id, set, set_line, qty, set_id,
    #                                 max_sequence=0, old_qty=0, old_pset_qty=0, split_sets=False):
    #    line_values = super(SaleOrder, self).prepare_sale_order_line_set_data(sale_order_id, set, set_line, qty, set_id,
    #                                 max_sequence=max_sequence, old_qty=old_qty, old_pset_qty=old_pset_qty, split_sets=split_sets)
    #    line_values = dict(line_values, code=set_line.pricelist_rule_id.code)
    #    #line_values = dict(line_values, pricelist_rule_id=set_line.pricelist_rule_id.id)
    #    #_logger.info("GET %s" % line_values)
    #    return line_values

    @api.multi
    def order_lines_sets_layouted(self):
        report_pages_sets = super(SaleOrder, self).order_lines_sets_layouted()
        if len(report_pages_sets[-1]) > 0:
            codes = set([])
            for val in report_pages_sets[-1]:
                if val.get('pset'):
                    val["codes"] = False
                    for line in val['lines']:
                        if 'code' in line._fields and line.code:
                            codes.update([line.code])
                    if codes:
                        val["codes"] = list(codes)
        #_logger.info("PSET %s" % report_pages_sets)
        return report_pages_sets

    def prepare_sale_order_line_set_data(self, sale_order_id, set, set_line, qty, set_id,
                                     max_sequence=0, old_qty=0, old_pset_qty=0, split_sets=False):
        line_values = super(SaleOrder, self).prepare_sale_order_line_set_data(sale_order_id, set, set_line, qty, set_id,
                                     max_sequence=max_sequence, old_qty=old_qty, old_pset_qty=old_pset_qty, split_sets=split_sets)
        line_values['pricelist_rule_id'] = set_line.pricelist_rule_id.id
        if set_line.product_id:
            so = self.env['sale.order'].browse([sale_order_id])
            line_values['code'] = set_line.product_id.with_context(pricelist=so.pricelist_id.id, product_set_id=line_values['product_set_id']).pricelist_code
        return line_values


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_rule_id = fields.Many2one('product.pricelist.item', string='Pricelist Rule')
    code = fields.Char('Code')

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        values.update({'code': self.code})
        return values

    @api.multi
    def _prepare_invoice_line(self, qty):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.code:
            res.update({'code': self.code})
        return res

    #@api.multi
    #def _get_display_price(self, product):
    #    for sale in self:
    #        #if not sale.code and sale.order_id.pricelist_id.discount_policy == 'with_discount':
    #        sale.code = product.with_context(pricelist=sale.order_id.pricelist_id.id).pricelist_code
    #    return super(SaleOrderLine, self)._get_display_price(product)

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.code = self.product_id.with_context(pricelist=self.order_id.pricelist_id.id, product_set_id=self.product_set_id.id).pricelist_code
        return res

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        if not self.code and rule_id:
            PricelistItem = self.env['product.pricelist.item'].sudo().browse(rule_id)
            if PricelistItem:
                self.code = PricelistItem.code
                self.pricelist_rule_id = rule_id
        return super(SaleOrderLine, self)._get_real_price_currency(product, rule_id, qty, uom, pricelist_id)
