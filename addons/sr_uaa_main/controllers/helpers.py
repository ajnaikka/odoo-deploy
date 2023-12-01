from itertools import islice

import re
import json

from odoo import http
from odoo.http import request

class WebsiteHelpers(http.Controller):

    @http.route(["/api/website/get-all-countries"], type="http", auth="none", csrf=False, cors="*")
    def get_all_countries(self, **post):
        where_str = ""
        if post.get("term"):
            where_str = "%s WHERE rc.name ILIKE '%%%s%%' or rc.code ILIKE '%%%s%%' or CAST(rc.phone_code AS TEXT) ILIKE '%%%s%%'" % (where_str, post.get("term"), post.get("term"), post.get("term"))
        # query = """ SELECT rc.id, rc.name FROM res_country rc %s """ % where_str
        query = """ SELECT rc.id, CONCAT(rc.name, ' (', '+',rc.phone_code, ')') as name FROM res_country rc %s """ % where_str
        request.env.cr.execute(query)
        all_countries = request.env.cr.dictfetchall()
        return json.dumps({
            "results": all_countries
        })

    @http.route(["/api/website/get-all-airports"], type="http", auth="none", csrf=False, cors="*")
    def get_all_airports(self, **post):
        where_str = ""
        if post.get("term"):
            where_str = "%s WHERE rc.name ILIKE '%%%s%%' or rc.code ILIKE '%%%s%%' or country.name ILIKE '%%%s%%' or country.code ILIKE '%%%s%%' and rc.active=true" % (where_str, post.get("term"), post.get("term"), post.get("term"), post.get("term"))
        query = """ SELECT rc.id, CONCAT(rc.name, ' (', rc.code, ')', ' / ', country.name ) as name FROM admin_airport rc left join res_country country on country.id = rc.country_id %s """ % where_str
        request.env.cr.execute(query)
        all_airports = request.env.cr.dictfetchall()
        return json.dumps({
            "results": all_airports
        })

