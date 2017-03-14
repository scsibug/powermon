import falcon
import json
import psycopg2
from settings import *

conn = psycopg2.connect(pg_conn_str)


home_query_SQL = "select to_char(date_trunc('second',sample_time at time zone 'CDT'),'YYYY-MM-DD HH24:MI:SS'), watts from today_10m_usage where meter_id=30"

class HomeReportResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Query
        curs = conn.cursor() 
        curs.execute(home_query_SQL)
        csv="sample_time,watts\n"
        for record in curs:
            csv+= str(record[0]) +","+ str(record[1]) + "\n"
        resp.body = csv
api = falcon.API()
api.add_route('/home-report', HomeReportResource())
