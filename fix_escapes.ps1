Get-ChildItem corpus\docs\*.md | ForEach-Object {
    $path = $_.FullName
    $text = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
    $original = $text
    $text = $text -replace '\\([_\[\]#*()`\.\-])', '$1'
    if ($text -ne $original) {
        [System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding $false))
        Write-Host "FIXED: $($_.Name)"
    } else {
        Write-Host "CLEAN: $($_.Name)"
    }
}