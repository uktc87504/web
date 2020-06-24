# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from functools import reduce

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def order_lines_sets_layouted(self):
        report_pages_sets = super(AccountInvoice, self).order_lines_sets_layouted()
        if len(report_pages_sets[-1]) > 0:
            for val in report_pages_sets[-1]:
                codes = {}
                if val.get('pset'):
                    if not codes.get(val['pset']):
                        codes[val['pset']] = set([])
                    val["codes"] = False
                    for line in val['lines']:
                        if 'code' in line._fields and line.code:
                            codes[val['pset']].update([line.code])
                    if codes:
                        val["codes"] = list(set(reduce(lambda x, y: list(x)+list(y), list(codes.values()))))
        #_logger.info("PSET %s" % report_pages_sets)
        return report_pages_sets


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    code = fields.Char('Code')
