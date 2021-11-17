"""Visualize the distribution from light sources at specific camera pixel
"""
import numpy as np
import cv2
from skimage.exposure import adjust_gamma

ix, iy = 0, 0

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
    T_reshaped = T.reshape((n, m, co, q, p))

    winname_main = "main"
    winname_sub = "sub"
    cv2.namedWindow(winname_main)
    cv2.namedWindow(winname_sub)

    def update_position(event, x, y, flags, param):
        global ix, iy 
        if event == cv2.EVENT_MOUSEMOVE:
            ix, iy = x, y

    cv2.setMouseCallback(winname_main, update_position)

    img_relighted = adjust_gamma(np.sum(T_reshaped, axis=(-1, -2)) * 2.0, 1/1.8)
    img_relighted_u8 = np.clip(img_relighted * 255, 0, 255).astype(np.uint8)

    while True:
        img_ltm_at_ixiy = np.moveaxis(T_reshaped[iy, ix] * 30, 0, -1) # (co, q, p) -> (q, p, co)
        img_ltm_at_ixiy_u8 = np.clip(img_ltm_at_ixiy * 255, 0, 255).astype(np.uint8)
        img_ltm_at_ixiy_u8 = cv2.resize(img_ltm_at_ixiy_u8, None, fx=20, fy=20, interpolation=cv2.INTER_NEAREST)

        cv2.imshow(winname_main, img_relighted_u8)
        cv2.imshow(winname_sub, img_ltm_at_ixiy_u8)
        
        key = cv2.waitKey(30)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()