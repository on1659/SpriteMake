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

function Get-ObjectPropertyValue([object]$Object, [string]$Name) {
  if ($null -eq $Object) {
    return $null
  }

  $property = $Object.PSObject.Properties[$Name]
  if ($null -ne $property) {
    return $property.Value
  }

  return $null
}

function Get-NestedObjectPropertyValue([object]$Object, [string[]]$Names) {
  $current = $Object
  foreach ($name in $Names) {
    $current = Get-ObjectPropertyValue $current $name
    if ($null -eq $current) {
      return $null
    }
  }

  return $current
}

function ConvertTo-QaOutcome([object]$Value) {
  if ($Value -is [bool]) {
    if ($Value) { return "pass" }
    return "fail"
  }

  if ($null -eq $Value) {
    return "pending"
  }

  $normalized = $Value.ToString().Trim().ToLowerInvariant()
  if ($normalized -in @("pass", "passed", "ok", "approved", "eligible", "ready")) {
    return "pass"
  }
  if ($normalized -in @("fail", "failed", "rejected", "ineligible", "blocked")) {
    return "fail"
  }

  return "pending"
}

function Get-CanonicalAssetStatusEntries([string]$BatchPath, [string]$QaDir) {
  # Canonical runner status files. A single status has assetId at the root; a
  # plural file may be an array or wrap entries in assets/assetStatuses/items.
  $candidatePaths = @(
    (Join-Path $QaDir "asset-status.json"),
    (Join-Path $QaDir "asset-statuses.json"),
    (Join-Path $BatchPath "asset-status.json"),
    (Join-Path $BatchPath "asset-statuses.json")
  ) | Select-Object -Unique

  $entries = @()
  $files = @()
  foreach ($path in $candidatePaths) {
    if (-not (Test-Path -LiteralPath $path)) {
      continue
    }

    try {
      $document = Get-Content -Raw -Encoding UTF8 -LiteralPath $path | ConvertFrom-Json
    } catch {
      Write-Warning "Ignoring invalid structured asset status: $(ConvertTo-RelativeDisplay $path $BatchPath)"
      continue
    }

    $items = @()
    if ($document -is [System.Array]) {
      $items = @($document)
    } else {
      foreach ($containerName in @("assets", "assetStatuses", "items")) {
        $container = Get-ObjectPropertyValue $document $containerName
        if ($null -ne $container) {
          $items = @($container)
          break
        }
      }
      if ($items.Count -eq 0) {
        $items = @($document)
      }
    }

    $validItems = @($items | Where-Object {
      $null -ne (Get-ObjectPropertyValue $_ "assetId") -or $null -ne (Get-ObjectPropertyValue $_ "qa")
    })
    if ($validItems.Count -gt 0) {
      $files += $path
      foreach ($item in $validItems) {
        $entries += [pscustomobject]@{
          Path = $path
          Entry = $item
        }
      }
    }
  }

  [pscustomobject]@{
    Entries = $entries
    Files = $files
  }
}

