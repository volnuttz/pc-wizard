param(
    [Parameter(Mandatory = $true)][string]$Executable,
    [Parameter(Mandatory = $true)][string]$Fixture,
    [Parameter(Mandatory = $true)][string]$Template,
    [Parameter(Mandatory = $true)][string]$Output,
    [int]$WarmRuns = 5
)

$ErrorActionPreference = "Stop"
$Executable = (Resolve-Path $Executable).Path
$Fixture = (Resolve-Path $Fixture).Path
$Template = (Resolve-Path $Template).Path
$temporary = Join-Path ([System.IO.Path]::GetTempPath()) ("pc-wizard-benchmark-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $temporary | Out-Null

function Invoke-Scenario {
    param([string]$Name, [string[]]$Arguments)
    $samples = @()
    $peakBytes = 0
    for ($index = 0; $index -le $WarmRuns; $index++) {
        $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
        $startInfo.FileName = $Executable
        $startInfo.UseShellExecute = $false
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        foreach ($argument in $Arguments) { $startInfo.ArgumentList.Add($argument) }
        $process = [System.Diagnostics.Process]::new()
        $process.StartInfo = $startInfo
        $watch = [System.Diagnostics.Stopwatch]::StartNew()
        if (-not $process.Start()) { throw "Unable to start $Name" }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $process.WaitForExit()
        $watch.Stop()
        if ($process.ExitCode -ne 0) {
            throw "$Name exited $($process.ExitCode): $($stdout.Result) $($stderr.Result)"
        }
        $peakBytes = [Math]::Max($peakBytes, $process.PeakWorkingSet64)
        $samples += [Math]::Round($watch.Elapsed.TotalMilliseconds, 3)
    }
    $warm = @($samples | Select-Object -Skip 1 | Sort-Object)
    $middle = [int][Math]::Floor($warm.Count / 2)
    $median = if ($warm.Count % 2 -eq 0) {
        [Math]::Round(($warm[$middle - 1] + $warm[$middle]) / 2, 3)
    } else {
        $warm[$middle]
    }
    [ordered]@{
        cold_ms = $samples[0]
        warm_median_ms = $median
        warm_samples_ms = $warm
        peak_working_set_bytes = $peakBytes
    }
}

try {
    $json = Join-Path $temporary "character.json"
    $pdf = Join-Path $temporary "character.pdf"
    $result = [ordered]@{
        schema_version = 1
        platform = [System.Runtime.InteropServices.RuntimeInformation]::RuntimeIdentifier
        executable_bytes = (Get-Item $Executable).Length
        one_file_extraction_overhead_ms = 0
        scenarios = [ordered]@{
            version = Invoke-Scenario "version" @("--version")
            show = Invoke-Scenario "show" @("show", $Fixture)
            create = Invoke-Scenario "create" @("create", "--template", $Template, "--from-json", $Fixture, "--json", $json, "--output", $pdf, "--force")
        }
    }
    $parent = Split-Path -Parent $Output
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $result | ConvertTo-Json -Depth 8 | Set-Content -Path $Output -Encoding utf8
} finally {
    Remove-Item -Recurse -Force $temporary -ErrorAction SilentlyContinue
}
