create table if not exists regions (
  id text primary key,
  name text not null,
  risk_score integer not null check (risk_score between 0 and 100),
  risk_level text not null check (risk_level in ('Low', 'Medium', 'High')),
  last_updated timestamptz not null default now()
);

create table if not exists disruptions (
  id text primary key,
  title text not null,
  description text not null,
  region text not null,
  severity text not null check (severity in ('Low', 'Medium', 'High')),
  source text not null,
  url text,
  created_at timestamptz not null default now()
);

create table if not exists documents (
  id text primary key,
  title text not null,
  content text not null,
  region text not null,
  source text not null,
  url text,
  published_at timestamptz not null,
  embedding_id text
);

create table if not exists trade_metrics (
  id text primary key,
  country text not null,
  partner_country text not null,
  trade_flow text not null,
  commodity text not null,
  period text not null,
  trade_value numeric not null,
  quantity numeric,
  created_at timestamptz not null default now()
);

create table if not exists historical_shipments (
  id text primary key,
  order_id text not null,
  region text not null,
  warehouse text not null,
  delivery_status text not null,
  delay_days integer not null,
  shipping_mode text not null,
  created_at timestamptz not null default now()
);
