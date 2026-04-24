<#
.SYNOPSIS
Batch processes .fit files using GraXpert CLI for default Background Extraction (BE).

.DESCRIPTION
This script uses the proven execution flow and argument structure from the user's 
working script and adapts the parameters for a standard background extraction. 
Saved with UTF-8 to prevent encoding issues.

.NOTES
Requires GraXpert to be installed and working with CLI mode.
#>

# --- Configuration Variables ---
$GraXpertPath         = "C:\Users\zabido\AppData\Local\Programs\GraXpert\GraXpert.exe"
$SourceDirectory      = "c:\Users\zabido\Astro\SeestarS30 Messier Project\cc\"
$DestinationDirectory = "c:\Users\zabido\Astro\SeestarS30 Messier Project\gxb\"
$MonitorIntervalSeconds = 5 # How often to check the process status

# Required fixed parameters for GraXpert CLI
$GraXpertCliParams    = "-cli"
$GraXpertOutputParams = "-output"

# --- Setup ---

## 1. Check for GraXpert CLI
if (-not (Test-Path $GraXpertPath)) {
    Write-Error "GraXpert executable not found at $GraXpertPath. Please check the path and try again."
    exit 1
}

## 2. Ensure Destination Directory Exists
if (-not (Test-Path $DestinationDirectory)) {
    Write-Host "Creating destination directory: $DestinationDirectory"
    New-Item -Path $DestinationDirectory -ItemType Directory -Force | Out-Null
} else {
    Write-Host "Destination directory exists. Starting processing."
}

Write-Host "---"

# --- Main Logic ---

## 3. Find .fit Files 
$FitsFiles = Get-ChildItem -Path $SourceDirectory -Filter "*.fit" -File

if ($FitsFiles.Count -eq 0) {
    Write-Warning "No .fit files found in $SourceDirectory. Exiting."
    exit 0
}

Write-Host "Found $($FitsFiles.Count) .fit files to process..."
Write-Host "---"

## 4. Process Each File
foreach ($File in $FitsFiles) {
    $BaseName = $File.BaseName
    
    # 1. Define Paths and Output Basename
    $BE_InputFile = $File.FullName
    
    # GraXpert Output File Definitions:
    # 1. Output Base Name (argument to GraXpert, WITHOUT .fit)
    $BE_OutputBaseName = Join-Path -Path $DestinationDirectory -ChildPath ("${BaseName}_gxb")
    # 2. Final Output File (used for Test-Path, WITH .fit)
    $BE_OutputFile = "$BE_OutputBaseName.fits"

    Write-Host "`nProcessing file: $($File.Name)" -ForegroundColor DarkCyan
    
    # Skip logic check
    if (Test-Path $BE_OutputFile) {
        Write-Host "  -> SKIPPED: GraXperted file already exists at $($BE_OutputFile)"
        continue
    }

    Write-Host "  1. Preparing to perform BE on: $($BE_InputFile)"

    # 2. Construct GraXpert Arguments
    $GraXpertArgsBE = @(
        "`"$BE_InputFile`"",      # Input file path (quoted)
        $GraXpertCliParams,      # -cli
        $GraXpertOutputParams,   # -output
        "`"$BE_OutputBaseName`"" # Output file basename (quoted)
    )

    $GraXpertCommandBE_Log = "$GraXpertPath " + ($GraXpertArgsBE -join ' ')
    Write-Host "  -> Command: $GraXpertCommandBE_Log"

    # 3. Start the process without waiting, storing the process object
    try {
        $Process = Start-Process -FilePath $GraXpertPath -ArgumentList $GraXpertArgsBE -PassThru -NoNewWindow -ErrorAction Stop
    }
    catch {
        Write-Error "Failed to start GraXpert for $($File.Name): $($_.Exception.Message)"
        continue
    }

    # 4. Enter the Active Monitoring Loop
    $ProcessID = $Process.Id
    Write-Host "  -> GraXpert started (PID: $ProcessID). Monitoring execution every ${MonitorIntervalSeconds}s..."
    
    do {
        # Wait for the specified interval
        Start-Sleep -Seconds $MonitorIntervalSeconds
        
        # Get the latest process information
        $Process = Get-Process -Id $ProcessID -ErrorAction SilentlyContinue
        
        if ($Process) {
            # Display live CPU and Memory usage
            $CPU = [Math]::Round($Process.CPU, 2)
            $WorkingSet = [Math]::Round($Process.WorkingSet / 1MB, 2)
            Write-Host "     [RUNNING] CPU: $($CPU)s | Memory: $($WorkingSet) MB"
        }
    }
    # This line has been manually typed to eliminate the hidden character error
    while ($Process -ne $null) 

    Write-Host "  ✅ GraXpert process finished for $($File.Name)." -ForegroundColor Green

    # 5. Final File Verification
    if (Test-Path $BE_OutputFile) {
        Write-Host "  🎉 Output file verified: $($BE_OutputFile)" -ForegroundColor Green
    } else {
        Write-Error "GraXpert process finished, but output file not found at $($BE_OutputFile). Check GraXpert logs."
    }
    
    Write-Host "---"
}

Write-Host "Batch Processing complete. All files processed." -ForegroundColor Yellow