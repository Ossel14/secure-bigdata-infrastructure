-- Database initialization script
CREATE DATABASE bigdata;
CREATE USER bigdata_user WITH ENCRYPTED PASSWORD 'here ur password';
GRANT ALL PRIVILEGES ON DATABASE bigdata TO bigdata_user;

\c bigdata

CREATE TABLE sensor_data (
    id          SERIAL PRIMARY KEY,
    sensor_id   VARCHAR(50) NOT NULL,
    value       DECIMAL(10, 2) NOT NULL,
    timestamp   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bigdata_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bigdata_user;
