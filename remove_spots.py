import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    img = cv2.imread(input_path)
    if img is None: return

    # 1. Maszk készítése - óvatosabban, hogy a csillag pereme megmaradjon
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Alacsonyabb threshold, hogy csak a tényleg sötét foltokat lássa
    _, mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY_INV)
    
    # 2. Maszk tisztítása
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)

    # 3. Inpainting - Kisebb sugárral, hogy ne mosson össze nagy területeket
    # A kisebb radius megőrzi a lokális gradiens változásokat
    restored = cv2.inpaint(img, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

    # 4. ZAJ-REINTEGRÁCIÓ (Ez a kulcs!)
    # Generálunk egy kis digitális zajt, ami hasonlít a szenzorzajhoz
    noise = np.zeros(img.shape, dtype=np.int8)
    cv2.randn(noise, 0, 5) # 5-ös szórású zaj
    
    # Csak ott adjuk hozzá a zajt, ahol javítottunk (a maszkon belül)
    noise_mask = cv2.bitwise_and(noise, noise, mask=mask).astype(np.uint8)
    final = cv2.add(restored, noise_mask)

    # 5. Mentés
    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"
    cv2.imwrite(output_path, final)
    print(f"Kész: {output_path}")

if __name__ == "__main__":
    process_image(sys.argv[1])