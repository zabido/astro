# Astro Photography Scripts 🌌

A collection of Python and PowerShell tools designed to automate astrophotography workflows, specifically for N.I.N.A., Seestar, and general FITS image processing.

---

## Detailed Script Guides

### [astro-platesolve.py](astro-platesolve.py)
**Description:** An intelligent wrapper for the **ASTAP** plate solver. It automatically fetches target coordinates from online catalogs (SIMBAD/NED via Astropy), calculates the Field of View (FOV) based on your focal length, and attempts to solve the image. If the initial search fails, it can perform a "blind search" by expanding the search radius to 180°.

**Usage Mode:** Command-line arguments (No file editing needed).

* **Prerequisites:** * ASTAP must be installed (Default: `C:\Program Files\astap\astap.exe`).
    * Python libraries: `pip install astropy`
* **How to run:**
    ```powershell
    python astro-platesolve.py --path "C:\path\to\your\image.fits" --object "M31" --focal 600 --blind
    ```
* **Key Parameters:**
    * `--path`: Full path to your FITS or RAW file.
    * `--object`: Target name for coordinate lookup (e.g., "M42", "NGC 7000").
    * `--focal`: Your telescope/lens focal length in mm.
    * `--astap`: (Optional) Use this if your ASTAP is installed in a custom folder.

---

## Other Scripts in this Repository

### Python Tools 🐍
* **fitsheader.py**: Extracts and displays metadata information from FITS file headers.
* **list_objects_from_fits.py**: Scans FITS files and lists identified celestial objects.
* **moonscale-fits-to-png.py**: Converts FITS to PNG with optimized scaling for lunar imaging.
* **remove_spots.py**: Image processing script for cleaning artifacts or hot pixels.

### PowerShell Scripts 🐚
* **graxpert-BE.ps1**: Automates background extraction using GraXpert.
* **gx-dn-iterative-monitor.ps1**: Monitoring script for GraXpert Denoise operations.
* **NINA_Light-to_lights.ps1**: Standardizes N.I.N.A. "Light" folder naming.
* **Seestar_sub_organizer-lights-deljpg.ps1**: Organizes Seestar sub-exposures and cleans up JPEGs.

---

## Quick Git Workflow
To keep your scripts synced and safe:
1. **Pull latest:** `git pull`
2. **Add changes:** `git add .`
3. **Save & Push:** `git commit -m "Update scripts"; git push`