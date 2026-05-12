param(
  [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$failed = $false

function Fail($Message) {
  Write-Host "[FAIL] $Message" -ForegroundColor Red
  $script:failed = $true
}

function Pass($Message) {
  Write-Host "[ OK ] $Message" -ForegroundColor Green
}

function Warn($Message) {
  Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

$required = @(
  "README.md",
  "USAGE.md",
  "HANDOFF.md",
  "AGENTS.md",
  "WORKFLOW.md",
  "start-symphony-gui.bat",
  "mockup.html",
  "symphony-concept.html",
  "symphony-usage.html",
  "tools\symphony-gui\server.js",
  "tools\symphony-gui\public\index.html",
  "templates\batch-sprite-request-template.md",
  "templates\folder-md-setup-template.md",
  "templates\resource-request-template.md",
  "templates\sprite-atlas-template.md",
  "templates\asset-qa-checklist.md",
  "templates\animation-player-template.html",
  "templates\animation-manifest-template.json",
  ".agents\README.md",
  ".agents\skills\spritemake-batch\SKILL.md",
  ".agents\hooks\preflight.ps1",
  ".agents\hooks\sprite-intake.ps1",
  ".agents\hooks\sprite-intake.config.json",
  ".agents\hooks\symphony.ps1",
  ".agents\hooks\symphony.config.json",
  ".agents\hooks\new-batch.ps1",
  ".agents\hooks\generation-choice.ps1",
  ".agents\hooks\generation-choice.config.json",
  ".agents\hooks\prompt-inject.ps1",
  ".agents\hooks\prompt-hook.config.json"
)

foreach ($relative in $required) {
  $path = Join-Path $ProjectRoot $relative
  if (Test-Path -LiteralPath $path) {
    Pass "exists $relative"
  } else {
    Fail "missing $relative"
  }
}

$manifestPath = Join-Path $ProjectRoot "templates\animation-manifest-template.json"
if (Test-Path -LiteralPath $manifestPath) {
  try {
    Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json | Out-Null
    Pass "animation manifest template parses"
  } catch {
    Fail "animation manifest template JSON parse failed: $($_.Exception.Message)"
  }
}

$hookConfigFiles = @(
  ".agents\hooks\sprite-intake.config.json",
  ".agents\hooks\symphony.config.json",
  ".agents\hooks\generation-choice.config.json",
  ".agents\hooks\prompt-hook.config.json"
)

foreach ($relative in $hookConfigFiles) {
  $path = Join-Path $ProjectRoot $relative
  if (Test-Path -LiteralPath $path) {
    try {
      Get-Content -Raw -LiteralPath $path | ConvertFrom-Json | Out-Null
      Pass "hook config parses $relative"
    } catch {
      Fail "hook config JSON parse failed $relative`: $($_.Exception.Message)"
    }
  }
}

$handoffPath = Join-Path $ProjectRoot "HANDOFF.md"
if (Test-Path -LiteralPath $handoffPath) {
  $handoffText = Get-Content -Raw -Encoding UTF8 -LiteralPath $handoffPath
  $hasReplacementChar = $handoffText.Contains(([char]0xfffd).ToString())
  $hasCjkMojibake = [Text.RegularExpressions.Regex]::IsMatch($handoffText, "[\u4E00-\u9FFF\uF900-\uFAFF]")
  $hangulCount = [Text.RegularExpressions.Regex]::Matches($handoffText, "[\uAC00-\uD7A3]").Count
  if ($hasReplacementChar -or $hasCjkMojibake -or $hangulCount -lt 20) {
    Fail "HANDOFF.md appears to contain mojibake/encoding corruption"
  } else {
    Pass "HANDOFF.md encoding sanity"
  }
}

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
  $jsFiles = @("tools\symphony-gui\server.js")
  foreach ($relative in $jsFiles) {
    $path = Join-Path $ProjectRoot $relative
    if (Test-Path -LiteralPath $path) {
      & node --check $path
      if ($LASTEXITCODE -eq 0) {
        Pass "node syntax $relative"
      } else {
        Fail "node syntax failed $relative"
      }
    }
  }

  $htmlFiles = @("mockup.html", "symphony-usage.html", "tools\symphony-gui\public\index.html", "templates\animation-player-template.html")
  foreach ($relative in $htmlFiles) {
    $path = Join-Path $ProjectRoot $relative
    if (Test-Path -LiteralPath $path) {
      $script = @"
const fs = require('fs');
const html = fs.readFileSync(process.argv[1], 'utf8');
const match = html.match(/<script>([\s\S]*)<\/script>/);
if (!match) process.exit(0);
new Function(match[1]);
"@
      $tmp = [System.IO.Path]::GetTempFileName() + ".js"
      Set-Content -LiteralPath $tmp -Value $script -Encoding UTF8
      try {
        & node $tmp $path
        if ($LASTEXITCODE -eq 0) {
          Pass "script syntax $relative"
        } else {
          Fail "script syntax failed $relative"
        }
      } finally {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
      }
    }
  }
} else {
  Warn "node not found; skipped HTML script syntax checks"
}

$promptHook = Join-Path $ProjectRoot ".agents\hooks\prompt-inject.ps1"
if (Test-Path -LiteralPath $promptHook) {
  $sample = "Create a transparent sprite atlas."
  $hooked = $sample | powershell -NoProfile -ExecutionPolicy Bypass -File $promptHook
  if ($hooked -match "Required image model:\s*gpt-image-2") {
    Pass "prompt hook injects gpt-image-2"
  } else {
    Fail "prompt hook did not inject gpt-image-2"
  }
}

$choiceHook = Join-Path $ProjectRoot ".agents\hooks\generation-choice.ps1"
if (Test-Path -LiteralPath $choiceHook) {
  $choiceText = powershell -NoProfile -ExecutionPolicy Bypass -File $choiceHook -Short
  if ($choiceText -match "Codex" -and $choiceText -match "gpt-image-2" -and $choiceText -match "ChatGPT") {
    Pass "generation choice hook prints standard choice"
  } else {
    Fail "generation choice hook is missing required choice text"
  }
}

$intakeHook = Join-Path $ProjectRoot ".agents\hooks\sprite-intake.ps1"
if (Test-Path -LiteralPath $intakeHook) {
  $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("SpriteMakePreflight-" + [guid]::NewGuid().ToString("N"))
  try {
    powershell -NoProfile -ExecutionPolicy Bypass -File $intakeHook -Request "dragon sprite with fire and ice variants" -BatchId "preflight-dragon" -Mode codex -ProjectRoot $tempRoot | Out-Null
    $promptPath = Join-Path $tempRoot "output\preflight-dragon\PROMPT.md"
    if ((Test-Path -LiteralPath $promptPath) -and ((Get-Content -Raw -Encoding UTF8 -LiteralPath $promptPath) -match "Required image model:\s*gpt-image-2")) {
      Pass "sprite intake scaffold and prompt"
    } else {
      Fail "sprite intake did not create a gpt-image-2 prompt scaffold"
    }

    $symphonyHook = Join-Path $ProjectRoot ".agents\hooks\symphony.ps1"
    if (Test-Path -LiteralPath $symphonyHook) {
      $symphonyJson = powershell -NoProfile -ExecutionPolicy Bypass -File $symphonyHook -ProjectRoot $tempRoot -Json
      $symphonyData = $symphonyJson | ConvertFrom-Json
      $foundBatch = @($symphonyData.Batches | Where-Object { $_.Batch -eq "preflight-dragon" }).Count -eq 1
      if ($foundBatch) {
        Pass "mini-Symphony scans intake batch"
      } else {
        Fail "mini-Symphony did not report the intake batch"
      }

      powershell -NoProfile -ExecutionPolicy Bypass -File $symphonyHook -ProjectRoot $tempRoot -WriteReport | Out-Null
      $symphonyReport = Join-Path $tempRoot "output\SYMPHONY.md"
      if ((Test-Path -LiteralPath $symphonyReport) -and ((Get-Content -Raw -Encoding UTF8 -LiteralPath $symphonyReport) -match "preflight-dragon")) {
        Pass "mini-Symphony writes report"
      } else {
        Fail "mini-Symphony did not write output/SYMPHONY.md"
      }
    }
  } finally {
    $tempBase = [System.IO.Path]::GetTempPath()
    if ($tempRoot.StartsWith($tempBase, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $tempRoot)) {
      Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
  }
}

$secretPattern = "sk-[A-Za-z0-9_-]{20,}"
$files = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File -Force |
  Where-Object {
    $_.FullName -notmatch "\\output\\.*\\source\\" -and
    $_.Extension -in @(".md", ".html", ".json", ".js", ".ps1", ".yaml", ".yml")
  }

foreach ($file in $files) {
  $matches = Select-String -LiteralPath $file.FullName -Pattern $secretPattern -ErrorAction SilentlyContinue
  if ($matches) {
    Fail "possible API key pattern in $($file.FullName)"
  }
}

if ($failed) {
  throw "SpriteMake preflight failed"
}

Pass "SpriteMake preflight complete"


