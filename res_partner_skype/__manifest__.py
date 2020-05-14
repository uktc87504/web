# Copyright 2016 robyf70  <https://github.com/robyf70 >
# Copyright 2019 Artem Rafailov <https://it-projects.info/team/Ommo73/>
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl.html).
{
    "name": """Skype field for partners""",
    "summary": """This module adds a Skype field along with a widget to integrate Skype chat window of the contact account while clicking on it.""",
    "category": "Discuss",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": ['images/partner.png'],
    "version": "11.0.2.0.0",
    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://twitter.com/yelizariev",
    "license": "LGPL-3",
    "depends": [
        "web"
    ],
    "data": [
        'views/res_partner_views.xml',
        'views/template.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],
    "installable": True,
}
