# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    loyalty_points = fields.Integer(string='Loyalty Points', compute='_loyalty_points', store=True)
    future_loyalty_points = fields.Integer(string='Potential Loyalty Points', compute='_loyalty_points', store=True)
    payed_loyalty_points = fields.Integer("Payed loyalty Points", compute='_loyalty_points', store=True)

    @api.one
    @api.depends('invoice_line_ids', 'invoice_line_ids.sale_line_ids')
    def _loyalty_points(self):
        for line in self.invoice_line_ids:
            for order_line in line.sale_line_ids:
                self.loyalty_points = self.loyalty_points + sum([l.loyalty_points for l in order_line])
                self.future_loyalty_points = self.future_loyalty_points + sum([l.future_loyalty_points for l in order_line])
                self.payed_loyalty_points = self.payed_loyalty_points + sum([l.payed_loyalty_points for l in order_line])

    @api.one
    def force_calculate_points(self):
        self.loyalty_points = 0
        self.future_loyalty_points = 0
        self.payed_loyalty_points = 0
        for line in self.invoice_line_ids:
            for order_line in line.sale_line_ids:
                self.loyalty_points = self.loyalty_points + sum(
                    [l.loyalty_points for l in order_line])
                self.future_loyalty_points = self.future_loyalty_points + sum(
                    [l.future_loyalty_points for l in order_line])
                self.payed_loyalty_points = self.payed_loyalty_points + sum(
                    [l.payed_loyalty_points for l in order_line])

    @api.multi
    def action_cancel(self):
        for invoice in self:
            invoice.loyalty_points = 0
            invoice.future_loyalty_points = 0
        return super(AccountInvoice, self).action_cancel()
