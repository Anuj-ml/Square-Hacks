-- Seed sample data for testing (only if tables are empty)

-- Sample patients
INSERT INTO patients (name, age, gender, phone, village, district, language_preference) VALUES
    ('Ramesh Kumar', 45, 'male', '+919876543210', 'Khalapur', 'Raigad', 'hi'),
    ('Sita Devi', 32, 'female', '+919876543211', 'Panvel', 'Raigad', 'mr'),
    ('Arjun Patil', 28, 'male', '+919876543212', 'Karjat', 'Raigad', 'mr'),
    ('Lakshmi Reddy', 55, 'female', '+919876543213', 'Alibag', 'Raigad', 'hi'),
    ('Mohammed Khan', 38, 'male', '+919876543214', 'Pen', 'Raigad', 'en')
ON CONFLICT (phone) DO NOTHING;

-- Sample medical records
INSERT INTO medical_records (patient_id, symptoms, diagnosis, severity, recorded_by) 
SELECT 1, ARRAY['fever', 'cough', 'body ache'], 'Common Cold', 'low', 'ASHA_Worker_01'
WHERE EXISTS (SELECT 1 FROM patients WHERE id = 1);

INSERT INTO medical_records (patient_id, symptoms, diagnosis, severity, recorded_by) 
SELECT 2, ARRAY['severe headache', 'vomiting', 'high fever'], 'Possible Dengue - Needs Lab Test', 'high', 'ASHA_Worker_02'
WHERE EXISTS (SELECT 1 FROM patients WHERE id = 2);

-- Sample telemedicine booking
INSERT INTO telemedicine_bookings (patient_id, doctor_name, doctor_specialization, call_type, scheduled_time, status, amount)
SELECT 1, 'Dr. Sharma', 'General Physician', 'audio', NOW() + INTERVAL '2 hours', 'pending', 200
WHERE EXISTS (SELECT 1 FROM patients WHERE id = 1);
