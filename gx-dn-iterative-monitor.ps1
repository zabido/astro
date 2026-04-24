# --- Configuration Section ---

# Set the path to the GraXpert executable
$GraXpertPath = "c:\Users\zabido\AppData\Local\Programs\GraXpert\GraXpert.exe"

# Source directory containing the FITS files (e.g., *-AS-BS.fits)
$SourceDir = "c:\Users\zabido\Astro\SeestarS30 Messier Project\gxb\"

# Define the output directory (a subfolder named 'dn')
$DestinationDir = Join-Path -Path $SourceDir -ChildPath "gxd"

# GraXpert command-line parameters
$GraXpertCliParams = "-cli"
$GraXpertOutputParams = "-output"
$GraXpertDnCmd = "-cmd denoising"
$MonitorIntervalSeconds = 5 # How often to check the process status

# --- Setup ---

# Ensure the destination directory exists
if (-not (Test-Path $DestinationDir)) {
    Write-Host "Creating destination directory: $DestinationDir"
    New-Item -Path $DestinationDir -ItemType Directory -Force | Out-Null
} else {
    Write-Host "Destination directory exists. Starting processing."
}

# Ensure GraXpert exists
if (-not (Test-Path $GraXpertPath)) {
    Write-Error "GraXpert executable not found at $GraXpertPath. Please check the path and try again."
    exit
}

Write-Host "---"

# --- Main Logic ---

# Find all .fits files in the source directory
$FitsFiles = Get-ChildItem -Path $SourceDir -Filter "*.fits" -File

if ($FitsFiles.Count -eq 0) {
    Write-Warning "No .fits files found in $SourceDir. Exiting."
    exit
}

foreach ($File in $FitsFiles) {
    $BaseName = $File.BaseName
    $Extension = $File.Extension
    
    # 1. Define Paths and Output Basename
    $DN_InputFile = $File.FullName 
    $DN_OutputFile = Join-Path -Path $DestinationDir -ChildPath ("${BaseName}-DN${Extension}")
    # GraXpert requires the basename only (it adds the extension itself)
    $DN_OutputBaseName = Join-Path -Path $DestinationDir -ChildPath "${BaseName}-DN"
    
    Write-Host "`nProcessing file: $($File.Name)" -ForegroundColor DarkCyan
    
    # Skip logic check
    if (Test-Path $DN_OutputFile) {
        Write-Host "  -> SKIPPED: Denoised file already exists at $($DN_OutputFile)"
        continue
    }

    Write-Host "  1. Preparing to denoise: $($DN_InputFile)"

    # 2. Construct GraXpert Arguments
    $GraXpertArgsDN = @(
        "`"$DN_InputFile`"",
        $GraXpertCliParams,
        $GraXpertDnCmd,
        $GraXpertOutputParams,
        "`"$DN_OutputBaseName`""
    )

    $GraXpertCommandDN_Log = "$GraXpertPath " + ($GraXpertArgsDN -join ' ')
    Write-Host "  -> Command: $GraXpertCommandDN_Log"

    # 3. Start the process without waiting, storing the process object
    # -PassThru returns the process object, -NoNewWindow keeps the console clean
    try {
        $Process = Start-Process -FilePath $GraXpertPath -ArgumentList $GraXpertArgsDN -PassThru -NoNewWindow -ErrorAction Stop
    }
    catch {
        Write-Error "Failed to start GraXpert for $($File.Name): $($_.Exception.Message)"
        continue
    }

    # 4. Enter the Active Monitoring Loop
    $ProcessID = $Process.Id
    Write-Host "  -> GraXpert started (PID: $ProcessID). Monitoring execution every ${MonitorIntervalSeconds}s..."
    
    do {
        # Wait for the specified interval
        Start-Sleep -Seconds $MonitorIntervalSeconds
        
        # Get the latest process information
        $Process = Get-Process -Id $ProcessID -ErrorAction SilentlyContinue
        
        if ($Process) {
            # Display live CPU and Memory usage
            $CPU = [Math]::Round($Process.CPU, 2)
            $WorkingSet = [Math]::Round($Process.WorkingSet / 1MB, 2)
            Write-Host "     [RUNNING] CPU: $($CPU)s | Memory: $($WorkingSet) MB"
        }
    }
    # Loop continues as long as the process object exists (GraXpert is running)
    while ($Process -ne $null) 

    Write-Host "  ✅ GraXpert process finished for $($File.Name)." -ForegroundColor Green

    # 5. Final File Verification
    # Check if the file was created successfully now that the process is guaranteed finished
    if (Test-Path $DN_OutputFile) {
        Write-Host "  🎉 Output file verified: $($DN_OutputFile)" -ForegroundColor Green
    } else {
        Write-Error "GraXpert process finished, but output file not found at $($DN_OutputFile). Check GraXpert logs."
    }
    
    Write-Host "---"
}

Write-Host "Batch Denoising complete. All files processed." -ForegroundColor Yellow