# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    code = fields.Char('Code', translate=True)

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for item in self:
            name = item.name
            if item.code:
                name = '[%s] %s' % (item.code, name)
            result.append((item.id, name))
        return result
