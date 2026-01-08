CREATE USER api WITH PASSWORD 'apisecretpassword';


CREATE DATABASE logsdb OWNER api;
GRANT ALL PRIVILEGES ON DATABASE logsdb TO api;

CREATE TABLE IF NOT EXISTS logs (
    row_id bigserial not null,
    row_hash varchar(255) not null,
    row JSONB not null,
    inserted_at timestamp DEFAULT current_timestamp,
    PRIMARY KEY (row_id),
    CONSTRAINT row_unique UNIQUE(row_hash, row)
)