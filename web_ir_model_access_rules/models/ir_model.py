# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, tools,  _


class IrModel(models.Model):
    _inherit = 'ir.model'

    rules_ids = fields.One2many('ir.rule', 'model_id', string='Rules')
