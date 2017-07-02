;;CREATE USER powermon WITH PASSWORD 'your-password-here';
;;CREATE DATABASE powermon OWNER powermon;

;; Meters are devices that broadcast usage information
create table meters (
  id serial primary key,
  name text unique not null,
  description text,
  type integer not null,
);

;; Readers receive meter broadcasts.
create table readers (
  id serial primary key,
  name text unique not null,
  description text
);

;; Each consumption broadcast
create table meter_readings (
  id serial primary key,
  reading integer, -- raw consumption, as sent
  tstamp timestamp with time zone,
  meter serial references meters(id),
  reader serial references readers(id)
);


;; Views

CREATE VIEW sample_view AS
 SELECT s.id AS sample_id, m.id AS meter_id, m.type AS meter_type, s.reading AS consumption, timezone('UTC'::text, s.tstamp) AS tstamp, r.name AS reader
   FROM meters m, meter_readings s, readers r
  WHERE m.id = s.meter AND s.reader = r.id AND (m.type = ANY (ARRAY[4, 5, 7, 8]))
  ORDER BY timezone('UTC'::text, s.tstamp) DESC;

CREATE VIEW my_last_month_usage AS
 SELECT round((max(sample_view.consumption) - min(sample_view.consumption))::numeric / 100.0, 1) AS monthly_usage
   FROM sample_view
  WHERE sample_view.meter_id = 30 AND sample_view.tstamp > (now() - '720:00:00'::interval);
  
CREATE VIEW last_month_usage AS 
 SELECT * FROM (
  SELECT meter_id, round((max(sample_view.consumption) - min(sample_view.consumption))::numeric / 100.0, 1) AS monthly_usage
   FROM sample_view
   WHERE sample_view.tstamp > (now() - '720:00:00'::interval)
   GROUP BY meter_id
   ORDER BY monthly_usage ASC) m
 WHERE monthly_usage > 3;

CREATE VIEW lifetime_mean_wattage AS
 SELECT a.meter_id, round(avg(a.watts)::numeric, 1) AS mean_watts
   FROM ( SELECT s.meter_id, s.end_time, s.watt_hours::double precision / s.hours AS watts
           FROM ( SELECT sample_view.meter_id, max(sample_view.tstamp) AS end_time, 10 * (max(sample_view.consumption) - min(sample_view.consumption)) AS watt_hours, date_part('epoch'::text, max(sample_view.tstamp) - min(sample_view.tstamp)) / 3600::double precision AS hours, round(date_part('epoch'::text, sample_view.tstamp) / (60 * 60)::double precision) AS rounded_tstamp
                   FROM sample_view
                  GROUP BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 60)::double precision), sample_view.meter_id) s
          WHERE s.hours > 0::double precision
          ORDER BY s.meter_id, s.end_time DESC) a
  GROUP BY a.meter_id
  ORDER BY round(avg(a.watts)::numeric, 1);


CREATE VIEW today_10m_usage AS
 SELECT counts.meter_id, counts.sample_count, counts.sample_time, round((counts.watt_hours::double precision / counts.hours)::numeric, 1) AS watts
   FROM ( SELECT sample_view.meter_id, min(sample_view.tstamp) + (max(sample_view.tstamp) - min(sample_view.tstamp)) AS sample_time, count(*) AS sample_count, 10 * (max(sample_view.consumption) - min(sample_view.consumption)) AS watt_hours, date_part('epoch'::text, max(sample_view.tstamp) - min(sample_view.tstamp)) / 3600::double precision AS hours, round(date_part('epoch'::text, sample_view.tstamp) / (60 * 10)::double precision) AS rounded_tstamp
           FROM sample_view
          WHERE sample_view.tstamp > (now() - '24:00:00'::interval)
          GROUP BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 10)::double precision), sample_view.meter_id
          ORDER BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 10)::double precision) DESC) counts
  WHERE counts.sample_count > 5 AND counts.watt_hours > 0;

CREATE VIEW today_30m_usage AS
 SELECT counts.meter_id, counts.sample_count, counts.sample_time, round((counts.watt_hours::double precision / counts.hours)::numeric, 1) AS watts
   FROM ( SELECT sample_view.meter_id, min(sample_view.tstamp) + (max(sample_view.tstamp) - min(sample_view.tstamp)) AS sample_time, count(*) AS sample_count, 10 * (max(sample_view.consumption) - min(sample_view.consumption)) AS watt_hours, date_part('epoch'::text, max(sample_view.tstamp) - min(sample_view.tstamp)) / 3600::double precision AS hours, round(date_part('epoch'::text, sample_view.tstamp) / (60 * 30)::double precision) AS rounded_tstamp
           FROM sample_view
          WHERE sample_view.tstamp > (now() - '24:00:00'::interval)
          GROUP BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 30)::double precision), sample_view.meter_id
          ORDER BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 30)::double precision) DESC) counts
  WHERE counts.sample_count > 5 AND counts.watt_hours > 0;

CREATE VIEW month_24h_usage AS
 SELECT counts.meter_id, counts.sample_count, counts.sample_time, round((counts.watt_hours::double precision / counts.hours)::numeric, 1) AS watts
   FROM ( SELECT sample_view.meter_id, min(sample_view.tstamp) + (max(sample_view.tstamp) - min(sample_view.tstamp)) AS sample_time, count(*) AS sample_count, 10 * (max(sample_view.consumption) - min(sample_view.consumption)) AS watt_hours, date_part('epoch'::text, max(sample_view.tstamp) - min(sample_view.tstamp)) / 3600::double precision AS hours, round(date_part('epoch'::text, sample_view.tstamp) / (60 * 60 * 24)::double precision) AS rounded_tstamp
           FROM sample_view
          WHERE sample_view.tstamp > (now() - '30 days'::interval)
          GROUP BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 60 * 24)::double precision), sample_view.meter_id
          ORDER BY round(date_part('epoch'::text, sample_view.tstamp) / (60 * 60 * 24)::double precision) DESC) counts
  WHERE counts.sample_count > 5 AND counts.watt_hours > 0;


CREATE VIEW last_day_usage AS
SELECT round((max(sample_view.consumption) - min(sample_view.consumption))::numeric / 100.0, 1) AS daily_usage
   FROM sample_view
  WHERE sample_view.meter_id = 30 AND sample_view.tstamp > (now() - '24:00:00'::interval);
