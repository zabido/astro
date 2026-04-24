# A célkönyvtár meghatározása
$targetPath = "S:\15T1200"

# Megkeressük az összes 'LIGHT' nevű mappát a mappaszerkezetben
# A -Recurse kapcsoló benéz a subfolderekbe is
Get-ChildItem -Path $targetPath -Filter "LIGHT" -Directory -Recurse | ForEach-Object {
    
    # Új név meghatározása
    $newName = "lights"
    
    # Átnevezés végrehajtása
    Write-Host "Átnevezés folyamatban: $($_.FullName) -> $newName"
    Rename-Item -Path $_.FullName -NewName $newName
}

Write-Host "Kész! Minden 'LIGHT' mappa átnevezve 'lights'-ra." -ForegroundColor Green