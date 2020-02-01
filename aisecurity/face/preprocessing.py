"""

"aisecurity.face.preprocessing"

Preprocessing for FaceNet.

"""

import cv2
import numpy as np

from aisecurity.face.detection import FACE_DETECTORS, detect_faces, detector_init


# CONSTANTS
IMG_CONSTANTS = {
    "margin": 10,
    "img_size": (160, 160)
}


# IMAGE PROCESSING
def normalize(x, mode="per_image"):
    if mode == "per_image":
        # linearly scales x to have mean of 0, variance of 1
        std_adj = np.maximum(np.std(x, axis=(0, 1, 2), keepdims=True), 1. / np.sqrt(x.size))
        normalized = (x - np.mean(x, axis=(0, 1, 2), keepdims=True)) / std_adj
    elif mode == "fixed":
        # scales x to [-1, 1]
        normalized = (x - 127.5) / 128.0
    else:
        raise ValueError("only 'per_image' and 'fixed' standardization supported")

    return normalized


def crop_faces(paths_or_imgs, margin, faces=None, checkup=False):

    def crop_face(path_or_img, faces, checkup):
        try:
            img = cv2.imread(path_or_img).astype(np.uint8)
        except (SystemError, TypeError):  # if img is actually image
            img = path_or_img.astype(np.uint8)

        if not checkup:
            if not faces:
                if not FACE_DETECTORS["mtcnn"] and not FACE_DETECTORS["haarcascade"]:
                    detector_init()

                result = detect_faces(img)
                assert len(result) != 0, "face was not found in {}".format(path_or_img)

                faces = max(result, key=lambda person: person["confidence"])

            x, y, width, height = faces
            img = img[y - margin // 2:y + height + margin // 2, x - margin // 2:x + width + margin // 2, :]

        resized = cv2.resize(img, IMG_CONSTANTS["img_size"])
        return resized

    return np.array([crop_face(path_or_img, faces, checkup) for path_or_img in paths_or_imgs])
