import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    img = cv2.imread(input_path)
    if img is None: return

    # 1. Maszk készítése - agresszívabb tágítással a peremek ellen
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY_INV)
    
    # Morfológia: kis zajok eltüntetése, majd jelentős tágítás (dilate)
    kernel_clean = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_clean)
    
    # A tágítás (dilate) biztosítja, hogy a maszk nagyobb legyen a foltnál (rálógjon)
    kernel_expand = np.ones((7,7), np.uint8)
    mask = cv2.dilate(mask, kernel_expand, iterations=2)

    # Kontúrok keresése
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output = img.copy()

    for cnt in contours:
        # Csak a releváns méretű foltokkal foglalkozunk
        if cv2.contourArea(cnt) < 5: continue
        
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Középpont meghatározása a klónozáshoz
        center = (x + w // 2, y + h // 2)
        
        # Forrás terület keresése (eltolás)
        offset = 40
        src_x = x + w + offset
        if src_x + w > img.shape[1]: src_x = x - w - offset
        if src_x < 0 or src_x + w > img.shape[1]: continue

        # Egyedi maszk az adott kontúrhoz
        single_mask = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(single_mask, [cnt], -1, 255, -1)
        
        # Ellenőrizzük, hogy a forrás terület tiszta-e (nincs benne csillag)
        src_patch = img[y:y+h, src_x:src_x+w]
        if np.max(src_patch) < 170:
            try:
                # SEAMLESS CLONING: Ez a funkció varázsolja bele a forrást a környezetbe
                # A MIXED_CLONE megtartja a cél terület (háttér) textúráját is
                output = cv2.seamlessClone(img, output, single_mask, center, cv2.MIXED_CLONE)
            except Exception as e:
                continue

    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"
    cv2.imwrite(output_path, output)
    print(f"Kész! Seamless Patchwork mentve: {output_path}")

if __name__ == "__main__":
    process_image(sys.argv[1])