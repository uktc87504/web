# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import chain

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

from odoo.addons import decimal_precision as dp

from odoo.tools import pycompat

import logging
_logger = logging.getLogger(__name__)

class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _add_where(self, products):
        return False, []

    def _rule(self, product, qty, partner, rule):
        return None

    def _filter(self, product, qty, partner, rule):
        return None

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = products and [tmpl.id for tmpl in products] or []
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = products and [product.id for product in products] or []
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        where_sql_add, where_arg_add = self._add_where(products)
        select_query = """
SELECT item.id 
    FROM product_pricelist_item AS item 
    LEFT JOIN product_category AS categ 
    ON item.categ_id = categ.id 
    WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s)) 
    AND (item.product_id IS NULL OR item.product_id = any(%s)) 
    AND (item.categ_id IS NULL OR item.categ_id = any(%s)) 
"""
        add_query = """
    AND (item.pricelist_id = %s) 
    AND (item.date_start IS NULL OR item.date_start<=%s) 
    AND (item.date_end IS NULL OR item.date_end>=%s)
    ORDER BY item.applied_on, item.sequence, item.min_quantity desc, categ.parent_left desc;
"""

        if where_sql_add:
            query = select_query+where_sql_add+add_query
            where = [prod_tmpl_ids, prod_ids, categ_ids]+where_arg_add+[self.id, date, date]
        else:
            query = select_query+add_query
            where = [prod_tmpl_ids, prod_ids, categ_ids]+[self.id, date, date]
        #_logger.info("PRICE LIST %s:%s:%s:%s:%s:%s:%s" % (prod_tmpl_ids, prod_ids, categ_ids, where_arg_add, self.id, date, date))
        #_logger.info("SQL %s" % query)
        # Load all rules
        self._cr.execute(query,
            tuple(where))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                #_logger.info("PRICELIST PRODUCT %s:::%s:%s:tmpl:%s" % (self._context, product.name, rule.name, is_product_template))
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if where_sql_add:
                    has_add_rule = self._rule(product, qty, partner, rule)
                    if has_add_rule != None and has_add_rule:
                        continue

                has_filtered = self._filter(product, qty, partner, rule)
                if has_filtered != None and has_filtered:
                    continue


                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)])[product.id][0]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))
                #_logger.info("Filter %s:%s:%s:%s:%s" % (has_filtered, rule.base, price, rule.compute_price, rule.price_discount))
                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (price - (price * (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (price - (price * (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if (suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist') or (self.currency_id.id != product.currency_id.id):
                price = product.currency_id.compute(price, self.currency_id, round=False)
            #_logger.info("PRICE LIST END %s:%s:TO CURRENCY:%s:FROM CURRENCY:%s:%s" % (self.id, price, self.currency_id, product.currency_id, suitable_rule))
            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _order = "applied_on, sequence, min_quantity desc, categ_id desc, id"

    sequence = fields.Integer('Sequence', help="Determine the display order")

