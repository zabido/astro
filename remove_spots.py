import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    img = cv2.imread(input_path)
    if img is None: return

    # 1. Maszk készítése a sötét foltokról
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY_INV)
    
    # Tisztítjuk a maszkot, hogy csak a valódi foltok maradjanak
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Megkeressük a foltokat (kontúrokat)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output = img.copy()

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Keressünk egy forrás területet a folt mellett (pl. 20 pixellel jobbra)
        offset = 25
        source_x = x + w + offset
        
        # Ellenőrizzük, hogy ne menjünk ki a képből
        if source_x + w > img.shape[1]:
            source_x = x - w - offset # Ha jobb szélén van, nézzük balra
            
        if source_x < 0: continue

        # Kivágjuk a forrást és a célterületet
        source_patch = img[y:y+h, source_x:source_x+w]
        
        # Fontos: Csak akkor másolunk, ha a forrás nem tartalmaz csillagot (nem túl fényes)
        if np.max(source_patch) < 180: 
            # Készítünk egy kis feather (lágy szél) maszkot a folthoz
            patch_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.rectangle(patch_mask, (0,0), (w,h), 255, -1)
            patch_mask = cv2.GaussianBlur(patch_mask, (7,7), 0) / 255.0
            
            # Mixelés (Blending)
            for c in range(3):
                output[y:y+h, x:x+w, c] = (1.0 - patch_mask) * output[y:y+h, x:x+w, c] + \
                                          patch_mask * source_patch[:, :, c]

    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"
    cv2.imwrite(output_path, output)
    print(f"Kész! Forrás-alapú klónozás mentve: {output_path}")

if __name__ == "__main__":
    process_image(sys.argv[1])