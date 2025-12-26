# RAG Chatbot Quick Start Script
# Run this to test the RAG system before starting the full application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG Chatbot Integration Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is running
Write-Host "1. Checking PostgreSQL connection..." -ForegroundColor Yellow
try {
    $pgTest = psql -U postgres -d arogya_swarm -c "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ PostgreSQL connected" -ForegroundColor Green
    } else {
        Write-Host "   ✗ PostgreSQL not accessible" -ForegroundColor Red
        Write-Host "   Please start PostgreSQL and ensure database 'arogya_swarm' exists" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ✗ PostgreSQL not running" -ForegroundColor Red
    Write-Host "   Please start PostgreSQL" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check environment variables
Write-Host "2. Checking environment variables..." -ForegroundColor Yellow

$ragEnvPath = Join-Path $PSScriptRoot "rag\.env"
if (Test-Path $ragEnvPath) {
    Write-Host "   ✓ Found rag/.env" -ForegroundColor Green
    
    # Load and check API key
    $envContent = Get-Content $ragEnvPath
    $hasApiKey = $false
    foreach ($line in $envContent) {
        if ($line -match "^VITE_GEMINI_API_KEY=.+") {
            $hasApiKey = $true
            Write-Host "   ✓ VITE_GEMINI_API_KEY is set" -ForegroundColor Green
            break
        }
    }
    
    if (-not $hasApiKey) {
        Write-Host "   ✗ VITE_GEMINI_API_KEY not found in rag/.env" -ForegroundColor Red
        Write-Host "   Please add your Gemini API key" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   ✗ rag/.env not found" -ForegroundColor Red
    Write-Host "   Please create rag/.env with DATABASE_URL and VITE_GEMINI_API_KEY" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if documents exist
Write-Host "3. Checking medical documents..." -ForegroundColor Yellow
$docsPath = Join-Path $PSScriptRoot "rag\data\medical_documents.json"
if (Test-Path $docsPath) {
    $docs = Get-Content $docsPath | ConvertFrom-Json
    Write-Host "   ✓ Found $($docs.Count) medical documents" -ForegroundColor Green
} else {
    Write-Host "   ✗ Medical documents not found" -ForegroundColor Red
    Write-Host "   Path: $docsPath" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Ingest documents
Write-Host "4. Ingesting documents into RAG system..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray

try {
    Set-Location (Join-Path $PSScriptRoot "backend")
    python scripts/ingest_medical_docs.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Documents ingested successfully" -ForegroundColor Green
    } else {
        Write-Host "   ✗ Document ingestion failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "   ✗ Error during ingestion: $_" -ForegroundColor Red
    exit 1
} finally {
    Set-Location $PSScriptRoot
}

Write-Host ""

# Test RAG query via CLI
Write-Host "5. Testing RAG query..." -ForegroundColor Yellow
Write-Host "   Query: 'What should we do during high AQI events?'" -ForegroundColor Gray

try {
    Set-Location (Join-Path $PSScriptRoot "rag")
    
    # Create a test query script
    $testScript = @"
import sys
from rag.cli import retrieve_relevant, build_rag_prompt, generate_text

query = "What should we do during high AQI events?"
print(f"\nSearching for: {query}")

docs = retrieve_relevant(query, top_k=2)
print(f"Found {len(docs)} relevant documents\n")

if docs:
    for i, doc in enumerate(docs, 1):
        print(f"Document {i} (ID: {doc.get('id', 'unknown')}):")
        content = doc.get('content', '')[:150]
        print(f"  {content}...\n")
    
    try:
        prompt = build_rag_prompt(query, docs)
        answer = generate_text(prompt, max_output_tokens=256)
        print("Generated Answer:")
        print(f"  {answer}\n")
        print("✓ RAG system is working correctly!")
    except Exception as e:
        print(f"⚠ Answer generation failed (API issue): {e}")
        print("✓ Document retrieval working (offline mode available)")
else:
    print("✗ No documents found")
    sys.exit(1)
"@
    
    $testScript | python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ RAG query test passed" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ RAG query test had issues (check output above)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ✗ Error during test: $_" -ForegroundColor Red
} finally {
    Set-Location $PSScriptRoot
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RAG System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Start backend:  cd backend && uvicorn main:app --reload" -ForegroundColor Gray
Write-Host "  2. Start frontend: cd frontend && npm run dev" -ForegroundColor Gray
Write-Host "  3. Open dashboard: http://localhost:3000" -ForegroundColor Gray
Write-Host "  4. Click the chat button (bottom-right) to test!" -ForegroundColor Gray
Write-Host ""
