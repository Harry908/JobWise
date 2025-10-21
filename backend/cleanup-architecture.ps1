# Architecture Cleanup Script for Windows PowerShell
# This script removes over-engineered and empty files while preserving adapter pattern

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend Architecture Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] No files will be deleted" -ForegroundColor Yellow
    Write-Host ""
}

if (-not $Force) {
    Write-Host "This script will remove the following:" -ForegroundColor Yellow
    Write-Host "  - Empty adapter stub files (LLM, PDF, storage, cache, jobs)"
    Write-Host "  - Over-engineered infrastructure (AI, core factories)"
    Write-Host "  - Empty use_cases files"
    Write-Host "  - Duplicate infrastructure directory"
    Write-Host "  - Empty domain/repositories directory"
    Write-Host ""
    $confirm = Read-Host "Do you want to continue? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "Cleanup cancelled." -ForegroundColor Red
        exit 0
    }
}

# Change to backend directory
$backendDir = $PSScriptRoot
if (-not (Test-Path "$backendDir/app")) {
    Write-Host "Error: Must run from backend/ directory" -ForegroundColor Red
    exit 1
}

Set-Location $backendDir

# Counter for removed items
$removedCount = 0

# Function to remove file or directory
function Remove-ItemSafe {
    param(
        [string]$Path,
        [string]$Description
    )

    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "[DRY RUN] Would remove: $Path" -ForegroundColor Gray
            Write-Host "  Description: $Description" -ForegroundColor Gray
        } else {
            Write-Host "Removing: $Path" -ForegroundColor Green
            Write-Host "  Description: $Description" -ForegroundColor Gray
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            $script:removedCount++
        }
    } else {
        Write-Host "Already removed or not found: $Path" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Step 1: Removing empty LLM adapter stubs..." -ForegroundColor Cyan
Write-Host "-------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/adapters/llm/azure_openai_adapter.py" "Empty Azure OpenAI adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/llm/claude_adapter.py" "Empty Claude adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/llm/gemini_adapter.py" "Empty Gemini adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/llm/groq_adapter.py" "Empty Groq adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/llm/local_llm_adapter.py" "Empty local LLM adapter stub"

Write-Host ""
Write-Host "Step 2: Removing empty PDF adapter stubs..." -ForegroundColor Cyan
Write-Host "--------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/adapters/pdf/cloud_pdf_adapter.py" "Empty cloud PDF adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/pdf/weasyprint_adapter.py" "Empty WeasyPrint adapter stub"

Write-Host ""
Write-Host "Step 3: Removing empty storage adapter stubs..." -ForegroundColor Cyan
Write-Host "------------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/adapters/storage/azure_blob_adapter.py" "Empty Azure Blob adapter stub"
Remove-ItemSafe "app/infrastructure/adapters/storage/s3_adapter.py" "Empty S3 adapter stub"

Write-Host ""
Write-Host "Step 4: Removing empty cache adapter stubs..." -ForegroundColor Cyan
Write-Host "-----------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/adapters/cache/memory_adapter.py" "Empty memory cache adapter"
Remove-ItemSafe "app/infrastructure/adapters/cache/redis_adapter.py" "Minimal Redis adapter"

Write-Host ""
Write-Host "Step 5: Removing job adapter directory (not using adapter pattern)..." -ForegroundColor Cyan
Write-Host "---------------------------------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/adapters/jobs" "Job adapters directory (not using pattern)"

Write-Host ""
Write-Host "Step 6: Removing over-engineered AI infrastructure..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/ai/cost_optimizer.py" "Cost optimizer (premature)"
Remove-ItemSafe "app/infrastructure/ai/token_manager.py" "Token manager (premature)"
Remove-ItemSafe "app/infrastructure/ai/universal_llm_service.py" "Universal LLM service (over-engineered)"
Remove-ItemSafe "app/infrastructure/ai/prompt_manager.py" "Prompt manager (premature)"
Remove-ItemSafe "app/infrastructure/ai" "AI infrastructure directory"

Write-Host ""
Write-Host "Step 7: Removing service factory and circuit breakers..." -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/infrastructure/core/circuit_breaker.py" "Circuit breaker (premature)"
Remove-ItemSafe "app/infrastructure/core/fallback_manager.py" "Fallback manager (over-engineered)"
Remove-ItemSafe "app/infrastructure/core/health_checker.py" "Health checker (unnecessary)"
Remove-ItemSafe "app/infrastructure/core/service_factory.py" "Service factory (over-engineered)"
Remove-ItemSafe "app/infrastructure/core" "Core infrastructure directory"

Write-Host ""
Write-Host "Step 8: Removing empty external services directory..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------" -ForegroundColor Cyan

if (Test-Path "app/infrastructure/external_services") {
    $isEmpty = (Get-ChildItem "app/infrastructure/external_services" -Recurse -File | Measure-Object).Count -eq 0
    if ($isEmpty) {
        Remove-ItemSafe "app/infrastructure/external_services" "Empty external services directory"
    } else {
        Write-Host "External services directory not empty, keeping it" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Step 9: Removing empty use_cases files..." -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "app/application/use_cases/document_use_cases.py" "Empty document use cases"
Remove-ItemSafe "app/application/use_cases/generation_use_cases.py" "Empty generation use cases"
Remove-ItemSafe "app/application/use_cases/job_use_cases.py" "Empty job use cases"

# Check if profile_use_cases.py has content
if (Test-Path "app/application/use_cases/profile_use_cases.py") {
    $lineCount = (Get-Content "app/application/use_cases/profile_use_cases.py" | Measure-Object -Line).Lines
    Write-Host "profile_use_cases.py has $lineCount lines - keeping for manual review" -ForegroundColor Yellow
}

# Remove use_cases directory if empty
if (Test-Path "app/application/use_cases") {
    $isEmpty = (Get-ChildItem "app/application/use_cases" -Recurse -File | Measure-Object).Count -eq 0
    if ($isEmpty) {
        Remove-ItemSafe "app/application/use_cases" "Empty use_cases directory"
    }
}

Write-Host ""
Write-Host "Step 10: Removing duplicate root infrastructure directory..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

Remove-ItemSafe "infrastructure" "Duplicate infrastructure directory"

Write-Host ""
Write-Host "Step 11: Removing empty domain/repositories directory..." -ForegroundColor Cyan
Write-Host "---------------------------------------------------------" -ForegroundColor Cyan

if (Test-Path "app/domain/repositories") {
    $isEmpty = (Get-ChildItem "app/domain/repositories" -Recurse -File | Measure-Object).Count -eq 0
    if ($isEmpty) {
        Remove-ItemSafe "app/domain/repositories" "Empty domain repositories directory"
    } else {
        Write-Host "Domain repositories directory not empty, keeping it" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host ""
    Write-Host "[DRY RUN] No files were actually deleted" -ForegroundColor Yellow
    Write-Host "Run without -DryRun flag to perform actual cleanup" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Removed $removedCount items" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review changes: git status" -ForegroundColor White
    Write-Host "2. Run tests: pytest tests/" -ForegroundColor White
    Write-Host "3. Update imports if needed" -ForegroundColor White
    Write-Host "4. Commit changes: git commit -m 'Simplify architecture'" -ForegroundColor White
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
