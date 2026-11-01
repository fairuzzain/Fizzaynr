<#
.SYNOPSIS
  Generate one image with OpenAI Codex CLI (ChatGPT login, image_gen tool) and save it as a verified PNG.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File codex-image.ps1 -Prompt "neon city at night" -Out "C:\proj\images\city.png" -Aspect 16:9 -Width 1920
  powershell -ExecutionPolicy Bypass -File codex-image.ps1 -Prompt "same character, waving" -Out "C:\proj\images\wave.png" -Aspect 9:16 -Reference "C:\proj\images\char.png"
#>
[CmdletBinding()]
param(
    [string]$Prompt = "",
    [string]$PromptFile = "",      # UTF-8 text file with the prompt (used by the MCP server; avoids quoting issues)
    [Parameter(Mandatory = $true)][string]$Out,
    [string]$Preview = "",         # optional path for a small JPEG preview (max 1024 px side)
    [string]$Aspect = "",          # e.g. 16:9, 9:16, 1:1, 4:5 - centre-cropped to this exact ratio
    [int]$Width = 0,               # optional final width in px (height follows the ratio)
    [string[]]$Reference = @(),    # optional reference / source images (image-to-image, style or character reference)
    [string]$Pad = "",             # "auto" (sheet's own corner colour) or a colour like "#00FF00": fit the whole image and pad to -Aspect instead of cropping (key-colour sheets)
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

if ($PromptFile) { $Prompt = [IO.File]::ReadAllText($PromptFile, [Text.Encoding]::UTF8).Trim() }
if ([string]::IsNullOrWhiteSpace($Prompt)) { throw "Give -Prompt or -PromptFile." }
$Reference = @($Reference | ForEach-Object { $_ -split '\|' } | Where-Object { $_ })

$codexBin = Join-Path $env:LOCALAPPDATA "Programs\OpenAI\Codex\bin"
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { $env:Path = "$codexBin;$env:Path" }
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) { throw "Codex CLI not found. Install: irm https://chatgpt.com/codex/install.ps1 | iex" }

$Out = [IO.Path]::GetFullPath($Out)
if ([IO.Path]::GetExtension($Out) -ne ".png") { $Out = [IO.Path]::ChangeExtension($Out, ".png") }
if ((Test-Path -LiteralPath $Out) -and -not $Overwrite) {
    $base = [IO.Path]::Combine([IO.Path]::GetDirectoryName($Out), [IO.Path]::GetFileNameWithoutExtension($Out))
    $n = 2
    while (Test-Path -LiteralPath "$base-$n.png") { $n++ }
    $Out = "$base-$n.png"
}
New-Item -ItemType Directory -Force -Path ([IO.Path]::GetDirectoryName($Out)) | Out-Null

# Codex works in an isolated temp folder; only that folder is writable for it.
$work = Join-Path $env:TEMP ("codex-image\" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $work | Out-Null
$raw = Join-Path $work "out.png"

$orientation = "the closest supported size"
if ($Aspect -match '^\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)\s*$') {
    $r = [double]$Matches[1] / [double]$Matches[2]
    $orientation = if ($r -gt 1.1) { "a landscape size" } elseif ($r -lt 0.9) { "a portrait size" } else { "a square size" }
    if ($Pad) { $orientation += " (final target aspect ratio $Aspect; the image will be padded to that ratio with its background colour, never cropped)" }
    else { $orientation += " (final target aspect ratio $Aspect; keep important content away from the edges because it will be centre-cropped)" }
}

$imageArgs = @()
$refNote = ""
if ($Reference.Count -gt 0) {
    foreach ($ref in $Reference) {
        if (-not (Test-Path -LiteralPath $ref)) { throw "Reference image not found: $ref" }
        $imageArgs += @("-i", (Resolve-Path -LiteralPath $ref).Path)
    }
    $refNote = " The attached image(s) are reference images: follow them for subject, character identity, style and composition as the description asks (edit them if the description asks for an edit)."
}

$instruction = "Use your image generation tool to create this image: $Prompt.$refNote Use $orientation. " +
    "Do not crop, resize or otherwise modify the generated image yourself. " +
    "Save it unmodified as a PNG file at: $raw (copy it from wherever the tool writes it; convert to PNG only if it is not PNG). " +
    "Do not create or change any other files. Reply with only the saved path."

$log = Join-Path $work "codex.log"
# The prompt goes in on stdin: `-i` takes several files and would swallow a positional prompt.
$codexArgs = @("exec", "--skip-git-repo-check", "--ephemeral", "-s", "workspace-write", "-C", $work) + $imageArgs
$OutputEncoding = New-Object System.Text.UTF8Encoding $false
$ErrorActionPreference = "Continue"   # Codex writes progress to stderr; PS 5.1 would treat it as fatal
$instruction | & codex @codexArgs 2>&1 | Out-File -FilePath $log -Encoding utf8
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $raw)) {
    $tail = (Get-Content $log -Tail 30 | Where-Object { $_ -notmatch "rmcp::transport" }) -join "`n"
    throw "Codex did not produce an image. Last output:`n$tail"
}

