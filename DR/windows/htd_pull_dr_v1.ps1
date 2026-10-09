$ErrorActionPreference = 'Stop'

$Ssh = "$env:WINDIR\System32\OpenSSH\ssh.exe"
$Scp = "$env:WINDIR\System32\OpenSSH\scp.exe"

$Root = 'C:\HTD-RECOVERY'
$LogDir = Join-Path $Root 'LOGS'
$LogFile = Join-Path $LogDir ('pull_dr_v1_' + (Get-Date -Format 'yyyyMMdd') + '.log')

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $Message"
    Write-Host $line
    Add-Content -LiteralPath $LogFile -Value $line
}

function Verify-Manifest {
    param([string]$Directory)

    $manifest = Join-Path $Directory 'manifest.sha256'
    if (-not (Test-Path -LiteralPath $manifest)) {
        throw "Manifest missing: $manifest"
    }

    foreach ($line in Get-Content -LiteralPath $manifest) {
        if ($line -notmatch '^([0-9a-fA-F]{64})\s+\*?(.+)$') {
            throw "Invalid manifest line: $line"
        }

        $expected = $matches[1].ToLowerInvariant()
        $name = $matches[2]
        $file = Join-Path $Directory $name

        if (-not (Test-Path -LiteralPath $file)) {
            throw "Backup file missing: $file"
        }

        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $file).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "SHA256 mismatch: $name"
        }

        Write-Log "$name : OK"
    }
}

function Pull-LatestBackup {
    param(
        [string]$Node,
        [string]$HostAddress,
        [string]$Prefix,
        [string]$Destination
    )

    Write-Log "=== $Node ==="

    $remoteCommand = "find /home/hydrotech/htd_backups -maxdepth 1 -type d -name '${Prefix}_*' -printf '%f\n' | sort | tail -n 1"
    $latest = (& $Ssh -o BatchMode=yes -o ConnectTimeout=10 "hydrotech@$HostAddress" $remoteCommand).Trim()

    if ($LASTEXITCODE -ne 0) {
        throw "$Node SSH lookup failed."
    }

    if ([string]::IsNullOrWhiteSpace($latest)) {
        throw "$Node has no DR V1 backup directory."
    }

    if ($latest -notmatch ('^' + [regex]::Escape($Prefix) + '_\d{8}_\d{6}$')) {
        throw "$Node returned unexpected backup name: $latest"
    }

    Write-Log "Latest remote backup: $latest"

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    $localDir = Join-Path $Destination $latest

    if (-not (Test-Path -LiteralPath $localDir)) {
        Write-Log "Copying $Node backup to tower..."
        & $Scp -q -r -o BatchMode=yes -o ConnectTimeout=10 "hydrotech@${HostAddress}:/home/hydrotech/htd_backups/$latest" "$Destination\"
        if ($LASTEXITCODE -ne 0) {
            throw "$Node SCP failed."
        }
    }
    else {
        Write-Log "Backup already present locally; verifying existing copy."
    }

    Verify-Manifest -Directory $localDir
    Write-Log "$Node DR V1 pull verified: $localDir"
}

try {
    Write-Log 'HTD DR V1 nightly pull started.'

    Pull-LatestBackup `
        -Node 'EDGE' `
        -HostAddress '192.168.1.124' `
        -Prefix 'dr_v1_edge' `
        -Destination (Join-Path $Root 'EDGE\nightly')

    Pull-LatestBackup `
        -Node 'CORE' `
        -HostAddress '192.168.1.137' `
        -Prefix 'dr_v1_core' `
        -Destination (Join-Path $Root 'CORE\nightly')

    Write-Log 'HTD_DR_V1_PULL_OK'
    exit 0
}
catch {
    Write-Log ("ERROR: " + $_.Exception.Message)
    exit 1
}
