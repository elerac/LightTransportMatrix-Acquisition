"""Relighting with the Light Transport Matrix
"""
import numpy as np
import cv2
from skimage.exposure import adjust_gamma
import structuredlight as sl

def main():
    # Image size captured by camera
    m = 480
    n = 300
    co = 3 # color
    # Projection pattern size
    p = 16
    q = 9
    dir_name = f"lighttransport_{n}x{m}x{co}_{q}x{p}"
    print("Load light_transport_matrix")
    T = np.load(f"{dir_name}/light_transport_matrix.npy") # (m*n*co, p*q)

    # Relight pattern
    img_input = np.zeros((q, p, 3), dtype=np.uint8)
    img_input[:,       :p//3,   0] = 255 # B
    img_input[:,   p//3:p*2//3, 1] = 255 # G
    img_input[:, p*2//3:,       2] = 255 # R
    
    print("Calculate relighting")
    T_reshaped = np.reshape(T, (m*n, co, p*q)) # (m*n, co, p*q)
    imlist_output = []
    for i in range(co):
        P = img_input[..., i].flatten() # (p*q)
        C = T_reshaped[:, i, :] @ P # (m*n, p*q) x (p*q) = (m*n)
        img = np.reshape(C, (n, m)) # (n, m)
        imlist_output.append(img)
    
    img_output = cv2.merge(imlist_output) # (n, m, co)
    img_output_u8 = adjust_gamma(np.clip(img_output*4.0, 0, 255).astype(np.uint8), gamma=1/1.8)
    
    cv2.imwrite(f"{dir_name}/input.png", img_input)
    cv2.imwrite(f"{dir_name}/output.png", img_output_u8)

if __name__=="__main__":
    main()
