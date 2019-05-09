# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    company_price_unit = fields.Float('Company Unit Price', related="product_id.company_lst_price", digits=dp.get_precision('Product Price'))
