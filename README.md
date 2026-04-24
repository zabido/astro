# Astro Photography Scripts 🌌

A collection of Python and PowerShell tools designed to automate astrophotography workflows, specifically for N.I.N.A., Seestar, and general FITS image processing.

## Script Descriptions

### Python Tools 🐍
* **astro-platesolve.py**: 

Description: An intelligent wrapper for the ASTAP plate solver. It automatically fetches target coordinates from online catalogs (SIMBAD/NED via Astropy), calculates the Field of View (FOV) based on your focal length, and attempts to solve the image. If the initial search fails, it can perform a "blind search" by expanding the search radius to 180°.

Usage: This script uses command-line arguments. You don't need to edit the file every time, but you must have ASTAP installed.

Setup: Ensure the --astap path in the script matches your astap.exe location (default is C:\Program Files\astap\astap.exe).

Run command:

PowerShell
python astro-platesolve.py --path "C:\Astro\M31.fits" --object "M31" --focal 600 --blind
Key Arguments:

--path: Path to your FITS or RAW file (Required).

--object: Name of the target (e.g., "M42", "Vega") for coordinate lookup.

--focal: Your telescope's focal length in mm (default: 600).

--radius: Initial search radius in degrees (default: 30).

--blind: Add this flag to try a 180° search if the initial solve fails.

* **fitsheader.py**: A utility to extract and display metadata information from FITS file headers.
* **list_objects_from_fits.py**: Scans FITS files and lists identified celestial objects based on catalog data or header info.
* **moonscale-fits-to-png.py**: Converts FITS files to PNG format while applying specific scaling, likely optimized for lunar imaging.
* **remove_spots.py**: An image processing script for cleaning artifacts or hot pixels (spots) from astronomical frames.

### PowerShell Scripts 🐚
* **graxpert-BE.ps1**: Automates background extraction (BE) using GraXpert, likely for batch processing multiple frames.
* **gx-dn-iterative-monitor.ps1**: A monitoring script for GraXpert Denoise (DN) operations, possibly tracking iterative processing progress.
* **NINA_Light-to_lights.ps1**: A cleanup tool for N.I.N.A. (Nighttime Imaging 'N' Astronomy) that renames or reorganizes "Light" folders to a standard "lights" format.
* **Seestar_sub_organizer-lights-deljpg.ps1**: Specifically designed for ZWO Seestar users to organize sub-exposures and delete unnecessary JPEG previews to save space.

---

## Quick Setup

To use the PowerShell scripts, ensure your execution policy is set:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser