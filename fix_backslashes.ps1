Get-ChildItem corpus\docs\*.md | ForEach-Object {
    $path = $_.FullName
    $bytes = [System.IO.File]::ReadAllBytes($path)
    if ($bytes.Length -lt 3) { Write-Host "SKIP (too short): $($_.Name)"; return }
    if ($bytes[0] -eq 92 -and $bytes[1] -eq 45 -and $bytes[2] -eq 45) {
        [System.IO.File]::WriteAllBytes($path, $bytes[1..($bytes.Length-1)])
        Write-Host "FIXED: $($_.Name)"
    } else {
        Write-Host "CLEAN: $($_.Name)"
    }
}
