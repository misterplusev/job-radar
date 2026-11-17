# Process snapshot for the machine-safety tools (2026-10-19, Claude). Read-only. Prints ONE line of JSON.
# Used by 20261019_machine_watchdog_v1_0_0.py and by the Idea City runaway guard (scripts/lib/20261019_runaway_guard_v1_0_0.mjs).
# Command lines are inspected HERE ONLY to classify processes; they are never printed (prompts and URLs stay private).
#
# Kinds:
#   cft            Chrome for Testing / Chromium automation browser (any install: Hermes tools\chromium-*, ms-playwright,
#                  puppeteer, agent-browser). The user's real Google Chrome (Program Files\Google\Chrome) is NEVER cft.
#   cftHermes      cft whose exe is Hermes' bundled browser (%LOCALAPPDATA%\hermes\tools\chromium-*).
#   top            for cft: the browser's main process (command line has no --type=); one "instance" = one top process.
#   orphan         for cft top processes: the parent process no longer exists (leaked browser).
#   hermesOneShot  hermes.exe started with -z / --oneshot (a headless one-shot agent).
#   opencodeRun    opencode.exe started with "run" (a headless one-shot agent).
#   ideaCityLoop   node.exe running scripts\(groundskeeper|inspector|builder|council|idea_city|verification).mjs
$ErrorActionPreference = 'SilentlyContinue'
$all = Get-CimInstance Win32_Process
$ids = New-Object 'System.Collections.Generic.HashSet[int]'
foreach ($p in $all) { [void]$ids.Add([int]$p.ProcessId) }
$cftPath = '(?i)(\\hermes\\tools\\chromium-|\\ms-playwright\\|\\puppeteer\\|\\agent-browser|\\chrome-win64\\|\\chrome-headless-shell-win64\\)'
$realChrome = '(?i)\\Google\\Chrome\\Application\\'
$loopRe = '(?i)(^|[\\/\s"])scripts[\\/](groundskeeper|inspector|builder|council|idea_city|verification)\.mjs'
$items = New-Object System.Collections.ArrayList
foreach ($p in $all) {
  $name = [string]$p.Name; $cmd = [string]$p.CommandLine; $exe = [string]$p.ExecutablePath
  $kind = $null; $extra = @{}
  if ($name -match '^(chrome|chrome-headless-shell)\.exe$' -and $exe -match $cftPath -and $exe -notmatch $realChrome) {
    $kind = 'cft'
    $extra.cftHermes = [bool]($exe -match '(?i)\\hermes\\tools\\chromium-')
    $extra.top = -not ($cmd -match '--type=')
    $extra.orphan = $extra.top -and -not $ids.Contains([int]$p.ParentProcessId)
    $extra.install = if ($exe -match '(?i)\\hermes\\tools\\(chromium-\d+)') { 'hermes:' + $Matches[1] } elseif ($exe -match '(?i)\\ms-playwright\\([^\\]+)') { 'playwright:' + $Matches[1] } elseif ($exe -match '(?i)puppeteer') { 'puppeteer' } else { 'other' }
  } elseif ($name -ieq 'hermes.exe' -and $cmd -match '(\s|^)(-z|--oneshot)(\s|=|$)') {
    $kind = 'hermesOneShot'
  } elseif ($name -ieq 'opencode.exe' -and $cmd -match '(?i)\srun\s') {
    $kind = 'opencodeRun'
  } elseif ($name -ieq 'node.exe' -and $cmd -match $loopRe) {
    $kind = 'ideaCityLoop'; $extra.script = $Matches[2]
  }
  if ($kind) {
    $o = [ordered]@{ id = [int]$p.ProcessId; ppid = [int]$p.ParentProcessId; name = $name; kind = $kind
      created = if ($p.CreationDate) { $p.CreationDate.ToUniversalTime().ToString('o') } else { $null }
      privMB = [math]::Round(([double]$p.PageFileUsage) / 1024, 1) }
    foreach ($k in $extra.Keys) { $o[$k] = $extra[$k] }
    [void]$items.Add([pscustomobject]$o)
  }
}
$os = Get-CimInstance Win32_OperatingSystem
$byName = $all | Group-Object Name | ForEach-Object {
  [pscustomobject]@{ name = $_.Name; count = $_.Count; privMB = [math]::Round((($_.Group | Measure-Object PageFileUsage -Sum).Sum) / 1024, 0) } } |
  Sort-Object privMB -Descending | Select-Object -First 10
[pscustomobject]@{
  utc = (Get-Date).ToUniversalTime().ToString('o')
  procCount = $all.Count
  commitLimitKB = [int64]$os.TotalVirtualMemorySize
  commitFreeKB = [int64]$os.FreeVirtualMemory
  physTotalKB = [int64]$os.TotalVisibleMemorySize
  physFreeKB = [int64]$os.FreePhysicalMemory
  topByName = @($byName)
  procs = @($items)
} | ConvertTo-Json -Depth 4 -Compress
