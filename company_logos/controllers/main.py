# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import functools
import base64
import imghdr
import io

import odoo

from odoo import http
from odoo.modules import get_resource_path
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo.service import db

db_monodb = http.db_monodb

class Binary(http.Controller):

    @http.route([
        '/web/binary/company_logo_email',
        '/logo_email',
        '/logo_email.png',
    ], type='http', auth="none", cors="*")
    def company_email_logo(self, dbname=None, **kw):
        imgname = 'logo_email'
        imgext = '.png'
        placeholder = functools.partial(get_resource_path, 'l10n_bg_extend', 'static', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = odoo.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname + imgext))
        else:
            try:
                # create an empty registry
                registry = odoo.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    company = int(kw['company']) if kw and kw.get('company') else False
                    lang = kw['lang'] if kw and kw.get('lang') else 'en_EN'
                    mail_name = 'logo_mail_%s' % lang.split("_")[0]
                    cr.execute("SELECT column_name FROM information_schema.columns "
                               "WHERE table_name = 'res_partner' AND column_name = '%s'", (mail_name,))
                    if not cr.fetchone():
                        mail_name = 'logo_mail'
                    if company:
                        cr.execute("""SELECT %s, write_date
                                        FROM res_company
                                       WHERE id = %s
                                   """, (mail_name, company,))
                    else:
                        cr.execute("""SELECT c.%s, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                                   """, (mail_name, uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_base64 = base64.b64decode(row[0])
                        image_data = io.BytesIO(image_base64)
                        imgext = '.' + (imghdr.what(None, h=image_base64) or 'png')
                        response = http.send_file(image_data, filename=imgname + imgext, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('nologo.png'))
            except Exception:
                response = http.send_file(placeholder(imgname + imgext))

        return response

