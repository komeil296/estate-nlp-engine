$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Project virtual environment not found: $Python"
}

Write-Host "`n--- Python Test Suite ---"
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    throw "Pytest failed. Do not commit or push."
}

Write-Host "`n--- Python Compilation ---"
& $Python -m compileall -q .\src .\tests .\scripts
if ($LASTEXITCODE -ne 0) {
    throw "Compilation failed. Do not commit or push."
}

Write-Host "`n--- Git Whitespace Check ---"
git diff --check
if ($LASTEXITCODE -ne 0) {
    throw "Git whitespace check failed. Do not commit or push."
}

Write-Host "`n--- Git Status ---"
git status --short --branch

Write-Host "`nVerification completed. No commit or push was performed."
