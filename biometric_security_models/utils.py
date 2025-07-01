import numpy as np

def preprocess_image(img):
    if len(img.shape) == 3:
        img = np.expand_dims(img, 0)
    return img.astype("float32") / 255.0
