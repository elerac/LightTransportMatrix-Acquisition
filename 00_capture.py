import os

import numpy as np
import cv2
from tqdm import tqdm

import EasyPySpin  # https://github.com/elerac/EasyPySpin
import structuredlight as sl  # https://github.com/elerac/structuredlight
from fullscreen import FullScreen  # https://github.com/elerac/fullscreen


class ProjectorCamera:
    def __init__(self, projector, camera):
        self.projector = projector
        self.camera = camera

        self.DELAY = 250  # ms
        self.BACKGROUND = 0

    def read(self, img_projection):
        self.projector.imshow(img_projection)
        key = cv2.waitKey(self.DELAY)

        if key == -1:
            ret, img_captured = self.camera.read()
            img_captured = cv2.absdiff(img_captured, self.BACKGROUND)
            return ret, img_captured
        else:
            return False, None


def main():
    # Camera settings
    camera = EasyPySpin.VideoCapture(0)

    if not camera.isOpened():
        print("Camera is not opened")
        return -1

    camera.set(cv2.CAP_PROP_EXPOSURE, 8000)
    camera.set(cv2.CAP_PROP_GAIN, 15)
    camera.set(cv2.CAP_PROP_GAMMA, 1)
    camera.set(cv2.CAP_PROP_TRIGGER, True)
    camera.set_pyspin_value("BalanceWhiteAuto", "Off")
    camera.auto_software_trigger_execute = True
    m = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
    n = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Camera ({m}, {n})")

    # Projector settings
    projector = FullScreen()
    p = 16
    q = 9
    print(f"Projector ({p}, {q})")

    # Pro-Cam settings
    procam = ProjectorCamera(projector, camera)
    procam.DELAY = 100

    # Set background
    img_black = np.zeros((q, p, 3), dtype=np.uint8)
    ret, img_background = procam.read(img_black)
    procam.BACKGROUND = img_background

    # Number of captures
    num = int(p * q * 1.2)
    print(f"Number of captures {num}")

    # Output directory
    DIRNAME = f"lighttransport_{n}x{m}x{3}_{q}x{p}"
    os.makedirs(DIRNAME, exist_ok=True)
    print(f"Write images to {DIRNAME}")

    # Generate projection patterns
    stl = sl.LightTransport()
    imlist_code = stl.generate((p, q), num)

    # Start capturing
    imlist_observe = []
    for i, img_code in enumerate(tqdm(imlist_code)):
        ret, img_raw = procam.read(img_code)

        img_observe = cv2.cvtColor(img_raw, cv2.COLOR_BayerBG2BGR)
        img_observe = cv2.resize(img_observe, None, fx=0.25, fy=0.25)
        imlist_observe.append(img_observe)

        cv2.imwrite(f"{DIRNAME}/observe-{i+1}.png", img_observe)
        cv2.imwrite(f"{DIRNAME}/code-{i+1}.png", img_code)


if __name__ == "__main__":
    main()
