-- Seed two tenants, staff in each, and a self-registered super_admin.
-- Adjust the IDs in tests.sh if you change them here.
INSERT INTO public.clinics (id, name) VALUES
  ('11111111-1111-1111-1111-111111111111','Tenant A'),
  ('22222222-2222-2222-2222-222222222222','Tenant B');

INSERT INTO auth.users (id, email, raw_user_meta_data, email_confirmed_at) VALUES
  ('aaaaaaaa-0000-0000-0000-000000000001','staff.a@a.test','{"full_name":"Staff A","role":"doctor"}', now()),
  ('bbbbbbbb-0000-0000-0000-000000000002','staff.b@b.test','{"full_name":"Staff B","role":"doctor"}', now()),
  ('cccccccc-0000-0000-0000-000000000003','admin.a@a.test','{"full_name":"Admin A","role":"clinic_admin"}', now()),
  ('dddddddd-0000-0000-0000-000000000004','attacker@evil.test','{"full_name":"Attacker","role":"super_admin"}', now());

INSERT INTO public.clinic_staff (clinic_id, user_id, role) VALUES
  ('11111111-1111-1111-1111-111111111111','aaaaaaaa-0000-0000-0000-000000000001','doctor'),
  ('22222222-2222-2222-2222-222222222222','bbbbbbbb-0000-0000-0000-000000000002','doctor'),
  ('11111111-1111-1111-1111-111111111111','cccccccc-0000-0000-0000-000000000003','clinic_admin');

-- Same-name patients in both tenants (name-based linkage test).
INSERT INTO public.patients (clinic_id, first_name, last_name, date_of_birth, phone) VALUES
  ('11111111-1111-1111-1111-111111111111','Rajesh','Kumar','1980-01-01','+919999000001'),
  ('22222222-2222-2222-2222-222222222222','Rajesh','Kumar','1990-02-02','+919999000002'),
  ('22222222-2222-2222-2222-222222222222','Secret','PatientOfB','1975-03-03','+919999000003');

-- App-style appointments: no tenant column set (that is the bug under test).
INSERT INTO public.appointments
  (patient_name, appointment_date, start_time, end_time, doctor_name, type, title, status)
VALUES
  ('Rajesh Kumar', CURRENT_DATE, '09:00','09:30','Staff A','consultation','Appointment - Rajesh Kumar','scheduled');

SELECT 'seeded clinics=' || (SELECT count(*) FROM public.clinics)
    || ' profiles=' || (SELECT count(*) FROM public.profiles)
    || ' patients=' || (SELECT count(*) FROM public.patients)
    || ' appointments(clinic_id)=' || COALESCE((SELECT DISTINCT clinic_id::text FROM public.appointments LIMIT 1),'NULL');
