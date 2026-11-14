-- TASK A disposable seed. Synthetic rows only.
create schema sales;
create table sales."order" (order_id text primary key, customer_id text not null, status text not null);
insert into sales."order"
  select 'O-' || lpad(g::text, 3, '0'), case when g in (3, 7) then 'C-SECRET' else 'C-' || lpad((g % 9)::text, 3, '0') end, 'OPEN'
  from generate_series(1, 25) g;
insert into sales."order"
  select 'O-' || lpad(g::text, 3, '0'), 'C-' || lpad((g % 9)::text, 3, '0'), 'CLOSED' from generate_series(101, 105) g;
insert into sales."order"
  select 'O-' || lpad(g::text, 3, '0'), 'C-SECRET', 'HOLD' from generate_series(201, 203) g;
-- a second reader that row-level security restricts
create role t3a_limited login password 't3a_limited_pw';
grant usage on schema sales to t3a_limited;
grant select on sales."order" to t3a_limited;
alter table sales."order" enable row level security;
create policy hide_secret on sales."order" for select to t3a_limited using (customer_id <> 'C-SECRET');
