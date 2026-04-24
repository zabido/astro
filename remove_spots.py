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
        print("Hiba: Nem sikerült betölteni a képet. Ellenőrizd az elérési utat!")
        return

    print(f"Feldolgozás alatt: {input_path}...")

    # 3. Szürkeárnyalatos kép készítése a maszkoláshoz
    # EZ HIÁNYZOTT A HIBÁBÓL ADÓDÓAN
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 4. Érzékenyebb küszöbérték (Threshold)
    # A 30-as érték már a szürkébb, elmosódottabb foltokat is elkapja
    _, mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY_INV)

    # 5. Erősebb tágítás (Dilatáció)
    # 7x7-es kerettel és 2 ismétléssel (iterations=2) 
    # jóval túlhúzzuk a maszkot a foltok szélén
    kernel = np.ones((7,7), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # 6. Inpainting (A foltok eltüntetése)
    # Az inpaintRadius=10 segít a nagyobb foltok simább kitöltésében
    result = cv2.inpaint(img, mask, inpaintRadius=10, flags=cv2.INPAINT_TELEA)

    # 7. Mentési útvonal generálása
    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"

    # Mentés
    cv2.imwrite(output_path, result)
    print(f"Kész! Mentve ide: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python remove_spots.py \"eleresi_ut/kep.png\"")
    else:
        process_image(sys.argv[1])