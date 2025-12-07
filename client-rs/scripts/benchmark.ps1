param(
  [int]$DurationSec,
  [string]$OutputDir,
  [string]$RustDebug,
  [string]$RustRelease,
  [string]$PythonExe,
  [string]$PythonEntry
)

$ErrorActionPreference = 'Stop'

function Measure-Client($name, $startCmd, $durationSeconds) {
  $cpuCores = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
  $proc = Start-Process -FilePath $startCmd[0] -ArgumentList $startCmd[1..($startCmd.Length-1)] -PassThru -WindowStyle Hidden
  Start-Sleep -Milliseconds 500
  $samples = @()
  $t0 = Get-Date
  try { $prevCpu = (Get-Process -Id $proc.Id).CPU } catch { $prevCpu = 0 }
  for ($i=0; $i -lt $durationSeconds; $i++) {
    Start-Sleep -Seconds 1
    try {
      $p = Get-Process -Id $proc.Id
    } catch {
      break
    }
    $cpuTotal = $p.CPU
    $cpuDelta = $cpuTotal - $prevCpu
    $prevCpu = $cpuTotal
    $cpuPct = [math]::Min(100, [math]::Max(0, ($cpuDelta / 1.0) * 100.0 / $cpuCores))
    $samples += [pscustomobject]@{
      Time = (Get-Date).ToString('HH:mm:ss')
      CPUPct = [math]::Round($cpuPct,2)
      WorkingSetMB = [math]::Round($p.WorkingSet64/1MB,2)
      PrivateMB    = [math]::Round($p.PrivateMemorySize64/1MB,2)
      Handles = $p.HandleCount
      Threads = $p.Threads.Count
    }
  }
  $t1 = Get-Date
  if ($proc.HasExited -eq $false) { try { Stop-Process -Id $proc.Id -Force } catch {} }
  $avgCpu = [math]::Round((($samples | Measure-Object -Property CPUPct -Average).Average),2)
  $peakCpu = [math]::Round((($samples | Measure-Object -Property CPUPct -Maximum).Maximum),2)
  $avgWs = [math]::Round((($samples | Measure-Object -Property WorkingSetMB -Average).Average),2)
  $peakWs = [math]::Round((($samples | Measure-Object -Property WorkingSetMB -Maximum).Maximum),2)
  $avgPriv = [math]::Round((($samples | Measure-Object -Property PrivateMB -Average).Average),2)
  $peakPriv = [math]::Round((($samples | Measure-Object -Property PrivateMB -Maximum).Maximum),2)
  $avgHandles = [math]::Round((($samples | Measure-Object -Property Handles -Average).Average),0)
  $peakHandles = [math]::Round((($samples | Measure-Object -Property Handles -Maximum).Maximum),0)
  $avgThreads = [math]::Round((($samples | Measure-Object -Property Threads -Average).Average),0)
  $peakThreads = [math]::Round((($samples | Measure-Object -Property Threads -Maximum).Maximum),0)
  [pscustomobject]@{
    Name = $name
    DurationSec = [math]::Round(($t1 - $t0).TotalSeconds,0)
    AvgCPU = $avgCpu
    PeakCPU = $peakCpu
    AvgWorkingSetMB = $avgWs
    PeakWorkingSetMB = $peakWs
    AvgPrivateMB = $avgPriv
    PeakPrivateMB = $peakPriv
    AvgHandles = $avgHandles
    PeakHandles = $peakHandles
    AvgThreads = $avgThreads
    PeakThreads = $peakThreads
  }, $samples
}

function Write-Result($summary, $samples, $outDir) {
  if (-not [string]::IsNullOrWhiteSpace($outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $summary | Export-Csv -Path (Join-Path $outDir ("summary-" + $summary.Name + ".csv")) -NoTypeInformation
    $samples | Export-Csv -Path (Join-Path $outDir ("samples-" + $summary.Name + ".csv")) -NoTypeInformation
  }
}

$repo = Split-Path $PSScriptRoot -Parent
if (-not $DurationSec) { $DurationSec = 60 }
if (-not $OutputDir) { $OutputDir = Join-Path $repo 'dist/bench' }
if (-not $RustRelease) { $RustRelease = Join-Path $repo 'target\release\client-rs.exe' }
if (-not $RustDebug) { $RustDebug = Join-Path $repo 'target\debug\client-rs.exe' }
if (-not $PythonExe) { $PythonExe = Join-Path $repo 'venv\Scripts\python.exe' }
if (-not $PythonEntry) { $PythonEntry = Join-Path $repo 'client\main.py' }

$results = @()

if (Test-Path $RustRelease) {
  $r = Measure-Client 'rust-release' @($RustRelease) $DurationSec
  $results += $r[0]; Write-Result $r[0] $r[1] $OutputDir
}
elseif (Test-Path $RustDebug) {
  $r = Measure-Client 'rust-debug' @($RustDebug) $DurationSec
  $results += $r[0]; Write-Result $r[0] $r[1] $OutputDir
}

if ((Test-Path $PythonExe) -and (Test-Path $PythonEntry)) {
  $p = Measure-Client 'python-client' @($PythonExe, $PythonEntry) $DurationSec
  $results += $p[0]; Write-Result $p[0] $p[1] $OutputDir
}

if ($results.Count -gt 0) {
  $results | Format-Table Name,DurationSec,AvgCPU,PeakCPU,AvgWorkingSetMB,PeakWorkingSetMB,AvgPrivateMB,PeakPrivateMB,AvgHandles,PeakHandles,AvgThreads,PeakThreads -AutoSize | Out-String | Write-Output
} else {
  Write-Host 'No targets found to benchmark.'
}
