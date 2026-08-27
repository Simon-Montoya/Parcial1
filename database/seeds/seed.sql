-- Add development and test seed data here.
insert into response_units (
    name,
    unit_type,
    city,
    latitude,
    longitude
)
values
(
    'Ambulancia Cali 01',
    'AMBULANCE',
    'CALI',
    3.4516,
    -76.5320
),
(
    'Bomberos Pereira 01',
    'FIRE_DEPARTMENT',
    'PEREIRA',
    4.8133,
    -75.6961
),
(
    'Cruz Roja Manizales 01',
    'RED_CROSS',
    'MANIZALES',
    5.0703,
    -75.5138
);