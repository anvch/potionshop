create table
  public.transactions (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    gold integer null default 0,
    blue_ml integer null default 0,
    description text null,
    dark_ml integer null default 0,
    num_potions integer null default 0,
    red_ml integer null default 0,
    green_ml integer null default 0,
    barrel_color integer null default 0,
    constraint transactions_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.potions (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    item_sku text null,
    red integer null,
    green integer null,
    blue integer null,
    dark integer null,
    price integer null,
    quantity integer null,
    constraint potions_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.carts (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    constraint carts_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.cart_items (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    cart_id bigint null,
    potion_id bigint null,
    quantity integer null default 0,
    item_sku text null,
    price integer null default 0,
    constraint cart_items_pkey primary key (id),
    constraint public_cart_items_cart_id_fkey foreign key (cart_id) references carts (id),
    constraint public_cart_items_potion_id_fkey foreign key (potion_id) references potions (id)
  ) tablespace pg_default;