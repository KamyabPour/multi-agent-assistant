param(
    [string]$AssistantName = "Assistant",
    [string]$OutputDir = "$env:USERPROFILE\.assistant"
)

Add-Type -AssemblyName System.Drawing

$initial = $AssistantName.Substring(0,1).ToUpper()
$size = 256

# Create 256x256 transparent bitmap
$bmp = New-Object System.Drawing.Bitmap($size, $size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::Transparent)

# Draw coloured circle — blue gradient feel
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 50, 120, 255))
$g.FillEllipse($brush, 4, 4, $size - 8, $size - 8)

# Subtle inner highlight
$highlightBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(40, 255, 255, 255))
$g.FillEllipse($highlightBrush, 20, 20, $size - 80, $size - 120)

# Draw the assistant initial letter in white
$font = New-Object System.Drawing.Font("Segoe UI", 108, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$sf = New-Object System.Drawing.StringFormat
$sf.Alignment = [System.Drawing.StringAlignment]::Center
$sf.LineAlignment = [System.Drawing.StringAlignment]::Center
$rect = New-Object System.Drawing.RectangleF(0, 8, $size, $size)
$g.DrawString($initial, $font, $textBrush, $rect, $sf)
$g.Dispose()

# Encode bitmap as PNG bytes (ICO can embed PNG for 256x256)
$ms = New-Object System.IO.MemoryStream
$bmp.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
$pngBytes = $ms.ToArray()
$ms.Close()
$bmp.Dispose()

# Write ICO file wrapping the PNG
# ICO format: ICONDIR (6 bytes) + ICONDIRENTRY (16 bytes) + PNG data
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir | Out-Null }

$iconPath = Join-Path $OutputDir "$AssistantName.ico"
$stream = [System.IO.File]::Create($iconPath)
$writer = New-Object System.IO.BinaryWriter($stream)

# ICONDIR header
$writer.Write([uint16]0)                        # reserved
$writer.Write([uint16]1)                        # type = 1 (icon)
$writer.Write([uint16]1)                        # image count

# ICONDIRENTRY
$writer.Write([byte]0)                          # width  (0 = 256)
$writer.Write([byte]0)                          # height (0 = 256)
$writer.Write([byte]0)                          # color count (0 = no palette)
$writer.Write([byte]0)                          # reserved
$writer.Write([uint16]1)                        # planes
$writer.Write([uint16]32)                       # bits per pixel
$writer.Write([uint32]$pngBytes.Length)         # image data size
$writer.Write([uint32]22)                       # offset to image data (6+16=22)

# PNG image data
$writer.Write($pngBytes)
$writer.Close()
$stream.Close()

Write-Host "Icon created: $iconPath"
exit 0
