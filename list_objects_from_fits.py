import sys, os, numpy as np
from astropy.io import fits
from astropy.wcs import WCS
from astroquery.simbad import Simbad
import astropy.units as u

# Messier adatok: (Távolság Mly, Valós méret ly)
MESSIER_DATA = {
    'M  84': (52, 110000), 'M  86': (52, 135000), 'M  87': (53.5, 120000),
    'M  88': (55, 130000), 'M  89': (50, 80000),  'M  90': (58, 165000),
    'M  91': (63, 100000), 'M  98': (44, 160000), 'M  99': (55, 80000),
    'M 100': (55, 107000)
}

def get_col_val(row, target_name):
    for col in row.colnames:
        if col.lower() == target_name.lower():
            val = row[col]
            return val if not np.ma.is_masked(val) else None
    return None

def get_clean_name(ids_val):
    if not ids_val: return "Unknown"
    name_list = str(ids_val).split('|')
    
    # 1. Messier prioritás
    for n in name_list:
        if 'M ' in n or 'MESSIER' in n:
            return n.replace('MESSIER', 'M').strip()
    
    # 2. NGC/IC/PGC prioritás
    for prefix in ['NGC', 'IC ', 'PGC']:
        for n in name_list:
            if prefix in n.upper():
                return n.strip()
    return None

def get_unique_filename(base_name):
    if not os.path.exists(base_name): return base_name
    name, ext = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(f"{name}_{counter}{ext}"):
        counter += 1
    return f"{name}_{counter}{ext}"

def catalog_fits_objects(fits_path, output_base="galaxy_list.txt"):
    try:
        with fits.open(fits_path) as hdul:
            header = hdul[0].header
            wcs = WCS(header, naxis=2)
            nx, ny = header.get('NAXIS1'), header.get('NAXIS2')

        center = wcs.pixel_to_world(nx/2, ny/2)
        radius = center.separation(wcs.pixel_to_world(0, 0))

        print(f"Lekerdezes (SIMBAD)... Sugar: {radius.deg:.2f} deg")

        Simbad.add_votable_fields('otype', 'mesdistance', 'flux(V)', 'ids', 'galdim_majaxis')
        result = Simbad.query_region(center, radius=radius)

        if result is None: return

        galaxy_data = []
        seen_names = set() # Duplikációk kiszűrésére

        for row in result:
            ids_val = get_col_val(row, 'ids') or get_col_val(row, 'main_id')
            name = get_clean_name(ids_val)
            
            # CSAK HA NEVESÍTETT ÉS MÉG NEM LÁTTUK
            if not name or name in seen_names:
                continue

            otype = str(get_col_val(row, 'otype') or 'GAL').upper()
            mag_raw = get_col_val(row, 'flux_v') or get_col_val(row, 'v')
            try: mag = float(mag_raw)
            except: mag = 99.0
            
            # Magnitúdó és típus szűrés
            if mag > 16.0 or not any(x in otype for x in ['G', 'GAL', 'MCL', 'AGN', 'LIN', 'QSO']):
                continue

            seen_names.add(name)

            # Távolság és méret számítás
            dist_mly = None
            for m_key in MESSIER_DATA:
                if m_key in name: dist_mly = MESSIER_DATA[m_key][0]
            
            if dist_mly is None:
                try: dist_mly = float(get_col_val(row, 'mesdistance')) * 3.26
                except: dist_mly = None

            size_ly = 0
            try:
                maj_axis_min = get_col_val(row, 'galdim_majaxis')
                if maj_axis_min and dist_mly:
                    size_ly = (float(maj_axis_min) / 60) * (np.pi / 180) * (dist_mly * 1_000_000)
            except: size_ly = 0

            abs_mag = "n/a"
            if dist_mly and mag < 90:
                dist_pc = (dist_mly * 1_000_000) / 3.26
                abs_mag = mag - 5 * (np.log10(dist_pc) - 1)

            galaxy_data.append({
                'name': name, 'type': otype, 'mag': mag, 
                'dist': dist_mly, 'size': size_ly, 'abs_mag': abs_mag
            })

        galaxy_data.sort(key=lambda x: x['size'] if x['size'] else 0, reverse=True)

        output_txt = get_unique_filename(output_base)
        with open(output_txt, "w", encoding="utf-8") as f:
            f.write(f"Forras: {os.path.basename(fits_path)}\n")
            f.write(f"{'Nev':<18} | {'Tipus':<10} | {'Mag(V)':<6} | {'AbsMag':<7} | {'Tav(Mly)':<8} | {'Meret (ly)':<12}\n")
            f.write("-" * 80 + "\n")

            for g in galaxy_data:
                d_str = f"{g['dist']:.1f}" if g['dist'] else "n/a"
                m_str = f"{g['mag']:.1f}" if g['mag'] < 90 else "n/a"
                a_str = f"{g['abs_mag']:.1f}" if isinstance(g['abs_mag'], float) else "n/a"
                s_str = f"{int(g['size']):,}" if g['size'] > 0 else "n/a"
                f.write(f"{g['name']:<18} | {g['type']:<10} | {m_str:<6} | {a_str:<7} | {d_str:<8} | {s_str:<12}\n")

        print(f"Kesz! {len(galaxy_data)} egyedi galaxis mentve: {output_txt}")

    except Exception as e: print(f"Hiba: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1: catalog_fits_objects(sys.argv[1].strip("'\""))