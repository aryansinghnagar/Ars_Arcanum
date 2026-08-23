# PowerShell Offline Reference Archive Fetcher
param (
    [ValidateSet("simple", "full", "skip")]
    [string]$Tier = "simple"
)

$destDir = Resolve-Path "$PSScriptRoot\..\config\includes.chroot\var\lib\kiwix"
if (!(Test-Path $destDir)) {
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    ARS ARCANUM OFFLINE ARCHIVE DOWNLOADER & BUNDLER     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if ($Tier -eq "simple") {
    Write-Host "[*] Fetching Simple English Wikipedia ZIM (~900 MB)..." -ForegroundColor Yellow
    $url = "https://download.kiwix.org/zim/wikipedia/wikipedia_en_simple_all_maxi_2024-01.zim"
    $outPath = Join-Path $destDir "wikipedia_simple.zim"
    Invoke-WebRequest -Uri $url -OutFile $outPath
    Write-Host "[+] Downloaded: $outPath" -ForegroundColor Green
} elseif ($Tier -eq "full") {
    Write-Host "[*] Fetching Full English Wikipedia ZIM (~48 GB)..." -ForegroundColor Yellow
    $url = "https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2024-01.zim"
    $outPath = Join-Path $destDir "wikipedia_full.zim"
    Invoke-WebRequest -Uri $url -OutFile $outPath
    Write-Host "[+] Downloaded: $outPath" -ForegroundColor Green
} else {
    Write-Host "[-] Skipping archive download." -ForegroundColor Gray
}
