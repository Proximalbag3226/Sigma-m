import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)

MIN_ASPECT_RADIO = 2.0
MAX_ASPECT_RADIO = 5.5
MIN_PLATE_WIDTH = 20

def find_plate_candidates(image: np.ndarray) -> list[tuple[int, int, int]]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.bilateralFilter(gray, 11, 17, 17)
    edges = cv2.Canny(blurred, 30, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < MIN_PLATE_WIDTH or h == 0:
            continue
        aspect_ratio = w / h
        if MIN_ASPECT_RADIO <= aspect_ratio <= MAX_ASPECT_RADIO:
            candidates.append((x, y, w, h))

    candidates.sort(key=lambda box: box[2] * box[3], reverse=True)
    return candidates[:3]

def read_plate(image: np.ndarray) -> dict:
    import pytesseract as pt
    candidates = find_plate_candidates(image)
    if not candidates:
        return {
            "plate_detected": False,
            "plate_text": None,
            "plate_confidence": None,
            "bounding_box": None
        }
    x,y,w,h = candidates[0]
    crop = image[y:y + h, x:x + w]
    gray_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = "--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raw_text = pt.image_to_string(thresh, config=config)
    text = "".join(ch for ch in raw_text.strip().upper() if ch.isalnum())

    bounding_box = {"x1": x, "y1": y, "x2": x + w, "y2": y + h}
    if not text:
        return {
            "plate_detected": False,
            "plate_text": None,
            "confidence": 0.0,
            "bounding_box": bounding_box
        }

    return {
        "plate_detected": True,
        "plate_text": text,
        "confidence": 0.5,
        "bounding_box": bounding_box
    }

