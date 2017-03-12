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


