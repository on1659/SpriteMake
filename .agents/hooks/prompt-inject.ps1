param(
  [string]$Prompt = "",
  [string]$InputPath = "",
  [string]$OutputPath = "",
  [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

$generationTarget = @"
Generation Target:
- Provider: OpenAI Images API
- Required image model: gpt-image-2
- Use gpt-image-2 for image generation or editing.
- Do not silently substitute another image model.
- SpriteMake does not store API keys or call the API directly; this model requirement is guaranteed only by a strict external generation step.
- Codex direct keyless generation may be used for convenience, but its model is not forced or verified as gpt-image-2.
"@

function Get-InputPrompt {
  if ($InputPath) {
    return Get-Content -Raw -LiteralPath $InputPath
  }

  if ($Prompt) {
    return $Prompt
  }

  if (-not [Console]::IsInputRedirected) {
    return ""
  }

  return [Console]::In.ReadToEnd()
}

function Test-HasGenerationTarget([string]$Text) {
  return $Text -match "Generation Target:" -and $Text -match "Required image model:\s*gpt-image-2"
}

function Add-GenerationTarget([string]$Text) {
  if (Test-HasGenerationTarget $Text) {
    return $Text
  }

  if ([string]::IsNullOrWhiteSpace($Text)) {
    return $generationTarget.Trim()
  }

  return ($generationTarget.TrimEnd() + "`r`n`r`n" + $Text.TrimStart())
}

$inputPrompt = Get-InputPrompt

if ($CheckOnly) {
  if (Test-HasGenerationTarget $inputPrompt) {
    Write-Host "[ OK ] prompt already contains gpt-image-2 generation target"
    exit 0
  }

  Write-Host "[FAIL] prompt is missing gpt-image-2 generation target" -ForegroundColor Red
  exit 1
}

$result = Add-GenerationTarget $inputPrompt

if ($OutputPath) {
  $dir = Split-Path -Parent $OutputPath
  if ($dir) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
  }
  Set-Content -LiteralPath $OutputPath -Value $result -Encoding UTF8
} else {
  Write-Output $result
}


