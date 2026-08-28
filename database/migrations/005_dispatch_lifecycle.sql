-- Transactional dispatch lifecycle. The emergency owns the lifecycle status;
-- dispatches records operational timestamps and remains available for audit.
create or replace function update_dispatch_status(
    p_dispatch_id uuid,
    p_status emergency_status
)
returns table (
    dispatch_id uuid,
    emergency_id uuid,
    response_unit_id uuid,
    response_unit_name text,
    status emergency_status,
    completed_at timestamptz
)
language plpgsql
security invoker
set search_path = public
as $$
declare
    v_emergency_id uuid;
    v_response_unit_id uuid;
    v_response_unit_name text;
    v_current_status emergency_status;
    v_completed_at timestamptz;
begin
    if p_status not in ('IN_PROGRESS', 'RESOLVED') then
        raise exception 'INVALID_TARGET_STATUS';
    end if;

    select
        d.emergency_id,
        d.response_unit_id,
        e.status,
        d.completed_at
    into
        v_emergency_id,
        v_response_unit_id,
        v_current_status,
        v_completed_at
    from dispatches d
    join emergencies e on e.id = d.emergency_id
    where d.id = p_dispatch_id
    for update of d, e;

    if not found then
        raise exception 'DISPATCH_NOT_FOUND';
    end if;

    if v_current_status = 'RESOLVED' then
        raise exception 'ALREADY_RESOLVED';
    end if;

    if p_status = 'IN_PROGRESS' and v_current_status <> 'ASSIGNED' then
        raise exception 'INVALID_STATUS_TRANSITION';
    end if;

    if p_status = 'RESOLVED'
       and v_current_status not in ('ASSIGNED', 'IN_PROGRESS') then
        raise exception 'INVALID_STATUS_TRANSITION';
    end if;

    -- Lock exactly the unit associated with this dispatch.
    select name
    into v_response_unit_name
    from response_units
    where id = v_response_unit_id
    for update;

    if not found then
        raise exception 'RESPONSE_UNIT_NOT_FOUND';
    end if;

    if p_status = 'IN_PROGRESS' then
        update dispatches
        set accepted_at = coalesce(accepted_at, now())
        where id = p_dispatch_id;

        update response_units
        set status = 'BUSY', updated_at = now()
        where id = v_response_unit_id;
    else
        update dispatches
        set completed_at = coalesce(completed_at, now())
        where id = p_dispatch_id
        returning dispatches.completed_at into v_completed_at;

        update response_units
        set status = 'AVAILABLE', updated_at = now()
        where id = v_response_unit_id;
    end if;

    update emergencies
    set status = p_status, updated_at = now()
    where id = v_emergency_id;

    insert into emergency_status_history (
        emergency_id,
        previous_status,
        new_status
    ) values (
        v_emergency_id,
        v_current_status,
        p_status
    );

    return query
    select
        p_dispatch_id,
        v_emergency_id,
        v_response_unit_id,
        v_response_unit_name,
        p_status,
        v_completed_at;
end;
$$;

-- Lambdas use the server-side Supabase role. Browser roles cannot invoke this
-- state-changing function directly; operators use the Dispatch API.
revoke all on function update_dispatch_status(uuid, emergency_status)
from public, anon, authenticated;
grant execute on function update_dispatch_status(uuid, emergency_status)
to service_role;
