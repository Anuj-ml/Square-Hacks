# Phase 1 Implementation Checklist

## ✅ Installation Steps

- [ ] **Step 1: Install Backend Dependencies**
  ```powershell
  cd backend
  pip install -r requirements.txt
  ```
  Expected: `langdetect`, `cachetools` installed

- [ ] **Step 2: Install Frontend Dependencies**
  ```powershell
  cd frontend
  npm install
  ```
  Expected: `i18next`, `react-i18next` installed

- [ ] **Step 3: Setup Environment Files**
  - [ ] Copy `backend/.env.example` to `backend/.env`
  - [ ] Add your `GOOGLE_API_KEY` to backend `.env`
  - [ ] Add your `OPENWEATHERMAP_API_KEY` to backend `.env`
  - [ ] Copy `frontend/.env.example` to `frontend/.env`
  - [ ] Add your `VITE_GEMINI_API_KEY` to frontend `.env`

- [ ] **Step 4: Run Database Migrations**
  ```powershell
  psql -U postgres -d arogya_swarm -f database/migrations/001_phase1_schema.sql
  psql -U postgres -d arogya_swarm -f database/seed_phase1_data.sql
  ```
  Expected: 6 new tables created

- [ ] **Step 5: Verify Database**
  ```powershell
  psql -U postgres -d arogya_swarm -c "\dt"
  ```
  Expected tables: `patients`, `medical_records`, `nutrition_plans`, `telemedicine_bookings`, `sms_logs`, `translation_cache`

- [ ] **Step 6: Start Backend Server**
  ```powershell
  cd backend
  uvicorn main:app --reload
  ```
  Expected output:
  - ✓ Database tables created successfully
  - ✓ Logging configured at INFO level
  - ✓ Uvicorn running on http://127.0.0.1:8000

- [ ] **Step 7: Start Frontend Server (New Terminal)**
  ```powershell
  cd frontend
  npm run dev
  ```
  Expected: Frontend running on http://localhost:5173

---

## ✅ Feature Testing

### Multilingual Support

- [ ] **UI Language Switcher**
  - [ ] Open http://localhost:5173
  - [ ] Find language selector (globe icon) in navbar
  - [ ] Switch to Hindi (हिंदी)
  - [ ] Verify UI text changes
  - [ ] Switch to Marathi (मराठी)
  - [ ] Verify UI text changes

- [ ] **Translation API**
  ```powershell
  curl -X POST "http://localhost:8000/api/v1/translate?text=Hello%20doctor&target_lang=hi"
  ```
  Expected: `{"success": true, "translated": "नमस्ते डॉक्टर", ...}`

- [ ] **Language Detection**
  ```powershell
  curl -X POST "http://localhost:8000/api/v1/translation/detect?text=नमस्ते"
  ```
  Expected: `{"detected_language": "hi", ...}`

- [ ] **Supported Languages**
  ```powershell
  curl http://localhost:8000/api/v1/languages
  ```
  Expected: List of 6 languages

- [ ] **Cache Statistics**
  ```powershell
  curl http://localhost:8000/api/v1/translation/stats
  ```
  Expected: Cache statistics with memory and DB counts

### SMS/WhatsApp Service

- [ ] **Send SMS (Mock)**
  ```powershell
  curl -X POST "http://localhost:8000/api/v1/messaging/sms" -H "Content-Type: application/json" -d '{"phone": "+919876543210", "message": "Test message", "recipient_name": "Test User", "language": "hi"}'
  ```
  Expected: 
  - API response: `{"success": true, "status": "sent_mock", ...}`
  - Console output: `📱 SMS SENT`

- [ ] **Send WhatsApp (Mock)**
  ```powershell
  curl -X POST "http://localhost:8000/api/v1/messaging/whatsapp" -H "Content-Type: application/json" -d '{"phone": "+919876543211", "message": "Test WhatsApp", "language": "mr"}'
  ```
  Expected:
  - API response: `{"success": true, "status": "sent_mock", ...}`
  - Console output: `💬 WhatsApp SENT`

- [ ] **View Message Logs**
  ```powershell
  curl http://localhost:8000/api/v1/messaging/logs?limit=10
  ```
  Expected: List of sent messages

- [ ] **Database Verification**
  ```powershell
  psql -U postgres -d arogya_swarm -c "SELECT * FROM sms_logs ORDER BY sent_at DESC LIMIT 5;"
  ```
  Expected: Recent SMS entries

### Text-to-Speech

- [ ] **Browser TTS Support**
  - [ ] Open browser console (F12)
  - [ ] Type: `'speechSynthesis' in window`
  - [ ] Expected: `true`

