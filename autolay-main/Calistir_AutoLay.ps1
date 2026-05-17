$ErrorActionPreference = "Stop"

$outerRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Join-Path $outerRoot "autolay-main"
$venvPython = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $projectRoot)) {
    Write-Host "HATA: Proje klasoru bulunamadi: $projectRoot" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

if (-not (Test-Path $venvPython)) {
    Write-Host "venv bulunamadi, olusturuluyor..." -ForegroundColor Yellow
    py -3 -m venv venv
}

Write-Host "Bagimliliklar kontrol ediliyor..." -ForegroundColor Cyan
& $venvPython -m pip install -q pywin32

Write-Host "AutoLay baslatiliyor..." -ForegroundColor Green
& $venvPython -m autolay
exit $LASTEXITCODE
