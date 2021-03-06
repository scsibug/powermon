import falcon
import json
import psycopg2
from settings import *

conn = psycopg2.connect(pg_conn_str)
conn.set_session(autocommit=True)


home_query_SQL = "select to_char(date_trunc('second',sample_time at time zone 'CDT'),'YYYY-MM-DD HH24:MI:SS'), watts from today_30m_usage where meter_id=30"
last_day_SQL = "select daily_usage from last_day_usage"
my_last_month_SQL = "select monthly_usage from last_month_usage where meter_id=30"
last_month_SQL = "select meter_id, monthly_usage from last_month_usage"
last_month_hist_SQL = "select meter_id,  to_char(date_trunc('second',sample_time at time zone 'CDT'),'YYYY-MM-DD HH24:MI:SS'), watts from month_24h_usage"
my_last_month_hist_SQL = "select meter_id,  to_char(date_trunc('second',sample_time at time zone 'CDT'),'YYYY-MM-DD HH24:MI:SS'), watts from month_24h_usage where meter_id=30"

class LastDayUsage:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Query
        curs = conn.cursor() 
        curs.execute(last_day_SQL)
        csv = "Last 24 Hour Usage\n"
        for record in curs:
            csv+= str(float(record[0])) + "\n"
        resp.body = csv

class MyLastMonthUsage:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Query
        curs = conn.cursor() 
        curs.execute(my_last_month_SQL)
        csv = "Last 30 Day Usage\n"
        for record in curs:
            csv+= str(float(record[0])) + "\n"
        resp.body = csv

class LastMonthUsage:
    def on_get(self, req, resp):
        """Handles GET requests"""
        # Query
        curs = conn.cursor() 
        curs.execute(last_month_SQL)
        csv = "Last 30 Day Usage\n"
        for record in curs:
            csv+= str(record[0]) +","+ str(float(record[1])) + "\n"
        resp.body = csv

class LastMonthHistory:
    def on_get(self, req, resp):
        """Show the full history of the last month usage, by day"""
        # Query
        curs = conn.cursor()
        curs.execute(last_month_hist_SQL)
        csv = "Meter,sample_time,Watts/Day\n"
        for record in curs:
            csv+=str(record[0]) +","+str(record[1])+","+str(float(record[2])) + "\n"
        resp.body = csv

class MyLastMonthHistory:
    def on_get(self, req, resp):
        """Show the full history of the last month usage, by day"""
        # Query
        curs = conn.cursor()
        curs.execute(my_last_month_hist_SQL)
        csv = "sample_time,Watts\n"
        for record in curs:
            csv+=str(record[1]) +","+str(float(record[2])) + "\n"
        resp.body = csv

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
api.add_route('/last-day-usage',LastDayUsage())
api.add_route('/my-last-month-usage',MyLastMonthUsage())
api.add_route('/last-month-usage',LastMonthUsage())
api.add_route('/last-month-history',LastMonthHistory())
api.add_route('/my-last-month-history',MyLastMonthHistory())
