param(
  [Parameter(Mandatory=$true)][string]$InputPath,
  [Parameter(Mandatory=$true)][string]$OutputPath,
  [int]$MaxWidth=1440,
  [int]$Quality=65
)

Add-Type -AssemblyName System.Drawing

if(!(Test-Path $InputPath)) { Write-Error "Source not found: $InputPath"; exit 1 }

$dir = Split-Path $OutputPath
if(!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

$img = [System.Drawing.Image]::FromFile($InputPath)
try {
  $w = [int]$img.Width
  $h = [int]$img.Height
  if($w -gt $MaxWidth) {
    $ratio = $MaxWidth / $w
    $newW = [int]$MaxWidth
    $newH = [int]([math]::Round($h * $ratio))
  } else {
    $newW = $w
    $newH = $h
  }
  $bmp = New-Object System.Drawing.Bitmap $newW, $newH
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode  = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
  $g.SmoothingMode      = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
  $g.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
  $g.DrawImage($img, 0, 0, $newW, $newH)
  $g.Dispose()

  $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq 'image/jpeg' }
  $ep = New-Object System.Drawing.Imaging.EncoderParameters 1
  $ep.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality), $Quality
  $bmp.Save($OutputPath, $codec, $ep)
  $bmp.Dispose()
  Write-Output "OK: $OutputPath"
}
finally {
  $img.Dispose()
}
