<#
.SYNOPSIS
Organizes Seestar astrophotography data by moving .fit files into a 'lights' folder
and deleting leftover .jpg files from *_sub directories.

.DESCRIPTION
This script recursively searches for folders ending in '_sub' under the specified
root path. For each matching folder:
1. It creates a 'lights' subdirectory if it doesn't exist.
2. It moves all .fit files into the 'lights' subdirectory.
3. It deletes all remaining .jpg files.
4. It calculates and reports the total size of the deleted .jpg files.

.PARAMETER RootPath
The starting directory for the search (e.g., 's:\SeestarS30 Messier Project\').

.NOTES
Requires PowerShell 5.1 or later. Run with appropriate permissions.
#>

# --- Configuration ---
# MANDATORY: Set the root directory where your project folders are located.
#$RootPath = "c:\Users\zabido\Astro\"
$RootPath = "s:\SeestarS30 Messier Project\"
# --- Script Variables ---
[long]$TotalDeletedSize = 0

# Function to convert bytes to a human-readable format (e.g., KB, MB, GB)
function Format-HumanReadableSize {
    param([long]$Bytes)

    if ($Bytes -eq 0) {
        return "0 Bytes"
    }

    $Units = @("Bytes", "KB", "MB", "GB", "TB", "PB", "EB")
    $i = 0
    $Size = $Bytes

    while ($Size -ge 1024 -and $i -lt $Units.Count - 1) {
        $Size /= 1024
        $i++
    }

    "{0:N2} {1}" -f $Size, $Units[$i]
}

Write-Host "--- Starting Seestar Data Organization ---"
Write-Host "Searching under: $RootPath"

# Check if the root path exists
if (-not (Test-Path -Path $RootPath -PathType Container)) {
    Write-Error "Error: Root path '$RootPath' does not exist. Please check the path and try again."
    exit 1
}

# 1. Iterate through all subfolders recursively and filter for those ending with '_sub'
$SubFolders = Get-ChildItem -Path $RootPath -Directory -Recurse | Where-Object { $_.Name -like "*_sub" }

if ($SubFolders.Count -eq 0) {
    Write-Host "No folders ending in '_sub' found. Script finished."
}
else {
    Write-Host "Found $($SubFolders.Count) target folders. Processing..."
    Write-Host ""

    foreach ($Folder in $SubFolders) {
        Write-Host "Processing folder: $($Folder.FullName)"

        # Define the target 'lights' folder path
        $LightsFolder = Join-Path -Path $Folder.FullName -ChildPath "lights"

        # 2. Create the 'lights' folder if it does not exist
        # Use -Force to ensure the directory is created, and Out-Null to suppress output
        if (-not (Test-Path $LightsFolder -PathType Container)) {
            Write-Host "  -> Creating lights directory: $LightsFolder" -ForegroundColor Yellow
            New-Item -Path $LightsFolder -ItemType Directory -Force | Out-Null
        } else {
            Write-Host "  -> lights directory already exists."
        }

        # 3. Move all .fit files to the 'lights' folder
        $FitFiles = Get-ChildItem -Path $Folder.FullName -Filter "*.fit" -File
        if ($FitFiles.Count -gt 0) {
            Write-Host "  -> Moving $($FitFiles.Count) .fit files to lights/..." -ForegroundColor Green
            $FitFiles | Move-Item -Destination $LightsFolder -Force -PassThru | Out-Null
        } else {
            Write-Host "  -> No .fit files found to move."
        }

        # 4. Delete remaining .jpg files and track size
        $JpgFiles = Get-ChildItem -Path $Folder.FullName -Filter "*.jpg" -File
        if ($JpgFiles.Count -gt 0) {
            Write-Host "  -> Deleting $($JpgFiles.Count) .jpg files..." -ForegroundColor Red
            
            # Iterate through .jpg files to calculate total size and delete them
            $JpgFiles | ForEach-Object {
                $TotalDeletedSize += $_.Length
                Remove-Item $_.FullName -Force
            }
        } else {
            Write-Host "  -> No .jpg files found to delete."
        }
        Write-Host ""
    }
}

# 5. Output the total data deleted in a human-readable format
$HumanSize = Format-HumanReadableSize -Bytes $TotalDeletedSize

Write-Host "=========================================================="
Write-Host "Process Complete."
Write-Host "Total space saved by deleting .jpg files: $HumanSize" -ForegroundColor Cyan
Write-Host "=========================================================="