# Registers the twice-daily Garmin to Notion sync in Windows Task Scheduler.
# Run once from a PowerShell prompt in the project root:
#   .\scripts\register_sync_task.ps1
# To change the schedule, edit the two trigger times below and run it again.
# Interactive logon type means it runs while you are logged in, including
# when the screen is locked, without storing your password.

$scriptPath = Join-Path $PSScriptRoot "run_sync.ps1"

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

$morning = New-ScheduledTaskTrigger -Daily -At 7:05AM
$evening = New-ScheduledTaskTrigger -Daily -At 8:05PM

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive

$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd

Register-ScheduledTask -TaskName "Garmin Notion Sync" `
    -Action $action -Trigger $morning, $evening `
    -Principal $principal -Settings $settings -Force

Write-Host "Registered 'Garmin Notion Sync' for 7:05 AM and 8:05 PM daily."
Write-Host "Missed runs fire on next unlock thanks to StartWhenAvailable."
