import numpy as np
from astropy.io import fits
import cv2
import os
import sys

def add_moon_scale(fits_path):
    # Kimeneti név generálása: eredeti_név + _MSL.png
    base_path = os.path.splitext(fits_path)[0]
    output_path = f"{base_path}_MSL.png"

    try:
        # 1. FITS megnyitása
        with fits.open(fits_path) as hdul:
            header = hdul[0].header
            data = hdul[0].data

            # 2. Pixel scale kinyerése (fokban/pixel)
            # A Siril a CDELT vagy a CD mátrix elemeibe menti a felbontást
            if 'CDELT1' in header:
                deg_per_px = abs(header['CDELT1'])
            elif 'CD1_1' in header:
                deg_per_px = np.sqrt(header['CD1_1']**2 + header['CD1_2']**2)
            else:
                print("Hiba: Nem találhatók Plate Solve adatok (CDELT vagy CD mátrix) a FITS fejlécben!")
                return

            # 3. Skála számítása (Hold átmérő = 0.5 fok = 30 ívperc)
            moon_diameter_px = int(0.5 / deg_per_px)
            
            # 4. Kép konvertálása 8-bitre (OpenCV-hez)
            # Biztosítjuk, hogy a kép adatai 0 és 1 közötti, majd 0-255 közötti értékek legyenek
            img_min = data.min()
            img_max = data.max()
            
            # Lineáris skálázás 0-255 közé
            img = ((data - img_min) / (img_max - img_min) * 255).astype(np.uint8)

            if data.ndim == 3:
                # Ha színes (3, H, W) -> (H, W, 3)
                img = np.transpose(img, (1, 2, 0))
                # Siril RGB-t ment, OpenCV BGR-t vár
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            # Egyszerű automatikus nyújtás (stretch), hogy ne legyen sötét a kép
            low, high = np.percentile(img, (0.5, 99.5))
            img = np.clip(img, low, high)
            img = ((img - low) / (high - low) * 255).astype(np.uint8)

            # 5. Skála rajzolása (I-alakú vonal)
            h, w = img.shape[:2]
            margin = 60
            line_y = h - margin
            end_x = w - margin
            start_x = end_x - moon_diameter_px
            tick_h = 12

            # Fehér szín, 2 pixel vastagság
            color = (255, 255, 255)
            cv2.line(img, (start_x, line_y), (end_x, line_y), color, 2) # Vízszintes
            cv2.line(img, (start_x, line_y - tick_h), (start_x, line_y + tick_h), color, 2) # Bal tick
            cv2.line(img, (end_x, line_y - tick_h), (end_x, line_y + tick_h), color, 2) # Jobb tick

            # Szöveg elhelyezése
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = "Hold atmeroje (30')"
            cv2.putText(img, text, (start_x, line_y - 25), font, 0.7, color, 2, cv2.LINE_AA)

            # 6. Mentés ékezetes útvonal támogatással
            # A sima cv2.imwrite helyett bufferen keresztül mentünk
            is_success, buffer = cv2.imencode(".png", img)
            if is_success:
                with open(output_path, "wb") as f:
                    f.write(buffer)
                print(f"Siker! Mentve: {output_path} (Hold átmérő: {moon_diameter_px} px)")
            else:
                print(f"HIBA: Nem sikerült a PNG kódolás!")

    except Exception as e:
        print(f"Váratlan hiba történt: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python script_neve.py kepfajl.fits")
    else:
        add_moon_scale(sys.argv[1])