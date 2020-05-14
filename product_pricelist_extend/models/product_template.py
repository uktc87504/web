# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    company_list_price = fields.Float('Company Sales Price', compute='_compute_company_price', inverse='_set_company_price', default=1.0, digits=dp.get_precision('Product Price'), help="Base price to compute the customer price. Sometimes called the catalog price.")
    company_lst_price = fields.Float('Company Public Price', related='list_price', digits=dp.get_precision('Product Price'))
    min_standard_price = fields.Float(
        'Min Cost', compute='_compute_min_standard_price',
        inverse='_set_min_standard_price', search='_search_min_standard_price',
        digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost used for stock valuation in standard price and as a first price to set in average/fifo. "
             "Also used as a base price for pricelists. "
             "Expressed in the default unit of measure of the product. ")

    @api.depends('product_variant_ids', 'product_variant_ids.min_standard_price')
    def _compute_min_standard_price(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.min_standard_price = template.product_variant_ids.min_standard_price
        for template in (self - unique_variants):
            template.min_standard_price = 0.0

    @api.one
    def _set_min_standard_price(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.min_standard_price = self.min_standard_price

    def _search_min_standard_price(self, operator, value):
        products = self.env['product.product'].search([('min_standard_price', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]

    @api.multi
    def _compute_company_price(self):
        pricelist = self.env['product.pricelist'].browse(self.env.user.company_id.default_pricelist_id.id)
        if not pricelist:
            raise ValidationError(_("Not default pricelist for company"))
        prices = pricelist.get_products_price(self, [1.0]*len(self), [self.env.user.company_id.partner_id]*len(self))
        for template in self:
            template.company_list_price = prices.get(template.id, 0.0)

    @api.multi
    def _set_company_price(self):
        for template in self:
            value = self.env['product.uom'].browse(template.uom_id.id)._compute_price(template.company_list_price, template.uom_id)
            #template.write({'company_list_price': value})
            pricelist = self.env['product.pricelist'].browse(self.env.user.company_id.default_pricelist_id.id)
            if not pricelist:
                raise ValidationError(_("Not default pricelist for company"))
            if template.company_list_price > 0.0:
                price_item = pricelist.item_ids.filtered(lambda r: r.product_tmpl_id.id == template.id and r.compute_price == 'fixed')
                if not price_item:
                    price_item.create({
                                        'pricelist_id': pricelist.id,
                                        'product_tmpl_id': template.id,
                                        'applied_on': '1_product',
                                        'compute_price': 'fixed',
                                        'fixed_price': value,
                                        })
                else:
                    price_item.write({'fixed_price': value})