- [ ] **Audio Instructions Component**
  - [ ] Look for "Play Instructions" button in UI
  - [ ] Click to play audio
  - [ ] Verify audio plays in selected language
  - [ ] Test Pause button
  - [ ] Test Resume button
  - [ ] Test Stop button

- [ ] **Multi-Language TTS**
  - [ ] Set UI language to Hindi
  - [ ] Play audio instructions
  - [ ] Verify Hindi speech
  - [ ] Switch to Marathi
  - [ ] Play audio instructions
  - [ ] Verify Marathi speech

### Database Tables

- [ ] **Patients Table**
  ```powershell
  psql -U postgres -d arogya_swarm -c "SELECT COUNT(*) FROM patients;"
  ```
  Expected: At least 5 patients (from seed data)

- [ ] **Medical Records**
  ```powershell
  psql -U postgres -d arogya_swarm -c "SELECT COUNT(*) FROM medical_records;"
  ```
  Expected: At least 2 records

- [ ] **Telemedicine Bookings**
  ```powershell
  psql -U postgres -d arogya_swarm -c "SELECT COUNT(*) FROM telemedicine_bookings;"
  ```
  Expected: At least 1 booking

- [ ] **Translation Cache**
  ```powershell
  psql -U postgres -d arogya_swarm -c "SELECT COUNT(*) FROM translation_cache;"
  ```
  Expected: Growing count after API usage

---

## ✅ Error Handling & Logging

- [ ] **Backend Logs**
  - [ ] Check file exists: `backend/logs/arogya_swarm.log`
  - [ ] Verify log entries are being written
  - [ ] Check for any ERROR level logs

- [ ] **Console Output**
  - [ ] Backend console shows no errors
  - [ ] Frontend console shows no errors
  - [ ] Network requests succeeding (check DevTools)

- [ ] **API Error Handling**
  ```powershell
  curl -X POST "http://localhost:8000/api/v1/translate?text=&target_lang=invalid"
  ```
  Expected: Proper error response with status code 422 or 500

---

## ✅ Performance Checks

- [ ] **Translation Speed**
  - [ ] First request (no cache): < 1 second
  - [ ] Cached request: < 10ms
  - [ ] Check cache stats shows increasing hit rate

- [ ] **SMS Service Speed**
  - [ ] Single SMS: < 100ms
  - [ ] Bulk alert (10 recipients): < 10 seconds

- [ ] **Page Load Time**
  - [ ] Frontend loads in < 2 seconds
  - [ ] Backend API responds in < 100ms for cached data

---

## ✅ Final Verification

- [ ] **API Documentation**
  - [ ] Visit http://localhost:8000/docs
  - [ ] Verify new endpoints visible:
    - `/api/v1/translate`
    - `/api/v1/messaging/sms`
    - `/api/v1/messaging/whatsapp`
    - `/api/v1/languages`

- [ ] **No Breaking Changes**
  - [ ] Existing dashboard loads properly
  - [ ] WebSocket connection works
  - [ ] Agent monitoring functional (if enabled)
  - [ ] RAG chatbot functional

- [ ] **All Features Work Together**
  - [ ] Change UI language
  - [ ] Send SMS in new language
  - [ ] Play TTS in new language
  - [ ] Verify all features work harmoniously

---

## 🎉 Success Criteria

✅ All backend dependencies installed
✅ All frontend dependencies installed
✅ Database migrations successful
✅ 6 new tables created
✅ Backend server running without errors
✅ Frontend server running without errors
✅ Language selector visible and functional
✅ Translation API working with caching
✅ SMS service logging to database
✅ Text-to-speech playing in all languages
✅ No errors in console or logs
✅ All API endpoints responding correctly

---

## 📝 Notes

- **Translation API**: Free tier, no API key required
- **SMS Service**: Mock mode only (no real messages)
- **TTS**: Uses browser Web Speech API (free)
- **Cache**: Automatically clears after 7 days
- **Logs**: Rotate daily (configure in production)

---

## 🆘 Common Issues

### "Translation returns original text"
→ Check internet connection, MyMemory API might be rate-limited. Check cache stats.

### "TTS not working"
→ Use Chrome/Edge/Safari. Firefox has limited support.

### "Database migration fails"
→ Ensure PostgreSQL is running and database exists.

### "Import errors in backend"
→ Run: `pip install --upgrade -r requirements.txt`

### "Frontend build errors"
→ Delete `node_modules`, run: `npm install`

---

**When all checkboxes are checked, Phase 1 is complete! 🎊**
