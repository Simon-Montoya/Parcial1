create or replace function get_zone_aggregation(
    p_city emergency_city,
    p_radius_meters double precision default 2000,
    p_min_points integer default 3
)
returns jsonb
language sql
stable
as $$
with active_emergencies as (
    select
        e.id,
        e.type,
        e.priority,
        e.status,
        e.city,
        e.description,
        e.latitude,
        e.longitude,
        e.location,
        e.created_at,

        st_clusterdbscan(
            st_transform(
                e.location::geometry,
                3857
            ),
            eps := p_radius_meters,
            minpoints := p_min_points
        ) over () as cluster_id

    from emergencies e

    where
        e.city = p_city
        and e.status not in (
            'RESOLVED',
            'CANCELLED'
        )
),

hotspots as (
    select
        cluster_id,

        count(*) as emergency_count,

        avg(latitude) as center_latitude,
        avg(longitude) as center_longitude,

        array_agg(id) as emergency_ids,

        min(priority::text) as highest_priority

    from active_emergencies

    where cluster_id is not null

    group by cluster_id
),

isolated as (
    select
        id,
        type,
        priority,
        status,
        description,
        latitude,
        longitude,
        created_at

    from active_emergencies

    where cluster_id is null
)

select jsonb_build_object(

    'city',
    p_city,

    'radius_meters',
    p_radius_meters,

    'min_points',
    p_min_points,

    'total_active_emergencies',
    (
        select count(*)
        from active_emergencies
    ),

    'hotspot_count',
    (
        select count(*)
        from hotspots
    ),

    'hotspots',
    coalesce(
        (
            select jsonb_agg(
                jsonb_build_object(
                    'cluster_id',
                    cluster_id,
                    'emergency_count',
                    emergency_count,
                    'center_latitude',
                    center_latitude,
                    'center_longitude',
                    center_longitude,
                    'highest_priority',
                    highest_priority,
                    'emergency_ids',
                    emergency_ids
                )
                order by emergency_count desc
            )
            from hotspots
        ),
        '[]'::jsonb
    ),

    'isolated_emergencies',
    coalesce(
        (
            select jsonb_agg(
                jsonb_build_object(
                    'id',
                    id,
                    'type',
                    type,
                    'priority',
                    priority,
                    'status',
                    status,
                    'description',
                    description,
                    'latitude',
                    latitude,
                    'longitude',
                    longitude,
                    'created_at',
                    created_at
                )
            )
            from isolated
        ),
        '[]'::jsonb
    )

);
$$;