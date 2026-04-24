# Astro Photography Scripts 🌌

A collection of Python and PowerShell tools designed to automate astrophotography workflows, specifically for N.I.N.A., Seestar, and general FITS image processing.

---

## Detailed Script Guides

### [astro-platesolve.py](astro-platesolve.py)
**Description:** An intelligent wrapper for the **ASTAP** plate solver. It automatically fetches target coordinates from online catalogs (SIMBAD/NED via Astropy), calculates the Field of View (FOV), and attempts to solve the image. If the initial search fails, it can perform a "blind search" by expanding the search radius to 180°.

**Usage Mode:** Command-line arguments.

* **Camera Compatibility:** * ⚠️ **Current version:** Specifically calibrated for **Canon 60D** (fixed 22.3mm sensor width in calculations).
    * **How to adapt:** If using a different sensor, edit the following line in the script:
      `fov_width = (22.3 / args.focal) * 57.3`
      Replace `22.3` with your sensor's width in mm (e.g., Seestar S50 = `6.4`, APS-C = `23.5`, Full Frame = `36`).
* **Prerequisites:** * **ASTAP** must be installed (Default path: `C:\Program Files\astap\astap.exe`).
    * Python libraries: `pip install astropy`
* **How to run:**
    ```powershell
    python astro-platesolve.py --path "C:\path\to\image.fits" --object "M31" --focal 600 --blind
    ```
* **Key Parameters:**
    * `--path`: Full path to your FITS or RAW file.
    * `--object`: Target name for coordinate lookup (e.g., "M42", "M31").
    * `--focal`: Your telescope/lens focal length in mm.
    * `--blind`: Optional flag to trigger a 180° wide search if the standard solve fails.

---

### [fitsheader.py](fitsheader.py)
**Description:** A metadata extraction tool for FITS files. It reads the primary header of a FITS image and saves all the technical information (EXPTIME, GAIN, DATE, etc.) into a plain text file (.txt) with the same name as the source.

**Usage Mode:** Command-line argument.

* **Prerequisites:** * Python library: `pip install astropy`
* **How to run:**
    ```powershell
    python fitsheader.py "C:\path\to\your\image.fits"
    ```
* **What it does:** 1. Opens the specified `.fits` file.
    2. Reads the primary header index.
    3. Creates a new `.txt` file in the same folder (e.g., `image.txt`).
    4. Writes all header keys and values into the text file for easy review.

---

### [list_objects_from_fits.py](list_objects_from_fits.py)
**Description:** An advanced astronomical identification tool. It reads the WCS (World Coordinate System) coordinates from a solved FITS file and queries the **SIMBAD** professional database to identify deep-sky objects (primarily galaxies) within the image's field of view. It filters results by magnitude and type, and calculates physical properties like distance (in millions of light-years) and actual size (in light-years).

**Usage Mode:** Command-line argument.

* **Prerequisites:** * Python libraries: `pip install numpy astropy astroquery`
    * An **internet connection** is required for the SIMBAD database query.
    * The input FITS file **must be plate-solved** (contain WCS headers).
* **How to run:**
    ```powershell
    python list_objects_from_fits.py "C:\path\to\solved_image.fits"
    ```
* **What it does:**
    1. Calculates the center and radius of your image in sky coordinates.
    2. Downloads object data (magnitude, type, distance, dimensions) from SIMBAD.
    3. Filters for galaxies and objects brighter than Mag 16.0.
    4. Calculates absolute magnitude and real-world size in light-years.
    5. Saves a formatted report (e.g., `galaxy_list.txt`) with a sorted table of all identified objects.

---

## Other Scripts in this Repository

### Python Tools 🐍

* **moonscale-fits-to-png.py**: Converts FITS to PNG with optimized scaling for lunar imaging.
* **remove_spots.py**: Image processing script for cleaning artifacts or hot pixels.

### PowerShell Scripts 🐚
* **graxpert-BE.ps1**: Automates background extraction using GraXpert.
* **gx-dn-iterative-monitor.ps1**: Monitoring script for GraXpert Denoise operations.
* **NINA_Light-to_lights.ps1**: Standardizes N.I.N.A. "Light" folder naming.
* **Seestar_sub_organizer-lights-deljpg.ps1**: Organizes Seestar sub-exposures and cleans up JPEGs.

---

## Quick Git Workflow
To keep your scripts synced and safe across all machines:

1. **Pull latest changes from GitHub:**
   ```powershell
   git pull origin main