function Get-CanonicalAssetStatusSummary([object[]]$StatusEntries) {
  $passed = 0
  $failed = 0
  $pending = 0
  $eligible = 0
  $assets = @()

  foreach ($statusEntry in $StatusEntries) {
    $entry = $statusEntry.Entry
    $assetId = Get-ObjectPropertyValue $entry "assetId"
    if ([string]::IsNullOrWhiteSpace($assetId)) {
      $assetId = "unnamed asset"
    }

    $qaOutcome = ConvertTo-QaOutcome (Get-NestedObjectPropertyValue $entry @("qa", "status"))
    $reviews = Get-ObjectPropertyValue $entry "reviews"
    $reviewOutcome = "pass"
    foreach ($reviewName in @("filenameContent", "style", "placement", "motion")) {
      $review = Get-ObjectPropertyValue $reviews $reviewName
      if ($null -eq $review) {
        continue
      }

      $required = Get-ObjectPropertyValue $review "required"
      if ($required -is [bool] -and -not $required) {
        continue
      }

      $outcome = ConvertTo-QaOutcome (Get-ObjectPropertyValue $review "status")
      if ($outcome -eq "fail") {
        $reviewOutcome = "fail"
      } elseif ($outcome -eq "pending" -and $reviewOutcome -ne "fail") {
        $reviewOutcome = "pending"
      }
    }

    $promotion = Get-ObjectPropertyValue $entry "promotion"
    $promotionEligible = Get-ObjectPropertyValue $promotion "eligible"
    $promotionStatus = Get-ObjectPropertyValue $promotion "status"
    # `eligible: false` is normal while a candidate awaits review. Treat it as
    # failure only when the gate explicitly says blocked/rejected; otherwise
    # the dashboard should request review instead of regeneration.
    if ($promotionEligible -is [bool] -and $promotionEligible) {
      $promotionOutcome = "pass"
    } elseif ((ConvertTo-QaOutcome $promotionStatus) -eq "fail") {
      $promotionOutcome = "fail"
    } elseif ((ConvertTo-QaOutcome $promotionStatus) -eq "pass") {
      $promotionOutcome = "pass"
    } else {
      $promotionOutcome = "pending"
    }

    $outcome = "pending"
    if ($qaOutcome -eq "fail" -or $reviewOutcome -eq "fail") {
      $outcome = "fail"
      $failed++
    } elseif ($qaOutcome -ne "pass" -or $reviewOutcome -ne "pass") {
      # The gate records a blocked promotion for missing approvals too. A
      # pending QA/review remains review work, not a regeneration failure.
      $pending++
    } elseif ($promotionOutcome -eq "pass") {
      $outcome = "pass"
      $passed++
      $eligible++
    } elseif ($promotionOutcome -eq "fail") {
      $outcome = "fail"
      $failed++
    } else {
      $pending++
    }

    $assets += [pscustomobject]@{
      AssetId = $assetId
      Outcome = $outcome
      Qa = $qaOutcome
      Reviews = $reviewOutcome
      Promotion = $promotionOutcome
      Path = $statusEntry.Path
    }
  }

  [pscustomobject]@{
    Count = $StatusEntries.Count
    Passed = $passed
    Failed = $failed
    Pending = $pending
    Eligible = $eligible
    Assets = $assets
  }
}

function Get-StructuredQaReportSummary([string]$QaDir, [int]$FinalPngCount) {
  $records = @()
  if (-not (Test-Path -LiteralPath $QaDir)) {
    return [pscustomobject]@{ Count = 0; Passed = 0; Failed = 0; Pending = 0; Selected = @(); Files = @() }
  }

  foreach ($path in @(Get-ChildItem -LiteralPath $QaDir -File -Filter "*.json" -ErrorAction SilentlyContinue)) {
    if ($path.Name -in @("asset-status.json", "asset-statuses.json")) {
      continue
    }

    try {
      $document = Get-Content -Raw -Encoding UTF8 -LiteralPath $path.FullName | ConvertFrom-Json
    } catch {
      continue
    }

    $passValue = Get-ObjectPropertyValue $document "pass"
    if ($null -eq $passValue) {
      $passValue = Get-NestedObjectPropertyValue $document @("qa", "status")
    }
    if ($null -eq $passValue) {
      continue
    }

    $outputPath = Get-ObjectPropertyValue $document "output"
    $isFinalOutput = $false
    if ($null -ne $outputPath) {
      $isFinalOutput = $outputPath.ToString() -match "(^|[\\/])final([\\/]|$)"
    }
    $records += [pscustomobject]@{
      Path = $path.FullName
      AssetId = (Get-ObjectPropertyValue $document "asset")
      Outcome = (ConvertTo-QaOutcome $passValue)
      IsFinalOutput = $isFinalOutput
    }
  }

  # Once final assets exist, a report for an obsolete generated attempt must
  # not keep the whole batch in failure. Prefer reports that explicitly attest
  # to files in final/; this fixes historical attempts such as Track B's first
  # beaver-dam repack without hiding a failure of the final candidate.
  $finalRecords = @($records | Where-Object { $_.IsFinalOutput })
  $selected = if ($FinalPngCount -gt 0 -and $finalRecords.Count -gt 0) { $finalRecords } else { $records }
  $passed = @($selected | Where-Object { $_.Outcome -eq "pass" }).Count
  $failed = @($selected | Where-Object { $_.Outcome -eq "fail" }).Count
  $pending = @($selected | Where-Object { $_.Outcome -eq "pending" }).Count

  [pscustomobject]@{
    Count = $selected.Count
    Passed = $passed
    Failed = $failed
    Pending = $pending
    Selected = $selected
    Files = @($selected | ForEach-Object { $_.Path })
  }
}

