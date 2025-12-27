# Phase 1 Feature Test Script
# Run this after starting backend server to verify all features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 1 Feature Testing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8000/api/v1"
$passed = 0
$failed = 0

function Test-Endpoint {
    param (
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    
    try {
        if ($Method -eq "POST" -and $Body) {
            $jsonBody = $Body | ConvertTo-Json
            $response = Invoke-RestMethod -Uri $Url -Method $Method -Body $jsonBody -ContentType "application/json" -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri $Url -Method $Method -ErrorAction Stop
        }
        
        Write-Host " ✓ PASSED" -ForegroundColor Green
        $script:passed++
        return $response
    }
    catch {
        Write-Host " ✗ FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
        return $null
    }
}

Write-Host "1. Testing Translation Service" -ForegroundColor Yellow
Write-Host "-------------------------------" -ForegroundColor Yellow

# Test 1: Get supported languages
Test-Endpoint -Name "Get Supported Languages" -Url "$API_URL/languages"

# Test 2: Translate text to Hindi
$result = Test-Endpoint -Name "Translate to Hindi" `
    -Url "$API_URL/translate?text=Hello%20doctor&target_lang=hi" `
    -Method "POST"

if ($result) {
    Write-Host "  Original: $($result.original)" -ForegroundColor Gray
    Write-Host "  Translated: $($result.translated)" -ForegroundColor Gray
}

# Test 3: Translate to Marathi
$result = Test-Endpoint -Name "Translate to Marathi" `
    -Url "$API_URL/translate?text=Welcome%20to%20hospital&target_lang=mr" `
    -Method "POST"

if ($result) {
    Write-Host "  Translated: $($result.translated)" -ForegroundColor Gray
}

# Test 4: Language detection
$result = Test-Endpoint -Name "Detect Language" `
    -Url "$API_URL/translation/detect?text=नमस्ते" `
    -Method "POST"

if ($result) {
    Write-Host "  Detected: $($result.detected_language)" -ForegroundColor Gray
}

# Test 5: Translation stats
$result = Test-Endpoint -Name "Get Translation Stats" -Url "$API_URL/translation/stats"

if ($result) {
    Write-Host "  Memory cache: $($result.stats.memory_cache_size)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "2. Testing Messaging Service" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Yellow

# Test 6: Send SMS
$smsBody = @{
    phone = "+919876543210"
    message = "Test SMS from Phase 1"
    recipient_name = "Test User"
    language = "hi"
}

$result = Test-Endpoint -Name "Send SMS (Mock)" `
    -Url "$API_URL/messaging/sms" `
    -Method "POST" `
    -Body $smsBody

if ($result) {
    Write-Host "  Status: $($result.status)" -ForegroundColor Gray
    Write-Host "  Message ID: $($result.message_id)" -ForegroundColor Gray
}

# Test 7: Send WhatsApp
$waBody = @{
    phone = "+919876543211"
    message = "Test WhatsApp from Phase 1"
    language = "mr"
}

$result = Test-Endpoint -Name "Send WhatsApp (Mock)" `
    -Url "$API_URL/messaging/whatsapp" `
    -Method "POST" `
    -Body $waBody

if ($result) {
    Write-Host "  Status: $($result.status)" -ForegroundColor Gray
}

# Test 8: Get message logs
$result = Test-Endpoint -Name "Get Message Logs" -Url "$API_URL/messaging/logs?limit=5"

if ($result) {
    Write-Host "  Total logs: $($result.count)" -ForegroundColor Gray
}

# Test 9: Bulk translation
Write-Host ""
Write-Host "3. Testing Bulk Operations" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow

$bulkBody = @{
    texts = @("Hello", "Goodbye", "Thank you")
    target_lang = "hi"
}

$result = Test-Endpoint -Name "Bulk Translation" `
    -Url "$API_URL/translate/bulk" `
    -Method "POST" `
    -Body $bulkBody

if ($result) {
    Write-Host "  Translated count: $($result.count)" -ForegroundColor Gray
}

# Test 10: Bulk SMS alert
$bulkSmsBody = @{
    message = "Hospital surge alert"
    recipients = @(
        @{ phone = "+919876543210"; name = "Patient 1"; language = "hi" },
        @{ phone = "+919876543211"; name = "Patient 2"; language = "mr" }
    )
}

$result = Test-Endpoint -Name "Bulk SMS Alert" `
    -Url "$API_URL/messaging/bulk-alert" `
    -Method "POST" `
    -Body $bulkSmsBody

if ($result) {
    Write-Host "  Total: $($result.total), Sent: $($result.sent), Failed: $($result.failed)" -ForegroundColor Gray
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Test Results Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Total Tests: $($passed + $failed)" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "🎉 All tests passed! Phase 1 is working correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Open http://localhost:5173 to test frontend" -ForegroundColor White
    Write-Host "2. Switch languages using the language selector" -ForegroundColor White
    Write-Host "3. Test text-to-speech by clicking 'Play Instructions'" -ForegroundColor White
    Write-Host "4. Check database: psql -U postgres -d arogya_swarm" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Please check:" -ForegroundColor Yellow
    Write-Host "1. Is backend server running? (http://localhost:8000)" -ForegroundColor White
    Write-Host "2. Did you run database migrations?" -ForegroundColor White
    Write-Host "3. Are all dependencies installed?" -ForegroundColor White
}

Write-Host ""
