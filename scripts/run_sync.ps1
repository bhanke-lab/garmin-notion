# Runs the Garmin to Notion sync from this machine.
# Called by Task Scheduler; can also be run by hand from any prompt.
# Reads credentials from the .env file in the project root.

$project = Split-Path -Parent $PSScriptRoot
Set-Location $project

$env:PYTHONPATH = "src"

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "$project\sync_log.txt" -Value "----- sync started $stamp -----"

& "$project\.venv\Scripts\python.exe" -m garmin_to_notion all -v 2>&1 |
    Add-Content -Path "$project\sync_log.txt"

$code = $LASTEXITCODE
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path "$project\sync_log.txt" -Value "----- sync finished $stamp (exit $code) -----"
exit $code
