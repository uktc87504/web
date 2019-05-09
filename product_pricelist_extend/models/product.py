# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = "product.product"

    company_lst_price = fields.Float('Company Sale Price', compute='_compute_product_company_lst_price',
        digits=dp.get_precision('Product Price'), inverse='_set_product_company_lst_price',
        help="The Company sale price is managed from the product template. Click on the 'Variant Prices' button to set the extra attribute prices.")

    @api.depends('company_list_price', 'price_extra')
    def _compute_product_company_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])

        for product in self:
            if to_uom:
                company_lst_price = product.uom_id._compute_price(product.company_list_price, to_uom)
            else:
                company_lst_price = product.company_list_price
            product.company_lst_price = company_lst_price + product.price_extra

    def _set_product_company_lst_price(self):
        for product in self:
            if self._context.get('uom'):
                value = self.env['product.uom'].browse(self._context['uom'])._compute_price(product.company_lst_price, product.uom_id)
            else:
                value = product.company_lst_price
            value -= product.price_extra
            product.write({'company_list_price': value})
