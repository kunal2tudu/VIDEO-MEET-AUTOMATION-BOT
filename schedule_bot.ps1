$TaskName = 'LPU_ClassBot_7PM'
$BotDir = ''
$BotScript = ''
$PythonExe = (Get-Command python).Source

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed old task."
}

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday -At '7:00PM'
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument $BotScript -WorkingDirectory $BotDir
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2) -StartWhenAvailable -RunOnlyIfNetworkAvailable

Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -RunLevel Highest -Force | Out-Null

Write-Host "Task '$TaskName' registered! Runs Mon-Fri at 7:00 PM."
