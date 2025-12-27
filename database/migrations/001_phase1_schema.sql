-- Add new tables for Phase 1 features (DO NOT MODIFY EXISTING TABLES)

-- Patients table for rural healthcare
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    phone VARCHAR(15) UNIQUE,
    village VARCHAR(100),
    district VARCHAR(100),
    state VARCHAR(50) DEFAULT 'Maharashtra',
    asha_worker_id INTEGER,
    language_preference VARCHAR(5) DEFAULT 'en' CHECK (language_preference IN ('en', 'hi', 'mr', 'ta', 'te', 'bn')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Medical records with image support
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    symptoms TEXT[],
    diagnosis TEXT,
    prescription TEXT,
    image_url TEXT,
    image_analysis JSONB,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    recorded_by VARCHAR(50),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Nutrition plans
CREATE TABLE IF NOT EXISTS nutrition_plans (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    age INTEGER,
    gender VARCHAR(10),
    weight_kg DECIMAL(5,2),
    height_cm INTEGER,
    bmi DECIMAL(4,2),
    region VARCHAR(50),
    dietary_restrictions TEXT[],
    health_conditions TEXT[],
    meal_plan JSONB,
    calories_target INTEGER,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    valid_until DATE
);

-- Telemedicine bookings
CREATE TABLE IF NOT EXISTS telemedicine_bookings (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_name VARCHAR(255),
    doctor_specialization VARCHAR(100),
    call_type VARCHAR(20) CHECK (call_type IN ('audio', 'video', 'chat')) DEFAULT 'audio',
    scheduled_time TIMESTAMP NOT NULL,
    duration_minutes INTEGER DEFAULT 15,
    status VARCHAR(20) CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled', 'no_show')) DEFAULT 'pending',
    payment_status VARCHAR(20) CHECK (payment_status IN ('unpaid', 'paid', 'refunded')) DEFAULT 'unpaid',
    amount INTEGER,
    meeting_link TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- SMS/WhatsApp logs
CREATE TABLE IF NOT EXISTS sms_logs (
    id SERIAL PRIMARY KEY,
    recipient_phone VARCHAR(15) NOT NULL,
    recipient_name VARCHAR(255),
    message TEXT NOT NULL,
    language VARCHAR(5) DEFAULT 'en',
    type VARCHAR(50) CHECK (type IN ('alert', 'reminder', 'appointment', 'prescription', 'bulk_alert', 'emergency')),
    channel VARCHAR(20) CHECK (channel IN ('sms', 'whatsapp')) DEFAULT 'sms',
    status VARCHAR(20) CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'sent_mock')) DEFAULT 'pending',
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    delivered_at TIMESTAMP
);

-- Translation cache (for performance)
CREATE TABLE IF NOT EXISTS translation_cache (
    id SERIAL PRIMARY KEY,
    source_text TEXT NOT NULL,
    source_lang VARCHAR(5) NOT NULL,
    target_lang VARCHAR(5) NOT NULL,
    translated_text TEXT NOT NULL,
    provider VARCHAR(50) DEFAULT 'mymemory',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(source_text, source_lang, target_lang)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_patients_village ON patients(village);
CREATE INDEX IF NOT EXISTS idx_patients_language ON patients(language_preference);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_telemedicine_bookings_patient ON telemedicine_bookings(patient_id);
CREATE INDEX IF NOT EXISTS idx_telemedicine_bookings_status ON telemedicine_bookings(status);
CREATE INDEX IF NOT EXISTS idx_sms_logs_phone ON sms_logs(recipient_phone);
CREATE INDEX IF NOT EXISTS idx_sms_logs_status ON sms_logs(status);
CREATE INDEX IF NOT EXISTS idx_translation_cache_lookup ON translation_cache(source_text, source_lang, target_lang);

-- Add triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_patients_updated_at
    BEFORE UPDATE ON patients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
