# PowerShell script to build Ars Arcanum ISO via Docker container
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   BUILDING ARS ARCANUM ISO VIA DEBIAN 13 CONTAINER      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$projectRoot = Resolve-Path "$PSScriptRoot\..\.."

Write-Host "[*] Building Debian live-build compiler image..." -ForegroundColor Yellow
docker build -f "$PSScriptRoot\..\Dockerfile.build" -t ars-arcanum-builder "$projectRoot"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker image build failed. Ensure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

Write-Host "[*] Executing live-build in privileged container..." -ForegroundColor Yellow
docker run --rm --privileged -v "${projectRoot}:/build" ars-arcanum-builder

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] SUCCESS: Ars Arcanum ISO compiled successfully!" -ForegroundColor Green
} else {
    Write-Host "[!] Build failed inside container." -ForegroundColor Red
}
