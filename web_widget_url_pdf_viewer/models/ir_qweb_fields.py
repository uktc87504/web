# -*- coding: utf-8 -*-

import base64
import urllib.parse

from io import BytesIO

from odoo import models, api, fields, _
from odoo.tools import html_escape as escape, posix_to_ldml, safe_eval, float_utils, format_date, pycompat
from odoo.addons.website.controllers.main import QueryURL

import logging
_logger = logging.getLogger(__name__)

class Url_pdf_viewerConverter(models.AbstractModel):
    """ ``url_pdf_viewer`` widget rendering, inserts a data:uri-using pdf file tag in the
    document. May be overridden by e.g. the website module to generate links
    instead.

    .. todo:: what happens if different output need different converters? e.g.
              reports may need embedded images or FS links whereas website
              needs website-aware
    """
    _name = 'ir.qweb.field.url_pdf_viewer'
    _description = 'Qweb Field PDF URL'
    _inherit = 'ir.qweb.field'

    @api.model
    def value_to_html(self, value, options):
        #_logger.info("OPTIONS %s" % options)
        pdf_url = html_escape(string, options)
        return u'<div class="o_form_view"><iframe class="o_field_pdfviewer" src="/web/static/lib/pdfjs/web/viewer.html?file=%s#page=1&zoom=125"></iframe></div>' % (urllib.parse.quote(pdf_url), )
