# Comprehensive System Check Script
# Tests: Frontend, Backend, Database, and RAG integration

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Arogya-Swarm System Integration Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = $PSScriptRoot
$allPassed = $true

# Test 1: PostgreSQL Database
Write-Host "TEST 1: PostgreSQL Database" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
try {
    $dbTest = psql -U postgres -d arogya_swarm -c "SELECT COUNT(*) FROM documents;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database 'arogya_swarm' accessible" -ForegroundColor Green
        
        # Check if documents table exists and has data
        $docCount = psql -U postgres -d arogya_swarm -t -c "SELECT COUNT(*) FROM documents;" 2>$null
        if ($docCount) {
            $docCount = $docCount.Trim()
            Write-Host "  ✓ Documents table exists with $docCount documents" -ForegroundColor Green
            if ([int]$docCount -eq 0) {
                Write-Host "  ⚠ No documents found - need to ingest!" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  ✗ Database connection failed" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    Write-Host "  ✗ PostgreSQL not running or accessible" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Test 2: Redis
Write-Host "TEST 2: Redis Cache" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host "  ✓ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Redis not responding (optional for RAG)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Redis not installed or running (optional)" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Backend Environment
Write-Host "TEST 3: Backend Configuration" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$backendEnv = Join-Path $baseDir "backend\.env"
if (Test-Path $backendEnv) {
    Write-Host "  ✓ backend/.env exists" -ForegroundColor Green
    
    $envContent = Get-Content $backendEnv
    $hasGoogleKey = $envContent | Where-Object { $_ -match "^GOOGLE_API_KEY=" }
    $hasViteKey = $envContent | Where-Object { $_ -match "^VITE_GEMINI_API_KEY=" }
    
    if ($hasGoogleKey) {
        Write-Host "  ✓ GOOGLE_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ GOOGLE_API_KEY not found" -ForegroundColor Yellow
    }
    
    if ($hasViteKey) {
        Write-Host "  ✓ VITE_GEMINI_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ VITE_GEMINI_API_KEY not found (needed for RAG)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ backend/.env not found" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Test 4: RAG Environment
Write-Host "TEST 4: RAG Configuration" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$ragEnv = Join-Path $baseDir "rag\.env"
if (Test-Path $ragEnv) {
    Write-Host "  ✓ rag/.env exists" -ForegroundColor Green
    
    $envContent = Get-Content $ragEnv
    $hasDbUrl = $envContent | Where-Object { $_ -match "^DATABASE_URL=" }
    $hasApiKey = $envContent | Where-Object { $_ -match "^VITE_GEMINI_API_KEY=" }
    
    if ($hasDbUrl) {
        Write-Host "  ✓ DATABASE_URL configured" -ForegroundColor Green
    }
    if ($hasApiKey) {
        Write-Host "  ✓ VITE_GEMINI_API_KEY configured" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠ rag/.env not found - creating from example..." -ForegroundColor Yellow
    $ragEnvExample = Join-Path $baseDir "rag\.env.example"
    if (Test-Path $ragEnvExample) {
        Copy-Item $ragEnvExample $ragEnv
        Write-Host "  ✓ Created rag/.env from example" -ForegroundColor Green
        Write-Host "  ⚠ Please edit rag/.env and add your API key!" -ForegroundColor Yellow
    }
}
Write-Host ""

# Test 5: Medical Documents
Write-Host "TEST 5: Medical Documents" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
$docsPath = Join-Path $baseDir "rag\data\medical_documents.json"
if (Test-Path $docsPath) {
    $docs = Get-Content $docsPath | ConvertFrom-Json
    Write-Host "  ✓ Found $($docs.Count) medical documents" -ForegroundColor Green
    Write-Host "    Topics: Respiratory surge, Bed management, Staff fatigue..." -ForegroundColor Gray
} else {
    Write-Host "  ✗ Medical documents not found" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# Test 6: Backend Server
Write-Host "TEST 6: Backend Server" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  Testing if backend is running on port 8000..." -ForegroundColor Gray

try {
    $backendTest = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($backendTest.StatusCode -eq 200) {
        Write-Host "  ✓ Backend is running on port 8000" -ForegroundColor Green
        Write-Host "    Swagger docs: http://localhost:8000/docs" -ForegroundColor Gray
        
        # Test RAG status endpoint
        try {
            $ragStatus = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/rag/status" -Method Get -ErrorAction Stop
            Write-Host "  ✓ RAG system status: $($ragStatus.status)" -ForegroundColor Green
            Write-Host "    Initialized: $($ragStatus.initialized)" -ForegroundColor Gray
            Write-Host "    Document count: $($ragStatus.document_count)" -ForegroundColor Gray
            Write-Host "    Database connected: $($ragStatus.database_connected)" -ForegroundColor Gray
            
            if ($ragStatus.document_count -eq 0) {
                Write-Host "  ⚠ No documents in RAG system - run ingestion script!" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠ RAG status endpoint not responding" -ForegroundColor Yellow
            Write-Host "    Error: $_" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "  ✗ Backend not running on port 8000" -ForegroundColor Red
    Write-Host "    Please start: cd backend && uvicorn main:app --reload" -ForegroundColor Yellow
    $allPassed = $false
}
Write-Host ""

# Test 7: Frontend Server
Write-Host "TEST 7: Frontend Server" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host "  Testing if frontend is running on port 5173..." -ForegroundColor Gray

try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($frontendTest.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend is running on port 5173" -ForegroundColor Green
        Write-Host "    Dashboard: http://localhost:5173" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Frontend not running on port 5173" -ForegroundColor Red
    Write-Host "    Please start: cd frontend && npm run dev" -ForegroundColor Yellow
    $allPassed = $false
}
Write-Host ""

# Test 8: RAG Query Test
Write-Host "TEST 8: RAG Query Integration" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

if ((Test-Path $ragEnv) -and (Get-Content $ragEnv | Where-Object { $_ -match "^VITE_GEMINI_API_KEY=.+" })) {
    try {
        Write-Host "  Testing RAG query endpoint..." -ForegroundColor Gray
        
        $queryBody = @{
            question = "What should we do during high AQI events?"
            context = @{
                aqi = 250
                bed_capacity = 75
                active_alerts = 2
            }
        } | ConvertTo-Json
        
        $ragResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/rag/query" `
            -Method Post `
            -Body $queryBody `
            -ContentType "application/json" `
            -TimeoutSec 30 `
            -ErrorAction Stop
        
        Write-Host "  ✓ RAG query successful!" -ForegroundColor Green
        Write-Host "    Mode: $($ragResponse.mode)" -ForegroundColor Gray
        Write-Host "    Confidence: $($ragResponse.confidence)%" -ForegroundColor Gray
        Write-Host "    Sources: $($ragResponse.sources.Count) documents" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Answer preview:" -ForegroundColor Cyan
        $preview = $ragResponse.answer.Substring(0, [Math]::Min(200, $ragResponse.answer.Length))
        Write-Host "    $preview..." -ForegroundColor Gray
        
    } catch {
        Write-Host "  ✗ RAG query failed" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Red
        if ($_.Exception.Message -match "rate limit") {
            Write-Host "    (API rate limited - system should fall back to offline mode)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ⚠ Skipping RAG query test (API key not configured)" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($allPassed) {
    Write-Host "✓ All critical tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "System is ready to use:" -ForegroundColor Green
    Write-Host "  1. Frontend:  http://localhost:5173" -ForegroundColor Cyan
    Write-Host "  2. Backend:   http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  3. API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To test the chatbot:" -ForegroundColor Yellow
    Write-Host "  1. Open http://localhost:5173" -ForegroundColor Gray
    Write-Host "  2. Click the purple/blue chat button (bottom-right)" -ForegroundColor Gray
    Write-Host "  3. Ask: 'What should we do during high AQI events?'" -ForegroundColor Gray
} else {
    Write-Host "⚠ Some tests failed - please fix the issues above" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common fixes:" -ForegroundColor Yellow
    Write-Host "  • PostgreSQL not running: Start PostgreSQL service" -ForegroundColor Gray
    Write-Host "  • Backend not running: cd backend && uvicorn main:app --reload" -ForegroundColor Gray
    Write-Host "  • Frontend not running: cd frontend && npm run dev" -ForegroundColor Gray
    Write-Host "  • No documents: cd backend && python scripts/ingest_medical_docs.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "For detailed logs, check:" -ForegroundColor Cyan
Write-Host "  • Backend terminal output" -ForegroundColor Gray
Write-Host "  • Frontend terminal output" -ForegroundColor Gray
Write-Host "  • Browser console (F12)" -ForegroundColor Gray
Write-Host ""
