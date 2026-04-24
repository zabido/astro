import cv2
import numpy as np
import sys
import os

def process_image(input_path):
    img = cv2.imread(input_path)
    if img is None: return

    # 1. Maszk készítése
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Kicsit bátrabb threshold, hogy a szürke udvarokat is elkapjuk
    _, mask = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
    
    # 2. A maszk agresszív növelése
    # Hogy a folt körüli sötétebb "aurát" is eltüntessük
    kernel = np.ones((11,11), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    
    # Lágy szél (feathering) előkészítése
    mask_blur = cv2.GaussianBlur(mask, (31, 31), 0).astype(np.float32) / 255.0
    mask_blur = cv2.merge([mask_blur, mask_blur, mask_blur]) # 3 csatornássá tesszük

    # 3. Mintavételi kép (eltoljuk a képet vízszintesen 60 pixellel)
    # Ez lesz a "tiszta" forrásunk
    rows, cols, _ = img.shape
    M = np.float32([[1, 0, 60], [0, 1, 0]])
    shift_img = cv2.warpAffine(img, M, (cols, rows), borderMode=cv2.BORDER_REPLICATE)

    # 4. A két kép összekeverése a maszk alapján
    # Ahol fekete volt a maszk, ott az eredeti marad
    # Ahol fehér, ott a shiftelt (tiszta) kép
    # A széleken pedig finom átmenet
    output = img.astype(np.float32) * (1.0 - mask_blur) + shift_img.astype(np.float32) * mask_blur
    output = np.clip(output, 0, 255).astype(np.uint8)

    file_name, file_ext = os.path.splitext(input_path)
    output_path = f"{file_name}-sptls{file_ext}"
    cv2.imwrite(output_path, output)
    print(f"Kész! Drasztikus javítás mentve: {output_path}")

if __name__ == "__main__":
    process_image(sys.argv[1])