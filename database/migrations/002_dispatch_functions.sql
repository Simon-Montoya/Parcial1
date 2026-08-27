create or replace function find_nearest_available_unit(
    p_emergency_id uuid
)
returns table (
    unit_id uuid,
    unit_name text,
    unit_type response_unit_type,
    city emergency_city,
    distance_meters double precision
)
language sql
stable
as $$
    select
        ru.id,
        ru.name,
        ru.unit_type,
        ru.city,
        st_distance(
            ru.location,
            e.location
        ) as distance_meters

    from response_units ru
    join emergencies e
        on e.id = p_emergency_id

    where
        ru.status = 'AVAILABLE'
        and ru.city = e.city

    order by
        ru.location <-> e.location

    limit 1;
$$;