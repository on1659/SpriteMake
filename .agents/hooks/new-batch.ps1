param(
  [string]$BatchId = "",

  [string]$GameProjectRoot = "",

  [string]$UserRequest = "",

  [ValidateSet("pending", "codex", "codex-setup", "gpt-image-2")]
  [string]$GenerationMode = "codex",

  [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

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

if ([string]::IsNullOrWhiteSpace($BatchId)) {
  $BatchId = New-BatchIdFromRequest $UserRequest
} else {
  $BatchId = ConvertTo-SafeSlug $BatchId "sprite-batch"
}

$createdAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
$batchRoot = Join-Path $ProjectRoot (Join-Path "output" $BatchId)
$folders = @(
  "",
  "prompts",
  "generated",
  "source",
  "manifests",
  "tools",
  "qa",
  "final"
)

foreach ($folder in $folders) {
  $path = if ($folder) { Join-Path $batchRoot $folder } else { $batchRoot }
  New-Item -ItemType Directory -Force -Path $path | Out-Null
}

$batchMd = Join-Path $batchRoot "BATCH.md"
$requestsMd = Join-Path $batchRoot "REQUESTS.md"
$promptMd = Join-Path $batchRoot "PROMPT.md"
$manifestMd = Join-Path $batchRoot "MANIFEST.md"
$qaMd = Join-Path $batchRoot "QA.md"

function Write-TextIfMissing([string]$Path, [string[]]$Lines) {
  if (-not (Test-Path -LiteralPath $Path)) {
    Set-Content -LiteralPath $Path -Encoding UTF8 -Value ($Lines -join [Environment]::NewLine)
  }
}

Write-TextIfMissing $batchMd @(
  "# Sprite Batch: $BatchId",
  "",
  "## Purpose",
  "",
  "- Created at: $createdAt",
  "- Original user request:",
  "",
  '```text',
  $UserRequest,
  '```',
  "",
  "- Game / project:",
  "- Feature / scene:",
  "- Shared gameplay purpose:",
  "- Shared visual direction:",
  "- Existing assets or style to match:",
  "- In-game scale reference:",
  "- Game project root: $GameProjectRoot",
  "- Strict generation provider: OpenAI Images API",
  "- Required image model for strict generation: gpt-image-2",
  "- Codex direct model guarantee: unverified when Generation mode is codex",
  "- Generation mode: $GenerationMode",
  "- Output folder: output/$BatchId",
  "",
  "## Assets",
  "",
  "| ID | Role | Target Path | Status |",
  "| --- | --- | --- | --- |",
  "| TBD | TBD | TBD | planned |",
  "",
  "## Status",
  "",
  "- planned"
)

Write-TextIfMissing $requestsMd @(
  "# Requests: $BatchId",
  "",
  "Use templates/batch-sprite-request-template.md and templates/resource-request-template.md.",
  "",
  "## Original User Request",
  "",
  '```text',
  $UserRequest,
  '```',
  "",
  "## Auto Paths",
  "",
  "- Batch folder: output/$BatchId",
  "- Prompt file: output/$BatchId/PROMPT.md",
  "- Generated attempts: output/$BatchId/generated/",
  "- QA reports: output/$BatchId/qa/",
  "- Final QA-passed assets: output/$BatchId/final/",
  "- Prompt variants: output/$BatchId/prompts/",
  "",
  "## Generation Choice",
  "",
  "- Current mode: $GenerationMode",
  "- Default keyless mode is codex: generate with Codex's built-in image tool, without API keys and without a verified gpt-image-2 model guarantee.",
  "- If strict gpt-image-2 is required, use mode gpt-image-2 and paste the prompt into ChatGPT web or another external generation environment.",
  "- If no image should be generated yet, use mode codex-setup.",
  "- SpriteMake never stores or uses API keys.",
  "",
  "## Asset Requests",
  "",
  '```text',
  "Asset:",
  "- ID:",
  "- Asset role:",
  "- Strict generation provider: OpenAI Images API",
  "- Required image model for strict generation: gpt-image-2",
  "- Codex direct model guarantee: unverified",
  "- Target file path:",
  "- Source/reference path:",
  "- Animation tool path:",
  "- Preview manifest path:",
  "- Asset type:",
  "- Static image or sprite atlas:",
  "- Final canvas size:",
  "- Grid columns:",
  "- Grid rows:",
  "- Cell size:",
  "- Row meanings:",
  "- Column meanings:",
  "- Contact anchor:",
  "- Contact anchor meaning:",
  "- Y-axis baseline/source plane:",
  "- Player-readable purpose:",
  "- Visual direction override:",
  "- QA priority:",
  '```'
)

Write-TextIfMissing $promptMd @(
  "# Prompt: $BatchId",
  "",
  "## Original User Request",
  "",
  '```text',
  $UserRequest,
  '```',
  "",
  "## SpriteMake Paths",
  "",
  "- Batch folder: output/$BatchId",
  "- Generated attempts folder: output/$BatchId/generated/",
  "- QA folder: output/$BatchId/qa/",
  "- Final folder: output/$BatchId/final/",
  "- Manifest folder: output/$BatchId/manifests/",
  "- Tool folder: output/$BatchId/tools/",
  "- Prompt variants folder: output/$BatchId/prompts/",
  "",
  "## Generation Decision",
  "",
  "- Mode: $GenerationMode",
  "- SpriteMake does not store API keys and does not call the image API directly.",
  "- Keyless Codex direct path: use the Codex image generation tool with the copy-ready prompt below; model selection is not user-selectable or verified as gpt-image-2.",
  "- Strict gpt-image-2 path: paste the copy-ready prompt below into ChatGPT web or another external generation environment that has access to that model.",
  "- Setup-only path: prepare these artifacts without generating an image.",
  "",
  "## Copy-Ready Prompt",
  "",
  "Generation Target:",
  "- Provider: OpenAI Images API",
  "- Required image model: gpt-image-2",
  "- Use gpt-image-2 for image generation or editing.",
  "- Do not silently substitute another image model.",
  "- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.",
  "- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.",
  "",
  "SpriteMake Output Contract:",
  "- Batch folder: output/$BatchId",
  "- Save raw generated attempts under: output/$BatchId/generated/",
  "- Save QA notes and screenshots under: output/$BatchId/qa/",
  "- Only QA-passed files may be moved to: output/$BatchId/final/",
  "",
  "User Request:",
  $UserRequest,
  "",
  "Create a transparent PNG-32 RGBA game sprite asset based on the user request.",
  "",
  "Use a strict sprite atlas if the request contains animation states, multiple variants, poses, directions, or frame sequences. Do not create a loose contact sheet.",
  "",
  "When atlas details are not specified, infer conservative defaults and state them in the output report:",
  "- final canvas size",
  "- grid columns and rows",
  "- cell size",
  "- row meanings",
  "- column meanings",
  "- contact anchor",
  "- Y-axis baseline or source plane",
  "",
  "Required Sprite Rules:",
  "- Fully transparent background.",
  "- No watermark, no labels, no guide grid, no text.",
  "- PNG-32 RGBA, straight alpha, sRGB.",
  "- Each cell contains exactly one complete frame when using an atlas.",
  "- No frame may bleed into adjacent cells.",
  "- Transparent padding may exist only inside fixed cells.",
  "- Contact anchor is not the visual center.",
  "- Y-axis baseline/source plane must not drift across frames, rows, or variants.",
  "- Keep silhouette, angle, lighting, and scale consistent across related variants.",
  "",
  "Output Report:",
  "- Final image size.",
  "- Whether the result is static or atlas.",
  "- Grid, cell size, row meanings, and column meanings if atlas.",
  "- Contact anchor and anchor meaning.",
  "- Y-axis baseline/source plane.",
  "- Alpha bbox and per-cell alpha bbox if possible.",
  "- Confirm the asset can be saved first under output/$BatchId/generated/."
)

Write-TextIfMissing $manifestMd @(
  "# Manifest Notes: $BatchId",
  "",
  "## Manifest Files",
  "",
  "- manifests/",
  "",
  "## Runtime Contracts",
  "",
  "| Asset | Image | Grid | Cell | Anchor | Baseline |",
  "| --- | --- | --- | --- | --- | --- |",
  "| TBD | TBD | TBD | TBD | TBD | TBD |"
)

Write-TextIfMissing $qaMd @(
  "# QA: $BatchId",
  "",
  "Use templates/asset-qa-checklist.md.",
  "",
  "## Summary",
  "",
  "- Asset count:",
  "- Passed:",
  "- Needs regeneration:",
  "- Needs repack:",
  "- Ready for game:",
  "",
  "## Reports",
  "",
  "| Asset | Size | Grid | Alpha BBox | Preview Tool | Status |",
  "| --- | --- | --- | --- | --- | --- |",
  "| TBD | TBD | TBD | TBD | TBD | qa-needed |"
)

Write-Host "Created SpriteMake batch scaffold: $batchRoot"
Write-Host "Prompt file: $promptMd"


