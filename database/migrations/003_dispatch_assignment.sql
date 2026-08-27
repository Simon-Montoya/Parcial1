create or replace function assign_nearest_available_unit(
    p_emergency_id uuid
)
returns table (
    dispatch_id uuid,
    emergency_id uuid,
    response_unit_id uuid,
    response_unit_name text,
    distance_meters double precision
)
language plpgsql
as $$
declare
    v_emergency_status emergency_status;
    v_unit_id uuid;
    v_unit_name text;
    v_distance double precision;
    v_dispatch_id uuid;
begin

    -- 1. Bloquear emergencia mientras se procesa
    select status
    into v_emergency_status
    from emergencies
    where id = p_emergency_id
    for update;

    if not found then
        raise exception 'EMERGENCY_NOT_FOUND';
    end if;

    -- Evitar asignar dos veces la misma emergencia
    if v_emergency_status not in ('RECEIVED', 'VALIDATED') then
        raise exception 'EMERGENCY_NOT_ASSIGNABLE';
    end if;

    -- 2. Buscar la unidad AVAILABLE más cercana
    select
        ru.id,
        ru.name,
        st_distance(ru.location, e.location)
    into
        v_unit_id,
        v_unit_name,
        v_distance
    from response_units ru
    join emergencies e
        on e.id = p_emergency_id
    where
        ru.status = 'AVAILABLE'
        and ru.city = e.city
    order by
        ru.location <-> e.location
    for update of ru skip locked
    limit 1;

    if v_unit_id is null then
        raise exception 'NO_AVAILABLE_UNIT';
    end if;

    -- 3. Crear despacho
    insert into dispatches (
        emergency_id,
        response_unit_id,
        assigned_at
    )
    values (
        p_emergency_id,
        v_unit_id,
        now()
    )
    returning id into v_dispatch_id;

    -- 4. Marcar unidad como asignada
    update response_units
    set
        status = 'ASSIGNED',
        updated_at = now()
    where id = v_unit_id;

    -- 5. Actualizar emergencia
    update emergencies
    set
        status = 'ASSIGNED',
        updated_at = now()
    where id = p_emergency_id;

    return query
    select
        v_dispatch_id,
        p_emergency_id,
        v_unit_id,
        v_unit_name,
        v_distance;

end;
$$;