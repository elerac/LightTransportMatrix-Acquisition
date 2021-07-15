import os

import numpy as np
import cv2
from tqdm import tqdm

import EasyPySpin  # https://github.com/elerac/EasyPySpin
import structuredlight as sl  # https://github.com/elerac/structuredlight
from fullscreen import FullScreen  # https://github.com/elerac/fullscreen


class ProjectorCamera:
    def __init__(self, projector, camera):
        self.projector = projector  # instance of FullScreen
        self.camera = camera  # instance of VideoCapture

        self.DELAY = 250  # delay time after imshow [ms]
        self.BACKGROUND = 0  # 0 means no background (ambient) light

    def read(self, img_projection):
        self.projector.imshow(img_projection)

        key = cv2.waitKey(self.DELAY)
        if key != -1:
            return False, None

        ret, img_captured = self.camera.read()

        img_captured = cv2.absdiff(img_captured, self.BACKGROUND)

        return ret, img_captured


def main():
    # Parameters of setting
    # Change as necessary to fit your environment
    EXPOSURE_TIME = 8000  # exposure time of camera [us]
    GAIN = 15  # gain value of camera [dB]
    DELAY = 100  # delay time after imshow [ms]
    SCALE = 0.25  # resize scale of captured image
    p = 16  # projector width [pixel]
    q = 9  # projector height [pixel]
    RATIO_OF_ADDITIONAL_CAPTURE = 1.2  # must be >= 1.0
    DIRNAME_BASE = "lighttransport"  # output directory name

    # Camera settings
    camera = EasyPySpin.VideoCapture(0)

    if not camera.isOpened():
        print("Camera is not opened")
        return -1

    camera.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE_TIME)
    camera.set(cv2.CAP_PROP_GAIN, GAIN)
    camera.set(cv2.CAP_PROP_GAMMA, 1)  # 1 means gamma correlation is off
    camera.set(cv2.CAP_PROP_TRIGGER, True)  # change as necessary
    camera.auto_software_trigger_execute = True  # change as necessary
    camera.set_pyspin_value("BalanceWhiteAuto", "Off")  # change as necessary

    m = int(SCALE * camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    n = int(SCALE * camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera ({m}, {n})")

    # Projector settings
    projector = FullScreen()
    print(f"Projector ({p}, {q})")

    # Pro-Cam settings
    procam = ProjectorCamera(projector, camera)
    procam.DELAY = DELAY

    # Set background
    img_black = np.zeros((q, p, 3), dtype=np.uint8)
    ret, img_background = procam.read(img_black)
    procam.BACKGROUND = img_background

    # Number of captures
    # The more increase number of captures,
    # the more estimated LTM becomes robust against noise.
    num = int(p * q * RATIO_OF_ADDITIONAL_CAPTURE)
    print(f"Number of captures {num}")

    # Generate projection patterns
    lt = sl.LightTransport()
    imlist_code = lt.generate((p, q), num)

    # Output directory
    DIRNAME = f"{DIRNAME_BASE}_{n}x{m}x{3}_{q}x{p}"
    os.makedirs(DIRNAME)
    print(f"Write images to {DIRNAME}")

    # Start capturing
    imlist_observe = []
    for i, img_code in enumerate(tqdm(imlist_code)):
        ret, img_raw = procam.read(img_code)

        img_observe = cv2.cvtColor(img_raw, cv2.COLOR_BayerBG2BGR)
        img_observe = cv2.resize(img_observe, None, fx=SCALE, fy=SCALE)

        imlist_observe.append(img_observe)

        cv2.imwrite(f"{DIRNAME}/observe-{i+1}.png", img_observe)
        cv2.imwrite(f"{DIRNAME}/code-{i+1}.png", img_code)


if __name__ == "__main__":
    main()
