# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    loyalty_program_id = fields.Many2one(comodel_name='loyalty.program', string='Loyalty Program')
    loyalty_points = fields.Integer(string='Loyalty Points', compute='_loyalty_points', store=True)
    future_loyalty_points = fields.Integer(string='Potential Loyalty Points', compute='_loyalty_points', store=True)
    loyalty_id = fields.Many2one(comodel_name='account.loyalty', string='Loyalty')
    loyalty_break = fields.Boolean('Used')
    loyalty_break_date = fields.Date('Date of used')
    payed_loyalty_points = fields.Integer("Payed loyalty Points")

    @api.one
    @api.depends('order_line', 'order_line.future_loyalty_points', 'order_line.loyalty_points')
    def _loyalty_points(self):
        self.loyalty_points = sum([l.loyalty_points for l in self.order_line])
        self.future_loyalty_points = sum([l.future_loyalty_points for l in self.order_line])

    @api.onchange('loyalty_break', 'order_line')
    def onchange_loyalty_break(self):
        if self.loyalty_program_id:
            self.order_line.set_loyalty_points()
            if self.loyalty_break:
                self.payed_loyalty_points = sum([l.payed_loyalty_points for l in self.order_line])
            else:
                self.payed_loyalty_points = 0
            self.loyalty_points = sum([l.loyalty_points for l in self.order_line])
            self.future_loyalty_points = sum([l.future_loyalty_points for l in self.order_line])
            for inv in self.invoice_ids:
                inv.force_calculate_points()

    @api.onchange('loyalty_program_id')
    def onchange_loyalty_program_id(self):
        if self.loyalty_program_id:
            self.order_line.set_loyalty_points()
            self.loyalty_points = sum([l.loyalty_points for l in self.order_line])
            self.future_loyalty_points = sum([l.future_loyalty_points for l in self.order_line])

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if not self.loyalty_program_id:
            self.loyalty_program_id = self.partner_id.loyalty_program_id
        return super(SaleOrder, self).onchange_partner_id()

    @api.multi
    def force_calculate_points(self):
        for order in self:
            if order.loyalty_program_id:
                order.order_line.set_loyalty_points()
                if order.loyalty_break:
                    order.payed_loyalty_points = sum([l.payed_loyalty_points for l in order.order_line])
                else:
                    order.payed_loyalty_points = 0
                order.loyalty_points = sum([l.loyalty_points for l in order.order_line])
                order.future_loyalty_points = sum([l.future_loyalty_points for l in self.order_line])
                for inv in order.invoice_ids:
                    inv.force_calculate_points()

    @api.multi
    def action_cancel(self):
        ret = super(SaleOrder, self).action_cancel()
        for order in self:
            for line in order.order_line:
                line.write({'loyalty_points': 0, 'future_loyalty_points': 0, 'payed_loyalty_points': 0})
            order.loyalty_points = sum([l.loyalty_points for l in order.order_line])
            order.future_loyalty_points = sum([l.future_loyalty_points for l in order.order_line])
        return ret

    @api.multi
    def action_confirm(self):
        ret = super(SaleOrder, self).action_confirm()
        for order in self:
            order.order_line.set_loyalty_points()
            if order.loyalty_break:
                order.payed_loyalty_points = sum([l.payed_loyalty_points for l in order.order_line])
            else:
                order.payed_loyalty_points = 0
            order.loyalty_points = sum([l.loyalty_points for l in self.order_line])
            order.future_loyalty_points = sum([l.future_loyalty_points for l in self.order_line])
        return ret


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    loyalty_points = fields.Integer(string='Loyalty Points')
    future_loyalty_points = fields.Integer(string='Potential Loyalty Points')
    payed_loyalty_points = fields.Integer(string="Payed loyalty Points")

    @api.one
    def calculate_loyalty_points(self, product, qty, price, **kwargs):
        return self.order_id.loyalty_program_id.calculate_loyalty_points(product, qty, price, **kwargs)

    @api.multi
    def set_loyalty_points(self):
        for record in self:
            if record.order_id.loyalty_program_id:
                if not record.order_id.loyalty_break:
                    record.payed_loyalty_points = 0

                if record.qty_invoiced > 0:
                    record.loyalty_points = record.calculate_loyalty_points(record.product_id, record.qty_invoiced,
                                                                        record.price_subtotal)

                if record.qty_invoiced > 0 and record.order_id.loyalty_break:
                    record.payed_loyalty_points = record.loyalty_points
                    record.loyalty_points = 0

                if record.product_uom_qty > 0:
                    record.future_loyalty_points = record.calculate_loyalty_points(record.product_id, record.product_uom_qty,
                                                                               record.price_subtotal)
