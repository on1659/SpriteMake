param(
  [string]$Request = "",

  [string]$BatchId = "",

  [ValidateSet("pending", "codex", "codex-setup", "gpt-image-2")]
  [string]$Mode = "codex",

  [string]$GameProjectRoot = "",

  [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

function Get-RequestText {
  if (-not [string]::IsNullOrWhiteSpace($Request)) {
    return $Request.Trim()
  }

  if ([Console]::IsInputRedirected) {
    return ([Console]::In.ReadToEnd()).Trim()
  }

  return ""
}

function ConvertTo-SafeSlug([string]$Value, [string]$Fallback) {
  $slug = $Value.ToLowerInvariant()
  $slug = [Text.RegularExpressions.Regex]::Replace($slug, "[^a-z0-9._-]+", "-")
  $slug = [Text.RegularExpressions.Regex]::Replace($slug, "-+", "-").Trim("-._")

  if ([string]::IsNullOrWhiteSpace($slug)) {
    return $Fallback
  }

  if ($slug.Length -gt 48) {
    $slug = $slug.Substring(0, 48).Trim("-._")
  }

  return $slug
}

function New-BatchIdFromRequest([string]$Text) {
  $tokens = @()

  $krDragon = [string]::Concat([char]0xB4DC, [char]0xB798, [char]0xACE4)
  $krFire = [string]::Concat([char]0xBD88)
  $krFlame = [string]::Concat([char]0xD654, [char]0xC5FC)
  $krIce = [string]::Concat([char]0xC5BC, [char]0xC74C)
  $krFrost = [string]::Concat([char]0xBE59, [char]0xACB0)
  $krSprite = [string]::Concat([char]0xC2A4, [char]0xD504, [char]0xB77C, [char]0xC774, [char]0xD2B8)
  $krCharacter = [string]::Concat([char]0xCE90, [char]0xB9AD, [char]0xD130)
  $krTile = [string]::Concat([char]0xD0C0, [char]0xC77C)
  $krEffect = [string]::Concat([char]0xC774, [char]0xD399, [char]0xD2B8)
  $krIcon = [string]::Concat([char]0xC544, [char]0xC774, [char]0xCF58)
  $krRide = [string]::Concat([char]0xD0D1, [char]0xC2B9)
  $krCanRidePattern = [string]::Concat([char]0xD0C8) + "\s*" + [string]::Concat([char]0xC218)

  if ($Text -match "(?i)dragon" -or $Text.Contains($krDragon)) { $tokens += "dragon" }
  if ($Text -match "(?i)fire|flame" -or $Text.Contains($krFire) -or $Text.Contains($krFlame)) { $tokens += "fire" }
  if ($Text -match "(?i)ice|frost" -or $Text.Contains($krIce) -or $Text.Contains($krFrost)) { $tokens += "ice" }
  if ($Text -match "(?i)sprite" -or $Text.Contains($krSprite)) { $tokens += "sprite" }
  if ($Text -match "(?i)character" -or $Text.Contains($krCharacter)) { $tokens += "character" }
  if ($Text -match "(?i)tile" -or $Text.Contains($krTile)) { $tokens += "tile" }
  if ($Text -match "(?i)effect|fx" -or $Text.Contains($krEffect)) { $tokens += "fx" }
  if ($Text -match "(?i)icon" -or $Text.Contains($krIcon)) { $tokens += "icon" }
  if ($Text -match "(?i)ride|mount" -or $Text.Contains($krRide) -or $Text -match $krCanRidePattern) { $tokens += "rideable" }

  $tokens = @($tokens | Select-Object -Unique)

  if ($tokens.Count -eq 0) {
    $ascii = ConvertTo-SafeSlug $Text "sprite-batch"
    if ($ascii -ne "sprite-batch") {
      $tokens += $ascii
    }
  }

  if ($tokens.Count -eq 0) {
    $tokens += "sprite-batch"
  }

  $base = ($tokens | Select-Object -First 5) -join "-"
  $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
  return "$base-$stamp"
}

$requestText = Get-RequestText

if ([string]::IsNullOrWhiteSpace($requestText)) {
  throw "sprite-intake requires -Request or piped request text."
}

$resolvedBatchId = if ([string]::IsNullOrWhiteSpace($BatchId)) {
  New-BatchIdFromRequest $requestText
} else {
  ConvertTo-SafeSlug $BatchId "sprite-batch"
}

$newBatch = Join-Path $PSScriptRoot "new-batch.ps1"
$newBatchArgs = @{
  BatchId = $resolvedBatchId
  UserRequest = $requestText
  GenerationMode = $Mode
  ProjectRoot = $ProjectRoot
}

if (-not [string]::IsNullOrWhiteSpace($GameProjectRoot)) {
  $newBatchArgs.GameProjectRoot = $GameProjectRoot
}

& $newBatch @newBatchArgs

$batchRoot = Join-Path $ProjectRoot (Join-Path "output" $resolvedBatchId)
$promptPath = Join-Path $batchRoot "PROMPT.md"
$requestPath = Join-Path $batchRoot "REQUESTS.md"

$promptInject = Join-Path $PSScriptRoot "prompt-inject.ps1"
if (Test-Path -LiteralPath $promptPath) {
  & $promptInject -InputPath $promptPath -OutputPath $promptPath
}

Write-Host ""
Write-Host "SpriteMake intake ready."
Write-Host "- Batch: $resolvedBatchId"
Write-Host "- Output: $batchRoot"
Write-Host "- Request doc: $requestPath"
Write-Host "- Prompt doc: $promptPath"
Write-Host "- API key: not used, not stored"
Write-Host "- Generation mode: $Mode"

if ($Mode -eq "codex") {
  Write-Host "- Codex direct: use the Codex image generation tool; model is not forced or verified as gpt-image-2"
  Write-Host "- Save or reference the generated attempt under generated/ before QA"
} elseif ($Mode -eq "codex-setup") {
  Write-Host "- Codex setup-only: no image generation requested"
} else {
  Write-Host "- Required image model for strict external generation: gpt-image-2"
}

if ($Mode -eq "pending") {
  Write-Host ""
  & (Join-Path $PSScriptRoot "generation-choice.ps1")
}


