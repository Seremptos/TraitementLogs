\connect logsdb

CREATE TABLE IF NOT EXISTS public.logs (
    row_id bigserial PRIMARY KEY,
    row_hash varchar(255) NOT NULL,
    row JSONB NOT NULL,
    inserted_at timestamp DEFAULT current_timestamp,
    CONSTRAINT row_unique UNIQUE (row_hash, row)
);

GRANT CONNECT ON DATABASE logsdb TO api;
GRANT USAGE ON SCHEMA public TO api;
GRANT ALL PRIVILEGES ON TABLE public.logs TO api;
GRANT USAGE, SELECT ON SEQUENCE public.logs_row_id_seq TO api;
