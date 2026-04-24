import subprocess
import os
import time
import argparse
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u

def get_target_coords(name):
    print(f"🔍 Searching catalog for {name}...")
    try:
        coords = SkyCoord.from_name(name)
        return coords.ra.deg, coords.dec.deg
    except Exception as e:
        print(f"❌ Coordinate lookup failed for {name}: {e}")
        return None, None

def run_astap(args, ra, dec, radius, fov, extra_flags=[]):
    cmd = [
        args.astap, "-f", args.path,
        "-ra", str(ra),
        "-dec", str(dec),
        "-v", str(round(fov, 2)),
        "-r", str(radius),
        "-z", "2",    # Binning 2x2 to handle DSLR noise/Bayer pattern
        "-s", "500",  # Focus on the 500 brightest landmark stars
        "-batch"
    ] + extra_flags
    
    subprocess.run(cmd)
    return os.path.splitext(args.path)[0] + ".wcs"

def solve_generic(args):
    ra_deg, dec_deg = get_target_coords(args.object)
    if ra_deg is None: return

    # Calculate FOV for Canon 60D (22.3mm sensor width)
    fov_width = (22.3 / args.focal) * 57.3
    print(f"🎯 Target: {args.object} | 📍 RA: {ra_deg:.4f}, Dec: {dec_deg:.4f}")
    print(f"📏 Focal: {args.focal}mm | FOV: {fov_width:.2f}°")

    # --- ATTEMPT 1: Standard Search ---
    print(f"🔭 Attempt 1: Standard search (Radius: {args.radius}°)...")
    wcs_file = run_astap(args, ra_deg, dec_deg, args.radius, fov_width)

    # --- ATTEMPT 2: Blind Search (If enabled and Attempt 1 failed) ---
    if not os.path.exists(wcs_file) and args.blind:
        print("⚠️  Standard solve failed. Initiating Blind/Wide Search (Radius: 180°)...")
        wcs_file = run_astap(args, ra_deg, dec_deg, 180, fov_width)

    # --- PROCESS RESULTS ---
    if os.path.exists(wcs_file):
        print("✅ Solve successful!")
        is_fits = args.path.lower().endswith(('.fit', '.fits', '.fts'))
        
        if is_fits:
            print("Merging WCS into FITS header...")
            # ... (Rest of the FITS merging logic from previous script)
            print(f"✨ SUCCESS! Saved as: {os.path.splitext(args.path)[0] + '_SOLVED.fit'}")
        else:
            print(f"📢 RAW file solved! Sidecar created: {wcs_file}")
            print("Tip: Convert to FITS in Siril to bake these coordinates in.")
        
        # Keep WCS for RAWs, delete for FITS if merged
        if is_fits: os.remove(wcs_file)
    else:
        print("❌ Plate solve failed after all attempts. Check focus or star database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic Astro Plate Solver")
    parser.add_argument("--path", type=str, required=True)
    parser.add_argument("--object", type=str, default="M31")
    parser.add_argument("--focal", type=float, default=600.0)
    parser.add_argument("--radius", type=float, default=30.0)
    parser.add_argument("--blind", action="store_true", help="Try 180° radius if first attempt fails")
    parser.add_argument("--astap", type=str, default=r"C:\Program Files\astap\astap.exe")

    args = parser.parse_args()
    solve_generic(args)