# Normalise: centre-crop to the exact aspect ratio, optional resize, always save as real PNG.
$src = [System.Drawing.Image]::FromFile($raw)
try {
    $sw = $src.Width; $sh = $src.Height
    $cx = 0; $cy = 0; $cw = $sw; $ch = $sh
    $fw = $sw; $fh = $sh                      # canvas size before resize (differs from crop size only when padding)
    if ($Aspect -match '^\s*(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)\s*$') {
        $target = [double]$Matches[1] / [double]$Matches[2]
        if ($Pad) {
            if (($sw / $sh) -gt $target) { $fh = [int][Math]::Round($sw / $target) } else { $fw = [int][Math]::Round($sh * $target) }
        } elseif (($sw / $sh) -gt $target) { $cw = [int][Math]::Round($sh * $target); $cx = [int](($sw - $cw) / 2); $fw = $cw }
        else { $ch = [int][Math]::Round($sw / $target); $cy = [int](($sh - $ch) / 2); $fh = $ch }
    }
    $dw = $fw; $dh = $fh
    if ($Width -gt 0) { $dw = $Width; $dh = [int][Math]::Round($Width * $fh / $fw) }
    $k = $dw / $fw
    $iw = [int][Math]::Round($cw * $k); $ih = [int][Math]::Round($ch * $k)
    $bmp = New-Object System.Drawing.Bitmap $dw, $dh
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    try {
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
        if ($Pad -eq "auto") { $g.Clear(([System.Drawing.Bitmap]$src).GetPixel(2, 2)) }   # the sheet's own background colour
        elseif ($Pad) { $g.Clear([System.Drawing.ColorTranslator]::FromHtml($Pad)) }
        $g.DrawImage($src, (New-Object System.Drawing.Rectangle ([int](($dw - $iw) / 2)), ([int](($dh - $ih) / 2)), $iw, $ih), $cx, $cy, $cw, $ch, [System.Drawing.GraphicsUnit]::Pixel)
        $bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
    } finally { $g.Dispose(); $bmp.Dispose() }
} finally { $src.Dispose() }

# Verify the PNG signature and dimensions of the saved file.
$bytes = [IO.File]::ReadAllBytes($Out)
$sig = ($bytes[0..7] | ForEach-Object { $_.ToString("X2") }) -join ""
if ($sig -ne "89504E470D0A1A0A") { throw "Saved file is not a valid PNG: $Out" }
$w = ($bytes[16] * 16777216) + ($bytes[17] * 65536) + ($bytes[18] * 256) + $bytes[19]
$h = ($bytes[20] * 16777216) + ($bytes[21] * 65536) + ($bytes[22] * 256) + $bytes[23]

if ($Preview) {
    $full = [System.Drawing.Image]::FromFile($Out)
    try {
        $scale = [Math]::Min(1.0, 1024.0 / [Math]::Max($full.Width, $full.Height))
        $pw = [int]($full.Width * $scale); $ph = [int]($full.Height * $scale)
        $pv = New-Object System.Drawing.Bitmap $pw, $ph
        $pg = [System.Drawing.Graphics]::FromImage($pv)
        try {
            $pg.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $pg.DrawImage($full, 0, 0, $pw, $ph)
            $jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
            $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
            $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), 85L
            $pv.Save($Preview, $jpeg, $ep)
        } finally { $pg.Dispose(); $pv.Dispose() }
    } finally { $full.Dispose() }
}

Remove-Item -LiteralPath $work -Recurse -Force -ErrorAction SilentlyContinue
[pscustomobject]@{ Path = $Out; Width = $w; Height = $h; Bytes = $bytes.Length; Source = "${sw}x${sh}" } | ConvertTo-Json -Compress
