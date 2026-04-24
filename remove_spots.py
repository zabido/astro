import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    img = cv2.imread(input_path)
    if img is None: return

    # 1. Érzékenyebb maszk készítése (60-as küszöb a halvány foltokhoz)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    
    # Maszk finomítása
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.dilate(mask, kernel, iterations=3) # Nagyobb rálógás

    # Kontúrok (egyedi foltok) keresése
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    output = img.copy().astype(np.float32)
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        center_x, center_y = x + w // 2, y + h // 2
        
        # 2. INTELIGENS FORRÁS KERESÉS
        # Megnézünk több irányt, és azt választjuk, ami a legkevésbé fényes (nincs csillag)
        best_patch = None
        min_brightness = float('inf')
        
        # Lehetséges eltolások: [jobbra, balra, le, fel]
        offsets = [(70, 0), (-70, 0), (0, 70), (0, -70)]
        
        for dx, dy in offsets:
            src_x, src_y = x + dx, y + dy
            
            # Határok ellenőrzése
            if src_x < 0 or src_y < 0 or src_x + w > img.shape[1] or src_y + h > img.shape[0]:
                continue
            
            test_patch = img[src_y:src_y+h, src_x:src_x+w]
            brightness = np.mean(test_patch)
            max_val = np.max(test_patch)
            
            # Ha nincs benne beégett csillag (max < 160) és ez a legsötétebb (legjobb háttér)
            if max_val < 160 and brightness < min_brightness:
                min_brightness = brightness
                best_patch = test_patch

        # 3. MÁSOLÁS LÁGY SZÉLLEL
        if best_patch is not None:
            # Egyedi lágy maszk a folthoz
            patch_mask = np.zeros((h, w), dtype=np.float32)
            cv2.rectangle(patch_mask, (0,0), (w,h), 1.0, -1)
            # Brutálisan elmosott szélek a tökéletes gradiensért
            blur_size = max(15, (w+h)//4 | 1) # dinamikus elmosás méret
            patch_mask = cv2.GaussianBlur(patch_mask, (blur_size, blur_size), 0)
            
            for c in range(3):
                target = output[y:y+h, x:x+w, c]
                source = best_patch[:, :, c].astype(np.float32)
                # Blending formula
                output[y:y+h, x:x+w, c] = (1.0 - patch_mask) * target + patch_mask * source

    # 4. Mentés
    output = np.clip(output, 0, 255).astype(np.uint8)
    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"
    cv2.imwrite(output_path, output)
    print(f"Kész! Intelligens klónozás mentve: {output_path}")

if __name__ == "__main__":
    process_image(sys.argv[1])