# PowerShell wrapper for fetch_offline_archives.py
param (
    [ValidateSet("simple", "full", "gutenberg", "status")]
    [string]$Tier = "simple"
)

$script = Join-Path $PSScriptRoot "fetch_offline_archives.py"
python $script --tier $Tier
