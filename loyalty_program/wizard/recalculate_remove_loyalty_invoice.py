# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class LoyaltyInvoiceRecalculate(models.TransientModel):
    _name = 'loyalty.invoice.recalculate'
    _description = "Wizard model to recalculate loyalty poins in invoice"

    loyalty_break = fields.Boolean('Used')
    loyalty_break_date = fields.Date('Date of used')

    @api.multi
    def sale_recal_loyalty(self):
        inv_ids = self._context['active_ids'] or self._context['active_id']
        if not inv_ids:
            return
        invoices = self.env['account.invoice'].browse(inv_ids)
        for inv in invoices:
            sale_order = False
            for line in inv.invoice_line_ids:
                if not sale_order:
                    sale_order = line.sale_line_ids.mapped('order_id')
                else:
                    sale_order |= line.sale_line_ids.mapped('order_id')
            if sale_order:
                for sale in sale_order:
                    sale.loyalty_break = self.loyalty_break
                    sale.loyalty_break_date = self.loyalty_break_date
                    sale.onchange_loyalty_break()

    @api.multi
    def sale_only_loyalty(self):
        inv_ids = self._context['active_ids'] or self._context['active_id']
        if not inv_ids:
            return
        invoices = self.env['account.invoice'].browse(inv_ids)
        for inv in invoices:
            sale_order = False
            for line in inv.invoice_line_ids:
                if not sale_order:
                    sale_order = line.sale_line_ids.mapped('order_id')
                else:
                    sale_order |= line.sale_line_ids.mapped('order_id')
            if sale_order:
                for sale in sale_order:
                    sale.onchange_loyalty_break()
