"""Calculate the Light Transport Matrix
"""
import glob
import numpy as np
import cv2
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

    code_names = sorted(glob.glob(f"{dir_name}/code*.png"))
    print("The projected patterns")
    print(code_names[:15])
    imlist_code = [cv2.imread(name, 0) for name in code_names]
    
    observe_names = sorted(glob.glob(dir_name + "/" + "observe*.png"))
    print("The images captured by the camera")
    print(observe_names[:15])
    imlist_observe = [cv2.imread(name, 1) for name in observe_names]

    decoder = sl.LightTransport()
    T = decoder.decode(imlist_code, imlist_observe) # (m*n*co, p*q)
    print("Light Transport Matrix")
    print(T.shape)
    print(T.dtype)

    np.save(f"{dir_name}/light_transport_matrix", T)

if __name__=="__main__":
    main()
