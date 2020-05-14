# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class Company(models.Model):
    _inherit = "res.company"

    logo_report_src = fields.Binary("Logo for external header in German")
    logo_report = fields.Char(compute='_compute_logo_report', search='_name_search_logo_report', store=False, index=False)
    logo_email_src = fields.Binary("Logo for email")
    logo_email = fields.Char(compute='_compute_logo_email', search='_name_search_logo_email', store=False, index=False)

    @api.multi
    def _compute_logo_report(self):
        for company in self:
            lang = company.partner_id.lang
            lang_name = 'logo_report_%s' % lang.split("_")[0]
            if self._context.get('res_partner_lang', False):
                lang_name = 'logo_report_%s' % self._context['res_partner_lang'].split("_")[0]
            if not lang_name in self._fields:
                lang_name = 'logo_report_src'
            company.logo_report = getattr(self, lang_name)

    @api.multi
    def _compute_logo_email(self):
        for company in self:
            lang = company.partner_id.lang
            lang_name = 'logo_email_%s' % lang.split("_")[0]
            if self._context.get('res_partner_lang', False):
                lang_name = 'logo_email_%s' % self._context['res_partner_lang'].split("_")[0]
            if not lang_name in self._fields:
                lang_name = 'logo_email_src'
            company.logo_email = getattr(self, lang_name)

    def _name_search_logo_email(self, operator, value):
        logo_email = 'logo_email_src'
        lang = self.env.user.sudo().lang
        lang_name = 'logo_mail_%s' % lang.split("_")[0]
        if lang_name in self._fields and len(value.encode('ascii', 'ignore')) != len(value):
            logo_email = lang_name
        if operator in ('ilike') and len(value.split()) > 1:
            operator = '%'
        return [(logo_email, operator, value)]

    def _name_search_logo_report(self, operator, value):
        logo_report = 'logo_report_src'
        lang = self.env.user.sudo().lang
        lang_name = 'logo_report_%s' % lang.split("_")[0]
        if lang_name in self._fields and len(value.encode('ascii', 'ignore')) != len(value):
            logo_report = lang_name
        if operator in ('ilike') and len(value.split()) > 1:
            operator = '%'
        return [(logo_report, operator, value)]
