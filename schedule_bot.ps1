$TaskName = 'LPU_ClassBot'
$BotDir = ''           # e.g. 'C:\path\to\lpu_bot'
$BotScript = ''        # e.g. 'C:\path\to\lpu_bot\lpu_join_class.py'
$ScheduleTime = ''     # e.g. '6:00PM'
$ScheduleDays = @()    # e.g. @('Monday', 'Wednesday', 'Friday')
$PythonExe = (Get-Command python).Source

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed old task."
}

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $ScheduleDays -At $ScheduleTime
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $BotScript -WorkingDirectory $BotDir
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -RunLevel Highest -Force | Out-Null

Write-Host "Task '$TaskName' registered! Runs on $ScheduleDays at $ScheduleTime."
