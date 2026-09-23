-- Run as an appropriately privileged Snowflake user.
create warehouse if not exists ANALYTICS_WH
  warehouse_size = 'XSMALL'
  auto_suspend = 60
  auto_resume = true;

create database if not exists ANALYTICS_DB;

create schema if not exists ANALYTICS_DB.RAW;
create schema if not exists ANALYTICS_DB.STAGING;
create schema if not exists ANALYTICS_DB.QUALITY;
create schema if not exists ANALYTICS_DB.ANALYTICS;

create table if not exists ANALYTICS_DB.RAW.TRIPS (
    trip_id varchar,
    vehicle_id varchar,
    started_at timestamp_ntz,
    completed_at timestamp_ntz,
    pickup_zone varchar,
    dropoff_zone varchar,
    distance_miles number(10,2),
    duration_seconds integer,
    delivery_status varchar,
    fare_amount number(12,2),
    source_file varchar,
    loaded_at timestamp_ntz default current_timestamp()
);