function Get-LegacyQaSignals([string]$QaText) {
  # QA.md remains a backwards-compatible fallback only. Ignore contract/sample
  # lines such as "PASS/FAIL" so a checklist example cannot become a failure.
  $actualLines = @($QaText -split "`r?`n" | Where-Object { $_ -notmatch "(?i)PASS\s*/\s*FAIL" })
  $actualText = $actualLines -join "`n"
  [pscustomobject]@{
    HasFail = Test-ContainsPattern $actualText "(?im)(->|→|:|\bstatus\s*=\s*)\s*FAIL\b|\bqa-failed\b|\bneeds (regeneration|repack)\s+[1-9]|\bdo not integrate\b|\bnot integrate\b"
    HasPass = Test-ContainsPattern $actualText "(?im)(->|→|:|\bstatus\s*=\s*)\s*PASS\b|\bqa-passed\b|\bready-for-game\b|\bfinal candidate\b|\bcopied-to-game\b"
  }
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
  $canonicalStatuses = Get-CanonicalAssetStatusEntries $batchPath $qaDir
  $canonicalSummary = Get-CanonicalAssetStatusSummary $canonicalStatuses.Entries
  $reportSummary = Get-StructuredQaReportSummary $qaDir $finalPngCount
  $legacyQa = Get-LegacyQaSignals $qaText

  # Structured asset statuses are authoritative. Generic JSON QA reports are
  # the compatibility bridge for batches created before the runner contract.
  # Only batches with neither use the legacy QA.md text fallback.
  $qaStatusSource = "none"
  $qaStatusFiles = @()
  $qaStatusCount = 0
  $qaPassedCount = 0
  $qaFailedCount = 0
  $qaPendingCount = 0
  $qaEligibleCount = 0
  if ($canonicalSummary.Count -gt 0) {
    $qaStatusSource = "asset-status"
    $qaStatusFiles = $canonicalStatuses.Files
    $qaStatusCount = $canonicalSummary.Count
    $qaPassedCount = $canonicalSummary.Passed
    $qaFailedCount = $canonicalSummary.Failed
    $qaPendingCount = $canonicalSummary.Pending
    $qaEligibleCount = $canonicalSummary.Eligible
  } elseif ($reportSummary.Count -gt 0) {
    $qaStatusSource = "qa-report"
    $qaStatusFiles = $reportSummary.Files
    $qaStatusCount = $reportSummary.Count
    $qaPassedCount = $reportSummary.Passed
    $qaFailedCount = $reportSummary.Failed
    $qaPendingCount = $reportSummary.Pending
    # Legacy reports do not contain an explicit promotion gate. Passing reports
    # make a batch a human-review candidate, never an automatic promotion.
    $qaEligibleCount = $reportSummary.Passed
  } elseif (-not [string]::IsNullOrWhiteSpace($qaText)) {
    $qaStatusSource = "legacy-qa-md"
    if ($legacyQa.HasPass) { $qaPassedCount = 1 }
    if ($legacyQa.HasFail) { $qaFailedCount = 1 }
  }

  $hasQaFail = $qaFailedCount -gt 0
  $hasQaPass = $qaPassedCount -gt 0 -and -not $hasQaFail
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
  # Documentation is a creation-time gate. Once a batch already contains
  # reviewed final assets, missing legacy prompt wording is documentation debt
  # rather than a reason to hide the real final-review state.
  } elseif (-not $hasPrompt -and $finalPngCount -eq 0) {
    $state = "needs-prompt"
    $priority = 1
    $nextAction = "Create PROMPT.md with a copy-ready gpt-image-2 prompt and SpriteMake output contract."
  } elseif (-not $hasGenerationTarget -and $finalPngCount -eq 0) {
    $state = "needs-prompt-inject"
    $priority = 1
    $nextAction = ".agents\hooks\prompt-inject.ps1 -InputPath output\$batchName\PROMPT.md -OutputPath output\$batchName\PROMPT.md"
  } elseif ($finalPngCount -eq 0 -and (-not $hasGrid -or -not $hasAnchor -or -not $hasBaseline -or -not $hasTargetPath -or $hasPlaceholders)) {
    $state = "needs-refine"
    $priority = 2
    $nextAction = "Refine REQUESTS.md and PROMPT.md with target path, grid/cell, contact anchor, and Y-axis baseline/source plane."
  } elseif ($finalPngCount -eq 0 -and $hasQaFail) {
    $state = "needs-regeneration"
    $priority = 2
    $nextAction = "Keep failed PNGs in generated/ and write regeneration or repack notes before producing a new attempt."
  } elseif ($finalPngCount -eq 0 -and $qaStatusSource -eq "asset-status" -and $qaStatusCount -gt 0 -and $qaEligibleCount -eq $qaStatusCount) {
    $state = "final-review"
    $priority = 3
    $nextAction = "All structured checks are promotion-eligible; run the local asset gate to atomically promote the approved candidate into final/."
  } elseif ($generatedPngCount -eq 0 -and $finalPngCount -eq 0) {
    $state = "prompt-ready"
    $priority = 3
    $nextAction = "Use PROMPT.md with Codex direct image generation for keyless convenience, or with an external gpt-image-2 environment for strict model control; put received PNGs under generated/."
  } elseif ($generatedPngCount -gt 0 -and $finalPngCount -eq 0) {
    $state = "qa-needed"
    $priority = 2
    $nextAction = "Inspect generated PNG size, alpha, grid, per-cell bbox, anchor, baseline, manifest, and preview playback."
  } elseif ($finalPngCount -gt 0 -and $hasQaFail) {
    $state = "mixed-review"
    $priority = 2
    $nextAction = "Review the structured QA status before integration; final/ contains PNGs but the current candidate has failed checks."
  } elseif ($finalPngCount -gt 0 -and $qaStatusSource -eq "asset-status" -and ($qaPendingCount -gt 0 -or $qaEligibleCount -lt $qaStatusCount)) {
    $state = "final-review"
    $priority = 4
    $nextAction = "Complete the required human reviews and run asset_gate.py validate to refresh promotion eligibility before final approval."
  } elseif ($finalPngCount -gt 0 -and $hasQaPass) {
    $state = "final-candidate"
    $priority = 4
    $nextAction = "Human review: confirm the structured QA status and copy final assets to the game project only if the target path is correct."
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
    QaStatusSource = $qaStatusSource
    QaStatusFiles = @($qaStatusFiles | ForEach-Object { ConvertTo-RelativeDisplay $_ $ProjectRoot })
    QaStatusCount = $qaStatusCount
    QaPassedCount = $qaPassedCount
    QaFailedCount = $qaFailedCount
    QaPendingCount = $qaPendingCount
    QaEligibleCount = $qaEligibleCount
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
    '| Batch | State | QA source | QA pass/fail/pending | Generated PNG | Final PNG | Next Action |',
    '| --- | --- | --- | --- | ---: | ---: | --- |'
  )

  foreach ($status in $Statuses) {
    $next = ($status.NextAction -replace "\|", "/")
    $qaSummary = "$($status.QaPassedCount)/$($status.QaFailedCount)/$($status.QaPendingCount)"
    $lines += "| ``$($status.Batch)`` | ``$($status.State)`` | ``$($status.QaStatusSource)`` | $qaSummary | $($status.GeneratedPng) | $($status.FinalPng) | $next |"
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
    $lines += "- QA status source: ``$($status.QaStatusSource)``"
    $lines += "- QA status totals: $($status.QaPassedCount) pass / $($status.QaFailedCount) fail / $($status.QaPendingCount) pending; $($status.QaEligibleCount) promotion-eligible"
    if ($status.QaStatusFiles.Count -gt 0) {
      $lines += '- QA status files:'
      foreach ($qaFile in $status.QaStatusFiles) {
        $lines += "  - ``$qaFile``"
      }
    }
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
  Select-Object Batch, State, QaStatusSource, QaPassedCount, QaFailedCount, QaPendingCount, GeneratedPng, FinalPng, ManifestJson, PreviewHtml, NextAction |
  Format-Table -Wrap -AutoSize
