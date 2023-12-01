from datetime import datetime
import pandas as pd
from odoo import models, api, _
from dateutil.relativedelta import relativedelta


class AirportEnquiry(models.Model):
    _inherit = 'airport.enquiry'

    @api.model
    def get_the_country_details(self):
        graph_result = []
        states_list = ['new', 'open', 'close']
        countrys_list = []
        query = """
                  select distinct count(enq.country_id) cnt,
                   air.name,air.id
                   from airport_enquiry enq 
                   left join res_country air on air.id = enq.country_id
                   group by air.name,air.id
                   order by cnt desc 
                   limit 5
        """
        self.env.cr.execute(query)
        country_results = self.env.cr.dictfetchall()
        for airports in country_results:
            countrys_list.append(airports['name'])

        for air in countrys_list:
            cnt = {}
            for state in states_list:
                cnt[state] = 0
            vals = {
                'l_month': air,
                'enquiry': cnt
            }
            graph_result.append(vals)

        sql = """
                SELECT count(h.status),h.status, a.name
                FROM  (select * from airport_enquiry) h,
                 (select * from res_country) a,
                     date_trunc('month', service_date::timestamp) y
                where 
                h.country_id = a.id and
                h.status is not null
                group by a.name,h.status
                order by count(h.status) desc,h.status,a.name 
                """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        countrys_lines = []
        for line in results:
            vals = {
                'status': line['status'],
                'l_month': line['name'],
                'days': line['count']
            }
            countrys_lines.append(vals)
        if countrys_lines:
            df = pd.DataFrame(countrys_lines)
            rf = df.groupby(['l_month', 'status']).sum()
            result_lines = rf.to_dict('index')
            for month in countrys_list:
                for line in result_lines:
                    if month and line[0] != None:

                        if month.replace(' ', '') == line[0].replace(' ', ''):
                            match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['enquiry']
                            dept_name = line[1]
                            if match:
                                match[dept_name] = result_lines[line]['days']
        # for result in graph_result:
        #     result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
        #                         result['l_month'].split(' ')[1:2][0]
        # states_list = ['new', 'open', 'close']
        return graph_result, states_list

    @api.model
    def get_the_airport_details(self):
        graph_result = []
        states_list = ['new', 'open', 'close']
        airports_list = []
        query = """
                  select distinct count(enq.airport_id) cnt,
                   air.name,air.id
                   from airport_enquiry enq 
                   left join admin_airport air on air.id = enq.airport_id
                   group by air.name,air.id
                   order by cnt desc 
                   limit 10
        """
        self.env.cr.execute(query)
        airport_results = self.env.cr.dictfetchall()
        for airports in airport_results:
            airports_list.append(airports['name'])

        for air in airports_list:
            cnt = {}
            for state in states_list:
                cnt[state] = 0
            vals = {
                'l_month': air,
                'enquiry': cnt
            }
            graph_result.append(vals)

        sql = """
                SELECT count(h.status),h.status, a.name
                FROM  (select * from airport_enquiry) h,
                 (select * from admin_airport) a,
                     date_trunc('month', service_date::timestamp) y
                where 
                h.airport_id = a.id and
                h.status is not null
                group by a.name,h.status
                order by count(h.status) desc,h.status,a.name 
                """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        airports_lines = []
        for line in results:
            vals = {
                'status': line['status'],
                'l_month': line['name'],
                'days': line['count']
            }
            airports_lines.append(vals)
        if airports_lines:
            df = pd.DataFrame(airports_lines)
            rf = df.groupby(['l_month', 'status']).sum()
            result_lines = rf.to_dict('index')
            for month in airports_list:
                for line in result_lines:
                    if month and line[0]:
                        if month.replace(' ', '') == line[0].replace(' ', ''):
                            match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['enquiry']
                            dept_name = line[1]
                            if match:
                                match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        # states_list = ['new', 'open', 'close']
        return graph_result, states_list


    @api.model
    def get_the_monthly_enquiry(self):
        graph_result = []
        states_list = ['new', 'open', 'close']
        month_list = []
        query = """
                  select DISTINCT(to_char(y, 'MM-01-YYYY')) as month_year
                    , to_char(y, 'YYYY') as year
                    , extract('month' FROM y)::int AS enquiry_month
                    FROM  (select * from airport_enquiry) h
                     , date_trunc('month', service_date::timestamp) y 
                     where h.service_date is not null
                     order by year desc,enquiry_month desc,month_year limit 6

        """
        self.env.cr.execute(query)
        month_results = self.env.cr.dictfetchall()
        for mont in month_results:
            present_month = datetime.strptime(str(mont['month_year']), '%m-%d-%Y').date()
            text = format(present_month, '%B %Y')
            month_list.append(text)

        # for i in range(6, -1, -1):
        #     last_month = datetime.now() - relativedelta(months=i)
        #     text = format(last_month, '%B %Y')
        #     month_list.append(text)

        for month in month_list:
            cnt = {}
            for state in states_list:
                cnt[state] = 0
            vals = {
                'l_month': month,
                'enquiry': cnt
            }
            graph_result.append(vals)

        sql = """
                SELECT count(h.status),h.status
                     , extract('month' FROM y)::int AS enquiry_month
                     , to_char(y, 'Month YYYY') as month_year
                     , to_char(y, 'YYYY') as year
                     
                FROM  (select * from airport_enquiry) h
                     , date_trunc('month', service_date::timestamp) y
                where 
                h.status is not null
                group by year,enquiry_month,month_year,h.status
                order by year desc,enquiry_month desc
                
                """
        # generate_series(date_trunc('month', service_date::timestamp)
        # , date_trunc('month', service_date::timestamp)
        # , interval
        # '1 month')

        # date_trunc('month', h.service_date) >= date_trunc('month', now()) - interval
        # '6 month' and
        # date_trunc('month', h.service_date) <= date_trunc('month', now()) and

        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        enquiry_lines = []
        for line in results:
            vals = {
                'status': line['status'],
                'l_month': line['month_year'],
                'days': line['count']
            }
            enquiry_lines.append(vals)
        if enquiry_lines:
            df = pd.DataFrame(enquiry_lines)
            rf = df.groupby(['l_month', 'status']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month and line[0]:
                        if month.replace(' ', '') == line[0].replace(' ', ''):
                            match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['enquiry']
                            dept_name = line[1]
                            if match:
                                match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        # states_list = ['new', 'open', 'close']
        return graph_result, states_list

    @api.model
    def get_the_weekly_enquiry(self):
        graph_result = []
        states_list = ['new', 'open', 'close']
        month_list = []

        for i in range(7, -1, -1):
            last_month = datetime.now() - relativedelta(days=i)
            text = format(last_month, '%d %b')
            month_list.append(text)

        for month in month_list:
            cnt = {}
            for state in states_list:
                cnt[state] = 0
            vals = {
                'l_month': month,
                'enquiry': cnt
            }
            graph_result.append(vals)

        sql = """
                    SELECT count(h.status),h.status
                         , extract('day' FROM y)::int AS enquiry_month
                         , to_char(y, 'DD Mon') as month_year
                         , to_char(y, 'YYYY') as year

                    FROM  (select * from airport_enquiry) h
                         , date_trunc('day', service_date::timestamp) y
                    where (service_date > (current_date - interval '7 days') 
                            and service_date <(current_date))
                            and h.status is not null
                    group by year,enquiry_month,month_year,h.status
                    order by year desc,enquiry_month desc

                    """

        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        enquiry_lines = []
        for line in results:
            vals = {
                'status': line['status'],
                'l_month': line['month_year'],
                'days': line['count']
            }
            enquiry_lines.append(vals)
        if enquiry_lines:
            df = pd.DataFrame(enquiry_lines)
            rf = df.groupby(['l_month', 'status']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month and line[0]:
                        if month.replace(' ', '') == line[0].replace(' ', ''):
                            match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['enquiry']
                            dept_name = line[1]
                            if match:
                                match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        # states_list = ['new', 'open', 'close']
        return graph_result, states_list
