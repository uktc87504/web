# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class LoyaltySaleRecalculate(models.TransientModel):
    _name = 'loyalty.sale.recalculate'
    _description = "Wizard model to recalculate loyalty poins in sele order"

    loyalty_break = fields.Boolean('Used')
    loyalty_break_date = fields.Date('Date of used')

    @api.multi
    def sale_recal_loyalty(self):
        so_ids = self._context['active_ids'] or self._context['active_id']
        if not so_ids:
            return
        order_obj = self.env['sale.order']
        so = order_obj.browse(so_ids)
        for sale in so:
            sale.loyalty_break = self.loyalty_break
            sale.loyalty_break_date = self.loyalty_break_date
            sale.onchange_loyalty_break()

    @api.multi
    def sale_only_loyalty(self):
        so_ids = self._context['active_ids'] or self._context['active_id']
        if not so_ids:
            return
        order_obj = self.env['sale.order']
        so = order_obj.browse(so_ids)
        for sale in so:
            sale.onchange_loyalty_break()