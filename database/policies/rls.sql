-- Define row-level security policies here.
alter table emergencies
enable row level security;

alter table rescue_details
enable row level security;

alter table shelter_details
enable row level security;

alter table supply_details
enable row level security;

alter table structural_damage_details
enable row level security;

alter table emergencies enable row level security;

create policy "citizens_can_read_own_emergencies"
on emergencies
for select
to authenticated
using (
    created_by = auth.uid()
);

create policy "citizens_can_create_emergencies"
on emergencies
for insert
to authenticated
with check (
    created_by = auth.uid()
);