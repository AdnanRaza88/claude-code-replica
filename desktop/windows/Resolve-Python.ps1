param(
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"
if (-not $RepoRoot) {
    $RepoRoot = (Get-Location).Path
}

function Test-Py([string]$exe) {
    if (-not $exe) { return $false }
    if (-not (Test-Path $exe) -and $exe -notmatch '^(python|py)(\.exe)?$') {
        $cmd = Get-Command $exe -ErrorAction SilentlyContinue
        if (-not $cmd) { return $false }
        $exe = $cmd.Source
    }
    try {
        & $exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

$candidates = @()
if ($env:AGENTFORGE_PYTHON) { $candidates += $env:AGENTFORGE_PYTHON }
$candidates += @(
    (Join-Path $RepoRoot "python\python.exe"),
    (Join-Path $RepoRoot "python\Scripts\python.exe"),
    "py",
    "python",
    "python3"
)

foreach ($c in $candidates) {
    if (Test-Py $c) {
        Write-Output $c
        exit 0
    }
}

Write-Error "Python 3.11+ not found. Install from https://www.python.org/downloads/ and tick 'Add python.exe to PATH', or set AGENTFORGE_PYTHON, or drop embeddable CPython under python\."
exit 1
