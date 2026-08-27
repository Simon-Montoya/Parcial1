create extension if not exists postgis;

create type emergency_type as enum (
    'RESCUE',
    'SHELTER',
    'SUPPLY',
    'STRUCTURAL_DAMAGE'
);

create type emergency_priority as enum (
    'P1',
    'P2',
    'P3',
    'P4'
);

create type emergency_status as enum (
    'RECEIVED',
    'VALIDATED',
    'ASSIGNED',
    'IN_PROGRESS',
    'RESOLVED',
    'CANCELLED'
);

create type emergency_city as enum (
    'CHOCO',
    'PEREIRA',
    'CALI',
    'MANIZALES'
);

create type supply_category as enum (
    'WATER',
    'FOOD',
    'FIRST_AID',
    'CHRONIC_MEDICATION'
);

create type response_unit_type as enum (
    'AMBULANCE',
    'FIRE_DEPARTMENT',
    'RED_CROSS',
    'CIVIL_DEFENSE',
    'UNGRD',
    'RESCUE_TEAM'
);

create type unit_status as enum (
    'AVAILABLE',
    'ASSIGNED',
    'BUSY',
    'OFFLINE'
);

create table emergencies (
    id uuid primary key default gen_random_uuid(),

    type emergency_type not null,

    priority emergency_priority not null,

    status emergency_status
        not null
        default 'RECEIVED',

    city emergency_city not null,

    description text,

    latitude double precision not null,
    longitude double precision not null,

    location geography(point, 4326),

    created_by uuid references auth.users(id),

    created_at timestamptz
        not null
        default now(),

    updated_at timestamptz
        not null
        default now()
);

create table rescue_details (
    emergency_id uuid primary key
        references emergencies(id)
        on delete cascade,

    trapped_people integer
        not null
        default 0
        check (trapped_people >= 0),

    injured_people integer
        not null
        default 0
        check (injured_people >= 0),

    gas_leak boolean
        not null
        default false,

    fire boolean
        not null
        default false,

    imminent_collapse_risk boolean
        not null
        default false
);

create table shelter_details (
    emergency_id uuid primary key
        references emergencies(id)
        on delete cascade,

    adults integer
        not null
        default 0
        check (adults >= 0),

    children integer
        not null
        default 0
        check (children >= 0),

    elderly integer
        not null
        default 0
        check (elderly >= 0),

    accessibility_required boolean
        not null
        default false,

    house_habitable boolean
);

create table supply_details (
    emergency_id uuid primary key
        references emergencies(id)
        on delete cascade,

    supply_category supply_category not null,

    quantity integer
        check (quantity >= 0),

    notes text
);

create table structural_damage_details (
    emergency_id uuid primary key
        references emergencies(id)
        on delete cascade,

    building_type text not null,

    cracking_level text,

    settlement_level text,

    collapse_risk boolean
        not null
        default false,

    road_risk boolean
        not null
        default false,

    photo_url text
);

create or replace function set_emergency_location()
returns trigger
language plpgsql
as $$
begin

    new.location :=
        st_setsrid(
            st_makepoint(
                new.longitude,
                new.latitude
            ),
            4326
        )::geography;

    return new;

end;
$$;

create trigger trg_set_emergency_location
before insert or update of latitude, longitude
on emergencies
for each row
execute function set_emergency_location();

create index idx_emergencies_location
on emergencies
using gist(location);

create type response_unit_type as enum (
    'AMBULANCE',
    'FIRE_DEPARTMENT',
    'RED_CROSS',
    'CIVIL_DEFENSE',
    'UNGRD',
    'RESCUE_TEAM'
);

create type unit_status as enum (
    'AVAILABLE',
    'ASSIGNED',
    'BUSY',
    'OFFLINE'
);

create table response_units (
    id uuid primary key default gen_random_uuid(),

    name text not null,

    unit_type response_unit_type not null,

    status unit_status not null default 'AVAILABLE',

    city emergency_city not null,

    latitude double precision not null,
    longitude double precision not null,

    location geography(point, 4326),

    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create or replace function set_response_unit_location()
returns trigger
language plpgsql
as $$
begin
    new.location :=
        st_setsrid(
            st_makepoint(
                new.longitude,
                new.latitude
            ),
            4326
        )::geography;

    return new;
end;
$$;

create trigger trg_set_response_unit_location
before insert or update of latitude, longitude
on response_units
for each row
execute function set_response_unit_location();

create table dispatches (
    id uuid primary key default gen_random_uuid(),

    emergency_id uuid not null
        references emergencies(id),

    response_unit_id uuid not null
        references response_units(id),

    assigned_at timestamptz not null default now(),

    accepted_at timestamptz,
    completed_at timestamptz,

    notes text
);

create table emergency_status_history (
    id uuid primary key default gen_random_uuid(),

    emergency_id uuid not null
        references emergencies(id)
        on delete cascade,

    previous_status emergency_status,

    new_status emergency_status not null,

    changed_by uuid references auth.users(id),

    changed_at timestamptz not null default now()
);

create type notification_status as enum (
    'PENDING',
    'SENT',
    'FAILED'
);

create table notifications (
    id uuid primary key default gen_random_uuid(),

    emergency_id uuid not null
        references emergencies(id)
        on delete cascade,

    recipient_id uuid references auth.users(id),

    message text not null,

    status notification_status
        not null
        default 'PENDING',

    created_at timestamptz
        not null
        default now(),

    sent_at timestamptz
);