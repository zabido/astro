import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    # 1. Fájl létezésének ellenőrzése
    if not os.path.exists(input_path):
        print(f"Hiba: A fájl nem található: {input_path}")
        return

    # 2. Kép betöltése
    img = cv2.imread(input_path)
    if img is None:
        print("Hiba: Nem sikerült betölteni a képet. Biztosan érvényes képfájl?")
        return

    print(f"Feldolgozás alatt: {input_path}...")

    # 3. Érzékenyebb küszöbérték (Threshold)
    # Megemeljük 15-ről 30-ra, hogy a szürkébb foltokat is elkapja
    _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # 4. Erősebb tágítás (Dilatáció)
    # Növeljük a kernel méretét és az ismétlésszámot, 
    # hogy a maszk biztosan túlnyúljon a folt elmosódott szélén is.
    kernel = np.ones((7,7), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # 5. Inpainting sugár növelése
    # Az inpaintRadius 5-ről 10-re emelése segít, hogy távolabbról 
    # vegyen tiszta mintát a kitöltéshez.
    result = cv2.inpaint(img, mask, inpaintRadius=10, flags=cv2.INPAINT_TELEA)

    # 6. Mentési útvonal generálása
    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"

    # Mentés
    cv2.imwrite(output_path, result)
    print(f"Kész! Mentve ide: {output_path}")

if __name__ == "__main__":
    # CLI argumentum ellenőrzése
    if len(sys.argv) < 2:
        print("Használat: python remove_spots.py kepfajl.png")
    else:
        process_image(sys.argv[1])