param(
  [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,

  [string]$BatchId = "",

  [switch]$WriteReport,

  [switch]$Json,

  [switch]$IncludeLooseFolders
)

$ErrorActionPreference = "Stop"

function Get-TextOrEmpty([string]$Path) {
  if (Test-Path -LiteralPath $Path) {
    return Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
  }
  return ""
}

function Get-CountByPattern([string]$Path, [string]$Filter) {
  if (-not (Test-Path -LiteralPath $Path)) {
    return 0
  }

  return @(Get-ChildItem -LiteralPath $Path -Recurse -File -Filter $Filter -ErrorAction SilentlyContinue).Count
}

function Test-ContainsPattern([string]$Text, [string]$Pattern) {
  if ([string]::IsNullOrWhiteSpace($Text)) {
    return $false
  }
  return [Text.RegularExpressions.Regex]::IsMatch($Text, $Pattern, [Text.RegularExpressions.RegexOptions]::IgnoreCase)
}

function ConvertTo-RelativeDisplay([string]$Path, [string]$Root) {
  $rootFull = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
  $pathFull = [System.IO.Path]::GetFullPath($Path)

  if ($pathFull.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    return $pathFull.Substring($rootFull.Length).TrimStart('\', '/')
  }

  return $pathFull
}

function New-BatchStatus([System.IO.DirectoryInfo]$BatchDir, [string]$ProjectRoot) {
  $batchName = $BatchDir.Name
  $batchPath = $BatchDir.FullName
  $requiredDocs = @("BATCH.md", "REQUESTS.md", "PROMPT.md", "MANIFEST.md", "QA.md")
  $requiredDirs = @("prompts", "generated", "source", "manifests", "tools", "qa", "final")

  $missingDocs = @()
  foreach ($doc in $requiredDocs) {
    if (-not (Test-Path -LiteralPath (Join-Path $batchPath $doc))) {
      $missingDocs += $doc
    }
  }

  $missingDirs = @()
  foreach ($dir in $requiredDirs) {
    if (-not (Test-Path -LiteralPath (Join-Path $batchPath $dir))) {
      $missingDirs += "$dir/"
    }
  }

  $batchText = Get-TextOrEmpty (Join-Path $batchPath "BATCH.md")
  $requestsText = Get-TextOrEmpty (Join-Path $batchPath "REQUESTS.md")
  $promptText = Get-TextOrEmpty (Join-Path $batchPath "PROMPT.md")
  $manifestText = Get-TextOrEmpty (Join-Path $batchPath "MANIFEST.md")
  $qaText = Get-TextOrEmpty (Join-Path $batchPath "QA.md")
  $allText = @($batchText, $requestsText, $promptText, $manifestText, $qaText) -join "`n"

  $generatedDir = Join-Path $batchPath "generated"
  $finalDir = Join-Path $batchPath "final"
  $manifestsDir = Join-Path $batchPath "manifests"
  $toolsDir = Join-Path $batchPath "tools"
  $qaDir = Join-Path $batchPath "qa"
  $promptsDir = Join-Path $batchPath "prompts"

  $generatedPngCount = Get-CountByPattern $generatedDir "*.png"
  $finalPngCount = Get-CountByPattern $finalDir "*.png"
  $manifestJsonCount = Get-CountByPattern $manifestsDir "*.json"
  $toolHtmlCount = Get-CountByPattern $toolsDir "*.html"
  $qaArtifactCount = Get-CountByPattern $qaDir "*"
  $promptVariantCount = Get-CountByPattern $promptsDir "*.md"

  $hasGenerationTarget = Test-ContainsPattern $promptText "Required image model:\s*gpt-image-2"
  $hasGrid = Test-ContainsPattern $allText "(Grid columns|Grid:|grid columns|columns and rows|Cell size|cell size)"
  $hasAnchor = Test-ContainsPattern $allText "(Contact anchor|contact anchor|Anchor:|anchor:)"
  $hasBaseline = Test-ContainsPattern $allText "(Y-axis|Y baseline|baseline|source plane)"
  $hasTargetPath = Test-ContainsPattern $allText "(Target file path|Target path|target asset path|Target file path after QA|Target file path after integration)"
  $hasPrompt = -not [string]::IsNullOrWhiteSpace($promptText)
  $hasQaFail = Test-ContainsPattern $qaText "(\bFAIL\b|qa-failed|needs regeneration|needs repack|do not integrate|not integrate|repack-needed)"
  $hasQaPass = Test-ContainsPattern $qaText "(\bPASS\b|qa-passed|ready-for-game|QA passed|final candidate|copied-to-game)"
  $hasPlaceholders = Test-ContainsPattern $requestsText "(?m)(\bTBD\b|TODO|\{[A-Z0-9_ -]+\}|-\s*(Target file path|Final canvas size|Grid columns|Grid rows|Contact anchor|Y-axis baseline/source plane):\s*$)"

  $blockers = @()
  if ($missingDocs.Count -gt 0) { $blockers += "missing docs: $($missingDocs -join ', ')" }
  if ($missingDirs.Count -gt 0) { $blockers += "missing folders: $($missingDirs -join ', ')" }
  if ($hasPrompt -and -not $hasGenerationTarget) { $blockers += "PROMPT.md lacks required gpt-image-2 generation target" }
  if ($hasPrompt -and -not $hasGrid) { $blockers += "grid/cell contract is not explicit" }
  if ($hasPrompt -and -not $hasAnchor) { $blockers += "contact anchor is not explicit" }
  if ($hasPrompt -and -not $hasBaseline) { $blockers += "Y-axis baseline/source plane is not explicit" }
  if ($hasPrompt -and -not $hasTargetPath) { $blockers += "target asset path is not explicit" }
  if ($hasPlaceholders) { $blockers += "REQUESTS.md still contains TBD/TODO or blank runtime fields" }

  $state = "unknown"
  $nextAction = "Review the batch docs and decide the next production step."
  $priority = 5

  if ($missingDocs.Count -gt 0 -or $missingDirs.Count -gt 0) {
    $state = "needs-scaffold"
    $priority = 1
    $nextAction = "Create the standard batch docs/folders with .agents\hooks\new-batch.ps1 or fill the missing files manually."
  } elseif (-not $hasPrompt) {
    $state = "needs-prompt"
    $priority = 1
    $nextAction = "Create PROMPT.md with a copy-ready gpt-image-2 prompt and SpriteMake output contract."
  } elseif (-not $hasGenerationTarget) {
    $state = "needs-prompt-inject"
    $priority = 1
    $nextAction = ".agents\hooks\prompt-inject.ps1 -InputPath output\$batchName\PROMPT.md -OutputPath output\$batchName\PROMPT.md"
  } elseif (-not $hasGrid -or -not $hasAnchor -or -not $hasBaseline -or -not $hasTargetPath -or $hasPlaceholders) {
    $state = "needs-refine"
    $priority = 2
    $nextAction = "Refine REQUESTS.md and PROMPT.md with target path, grid/cell, contact anchor, and Y-axis baseline/source plane."
  } elseif ($generatedPngCount -eq 0 -and $finalPngCount -eq 0) {
    $state = "prompt-ready"
    $priority = 3
    $nextAction = "Use PROMPT.md with Codex direct image generation for keyless convenience, or with an external gpt-image-2 environment for strict model control; put received PNGs under generated/."
  } elseif ($generatedPngCount -gt 0 -and $finalPngCount -eq 0 -and $hasQaFail) {
    $state = "needs-regeneration"
    $priority = 2
    $nextAction = "Keep failed PNGs in generated/ and write regeneration or repack notes before producing a new attempt."
  } elseif ($generatedPngCount -gt 0 -and $finalPngCount -eq 0) {
    $state = "qa-needed"
    $priority = 2
    $nextAction = "Inspect generated PNG size, alpha, grid, per-cell bbox, anchor, baseline, manifest, and preview playback."
  } elseif ($finalPngCount -gt 0 -and $hasQaFail) {
    $state = "mixed-review"
    $priority = 2
    $nextAction = "Review QA.md before integration; final/ contains PNGs but QA also records failures."
  } elseif ($finalPngCount -gt 0 -and $hasQaPass) {
    $state = "final-candidate"
    $priority = 4
    $nextAction = "Human review: confirm QA.md and copy final assets to the game project only if the target path is correct."
  } elseif ($finalPngCount -gt 0) {
    $state = "final-review"
    $priority = 4
    $nextAction = "Final assets exist; add explicit QA pass notes before game integration."
  }

  [pscustomobject]@{
    Batch = $batchName
    State = $state
    Priority = $priority
    Path = ConvertTo-RelativeDisplay $batchPath $ProjectRoot
    MissingDocs = $missingDocs
    MissingFolders = $missingDirs
    GeneratedPng = $generatedPngCount
    FinalPng = $finalPngCount
    ManifestJson = $manifestJsonCount
    PreviewHtml = $toolHtmlCount
    QaArtifacts = $qaArtifactCount
    PromptVariants = $promptVariantCount
    HasGenerationTarget = $hasGenerationTarget
    HasGrid = $hasGrid
    HasAnchor = $hasAnchor
    HasBaseline = $hasBaseline
    HasTargetPath = $hasTargetPath
    HasQaFail = $hasQaFail
    HasQaPass = $hasQaPass
    Blockers = $blockers
    NextAction = $nextAction
  }
}

function Write-SymphonyReport([object[]]$Statuses, [string]$ProjectRoot) {
  $outputRoot = Join-Path $ProjectRoot "output"
  New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

  $reportPath = Join-Path $outputRoot "SYMPHONY.md"
  $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
  $lines = @(
    '# SpriteMake Mini-Symphony Status',
    '',
    ('- Generated at: ' + $stamp),
    '- Control plane: `output/*` batch folders',
    '- Workflow policy: `WORKFLOW.md` and `AGENTS.md`',
    '- This report does not call image APIs and does not move files into `final/`.',
    '',
    '## Board',
    '',
    '| Batch | State | Generated PNG | Final PNG | Next Action |',
    '| --- | --- | ---: | ---: | --- |'
  )

  foreach ($status in $Statuses) {
    $next = ($status.NextAction -replace "\|", "/")
    $lines += "| ``$($status.Batch)`` | ``$($status.State)`` | $($status.GeneratedPng) | $($status.FinalPng) | $next |"
  }

  $lines += ''
  $lines += '## Details'
  $lines += ''

  foreach ($status in $Statuses) {
    $lines += "### $($status.Batch)"
    $lines += ''
    $lines += "- State: ``$($status.State)``"
    $lines += "- Path: ``$($status.Path)``"
    $lines += "- Generated PNG: $($status.GeneratedPng)"
    $lines += "- Final PNG: $($status.FinalPng)"
    $lines += "- Manifest JSON: $($status.ManifestJson)"
    $lines += "- Preview HTML: $($status.PreviewHtml)"
    $lines += "- QA artifacts: $($status.QaArtifacts)"
    $lines += "- Prompt variants: $($status.PromptVariants)"
    $lines += "- Next action: $($status.NextAction)"

    if ($status.Blockers.Count -gt 0) {
      $lines += '- Blockers:'
      foreach ($blocker in $status.Blockers) {
        $lines += "  - $blocker"
      }
    } else {
      $lines += '- Blockers: none detected by static scan'
    }

    $lines += ''
  }

  Set-Content -LiteralPath $reportPath -Encoding UTF8 -Value ($lines -join [Environment]::NewLine)
  return $reportPath
}

$outputRoot = Join-Path $ProjectRoot "output"
if (-not (Test-Path -LiteralPath $outputRoot)) {
  throw "SpriteMake output folder not found: $outputRoot"
}

$batchDirs = Get-ChildItem -LiteralPath $outputRoot -Directory -ErrorAction SilentlyContinue

if (-not [string]::IsNullOrWhiteSpace($BatchId)) {
  $batchDirs = @($batchDirs | Where-Object { $_.Name -eq $BatchId })
}

$batchDirs = @($batchDirs | Where-Object {
  if ($IncludeLooseFolders) {
    $true
  } else {
    $path = $_.FullName
    (
      (Test-Path -LiteralPath (Join-Path $path "BATCH.md")) -or
      (Test-Path -LiteralPath (Join-Path $path "REQUESTS.md")) -or
      (Test-Path -LiteralPath (Join-Path $path "PROMPT.md")) -or
      (Test-Path -LiteralPath (Join-Path $path "QA.md"))
    )
  }
})

$statuses = @($batchDirs | ForEach-Object { New-BatchStatus $_ $ProjectRoot } | Sort-Object Priority, Batch)

if ($WriteReport) {
  $report = Write-SymphonyReport $statuses $ProjectRoot
}

if ($Json) {
  $reportDisplay = $null
  if ($WriteReport) {
    $reportDisplay = ConvertTo-RelativeDisplay $report $ProjectRoot
  }

  $payload = [pscustomobject]@{
    ProjectRoot = $ProjectRoot
    ReportPath = $reportDisplay
    Batches = $statuses
  }
  $payload | ConvertTo-Json -Depth 8
  return
}

Write-Host "SpriteMake mini-Symphony board"
Write-Host "- Project: $ProjectRoot"
Write-Host "- Batches: $($statuses.Count)"
if ($WriteReport) {
  Write-Host "- Report: $(ConvertTo-RelativeDisplay $report $ProjectRoot)"
}
Write-Host ""

if ($statuses.Count -eq 0) {
  Write-Host "No standard SpriteMake batches found under output/."
  Write-Host "Use -IncludeLooseFolders to include non-standard output folders."
  return
}

$statuses |
  Select-Object Batch, State, GeneratedPng, FinalPng, ManifestJson, PreviewHtml, NextAction |
  Format-Table -Wrap -AutoSize
