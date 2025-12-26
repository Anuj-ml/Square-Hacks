# Start All Services Script
# Starts Backend and Frontend in separate terminals

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Arogya-Swarm Service Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseDir = $PSScriptRoot

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check PostgreSQL
Write-Host "1. PostgreSQL..." -ForegroundColor Gray
try {
    $pgTest = psql -U postgres -d arogya_swarm -c "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ PostgreSQL running" -ForegroundColor Green
    } else {
        Write-Host "   ✗ PostgreSQL not accessible" -ForegroundColor Red
        Write-Host "   Please start PostgreSQL and create 'arogya_swarm' database" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ✗ PostgreSQL not running" -ForegroundColor Red
    exit 1
}

# Check if documents need to be ingested
$docCount = psql -U postgres -d arogya_swarm -t -c "SELECT COUNT(*) FROM documents;" 2>$null
if ($docCount) {
    $docCount = $docCount.Trim()
    if ([int]$docCount -eq 0) {
        Write-Host ""
        Write-Host "⚠ No documents found in RAG system!" -ForegroundColor Yellow
        Write-Host "Would you like to ingest medical documents now? (Y/N)" -ForegroundColor Yellow
        $response = Read-Host
        if ($response -eq "Y" -or $response -eq "y") {
            Write-Host ""
            Write-Host "Ingesting documents..." -ForegroundColor Cyan
            Set-Location (Join-Path $baseDir "backend")
            python scripts/ingest_medical_docs.py
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Documents ingested successfully!" -ForegroundColor Green
            } else {
                Write-Host "✗ Document ingestion failed" -ForegroundColor Red
            }
            Set-Location $baseDir
        }
    } else {
        Write-Host "   ✓ RAG has $docCount documents" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "2. Python dependencies..." -ForegroundColor Gray
Set-Location (Join-Path $baseDir "backend")
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "   ✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠ No virtual environment found" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
    Write-Host "   ✓ Virtual environment created" -ForegroundColor Green
}
Set-Location $baseDir

Write-Host ""
Write-Host "3. Node modules..." -ForegroundColor Gray
Set-Location (Join-Path $baseDir "frontend")
if (Test-Path "node_modules") {
    Write-Host "   ✓ Node modules installed" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Node modules not found" -ForegroundColor Yellow
    Write-Host "   Installing dependencies..." -ForegroundColor Gray
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
    }
}
Set-Location $baseDir

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Services..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend in new terminal
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
$backendPath = Join-Path $baseDir "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host 'Backend Server' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
    cd '$backendPath'
    if (Test-Path 'venv\Scripts\Activate.ps1') {
        .\venv\Scripts\Activate.ps1
    }
    Write-Host 'Starting FastAPI server...' -ForegroundColor Yellow
    Write-Host ''
    uvicorn main:app --reload --port 8000
"@

Start-Sleep -Seconds 2

# Start Frontend in new terminal
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
$frontendPath = Join-Path $baseDir "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host 'Frontend Server' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
    cd '$frontendPath'
    Write-Host 'Starting Vite dev server...' -ForegroundColor Yellow
    Write-Host ''
    npm run dev
"@

Write-Host ""
Write-Host "✓ Services starting..." -ForegroundColor Green
Write-Host ""
Write-Host "Waiting for servers to initialize (10 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "System Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is up
try {
    $backendTest = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Backend running:  http://localhost:8000" -ForegroundColor Green
    Write-Host "  API Docs:         http://localhost:8000/docs" -ForegroundColor Gray
} catch {
    Write-Host "⚠ Backend still starting... (check backend terminal)" -ForegroundColor Yellow
}

# Check if frontend is up
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Frontend running: http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "⚠ Frontend still starting... (check frontend terminal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Quick Start Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Open Dashboard:" -ForegroundColor Yellow
Write-Host "   → http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test RAG Chatbot:" -ForegroundColor Yellow
Write-Host "   • Look for purple/blue chat button (bottom-right)" -ForegroundColor Gray
Write-Host "   • Click to open chat overlay" -ForegroundColor Gray
Write-Host "   • Try: 'What should we do during high AQI events?'" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Explore Features:" -ForegroundColor Yellow
Write-Host "   • Overview tab: Real-time metrics" -ForegroundColor Gray
Write-Host "   • Resources tab: Bed/staff/inventory status" -ForegroundColor Gray
Write-Host "   • Decisions tab: AI recommendations" -ForegroundColor Gray
Write-Host "   • Advisory tab: Patient notifications" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test Crisis Scenarios:" -ForegroundColor Yellow
Write-Host "   • Click scenario buttons: Normal/Pollution/Festival/Outbreak" -ForegroundColor Gray
Write-Host "   • Watch agents activate in real-time" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Red
Write-Host "  • Close both PowerShell terminal windows" -ForegroundColor Gray
Write-Host "  • Or press Ctrl+C in each terminal" -ForegroundColor Gray
Write-Host ""
Write-Host "For troubleshooting, run:" -ForegroundColor Yellow
Write-Host "  .\check-system.ps1" -ForegroundColor Cyan
Write-Host ""
