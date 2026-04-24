import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    if not os.path.exists(input_path):
        print(f"Hiba: A fájl nem található: {input_path}")
        return

    img = cv2.imread(input_path)
    if img is None:
        print("Hiba: Nem sikerült betölteni a képet.")
        return

    print(f"Végső finomhangolás: {input_path}...")

    # 1. Szürkeárnyalatos kép
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Emelt küszöbérték (Threshold = 45) 
    # Ez már a halványabb szürke széleket is látja
    _, mask = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY_INV)

    # 3. Zajszűrés a maszkon (Morphology)
    # Hogy ne kapjon bele az égbolt természetes sötétebb foltjaiba (zajba)
    kernel_clean = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_clean)

    # 4. Extra tágítás és elmosás a maszkhoz
    # A 9x9-es kernel brutálisabb, biztosan lefedi a fánkok szélét
    kernel_dilate = np.ones((9,9), np.uint8)
    mask = cv2.dilate(mask, kernel_dilate, iterations=2)
    mask = cv2.GaussianBlur(mask, (5,5), 0) # Lágyabb átmenet a javítás szélén

    # 5. Inpainting (Navier-Stokes metódus kipróbálása a változatosabb háttérhez)
    result = cv2.inpaint(img, mask, inpaintRadius=15, flags=cv2.INPAINT_NS)

    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"

    cv2.imwrite(output_path, result)
    print(f"Kész! Mentve: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Használat: python remove_spots.py \"fajlnev.png\"")
    else:
        process_image(sys.argv[1])