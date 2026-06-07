param(
  [string]$ProcessName = "node",
  [int]$Port = 3000,
  [string]$TargetHost = "github.com"
)

Write-Host "========================================"
Write-Host " Bhari Sagar - Server Health Check"
Write-Host "========================================"
Write-Host "Hostname        : $env:COMPUTERNAME"
Write-Host "Date            : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "PowerShell      : $($PSVersionTable.PSVersion)"

Write-Host "`n[CPU]"
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
Write-Host "CPU Name        : $($cpu.Name)"
Write-Host "CPU Load        : $($cpu.LoadPercentage)%"

Write-Host "`n[Memory]"
$os = Get-CimInstance Win32_OperatingSystem
$totalMemoryGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeMemoryGb = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$usedMemoryGb = [math]::Round($totalMemoryGb - $freeMemoryGb, 2)
Write-Host "Total           : $totalMemoryGb GB"
Write-Host "Used            : $usedMemoryGb GB"
Write-Host "Free            : $freeMemoryGb GB"

Write-Host "`n[Disk]"
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
  Select-Object DeviceID,
    @{Name="SizeGB"; Expression={[math]::Round($_.Size / 1GB, 2)}},
    @{Name="FreeGB"; Expression={[math]::Round($_.FreeSpace / 1GB, 2)}} |
  Format-Table -AutoSize

Write-Host "`n[Process Check]"
$process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
if ($process) {
  Write-Host "$ProcessName            : running"
} else {
  Write-Host "$ProcessName            : not running"
}

Write-Host "`n[Port Check]"
$portCheck = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portCheck) {
  Write-Host "$Port            : listening"
} else {
  Write-Host "$Port            : not listening"
}

Write-Host "`n[Network]"
if (Test-Connection -ComputerName $TargetHost -Count 1 -Quiet) {
  Write-Host "$TargetHost      : reachable"
} else {
  Write-Host "$TargetHost      : not reachable"
}

Write-Host "----------------------------------------"
Write-Host "Result          : health check completed"
