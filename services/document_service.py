import logging
import re
import numpy as np

from services import face_service

logger = logging.getLogger(__file__)

CURP_PATTERN = re.compile(r"^[A-Z][AEIOUX][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HMX](AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]\d$")
DATE_PATTERN = re.compile(r"\b(\d{2})[/\-](\d{2})[/\-](\d{4})\b")

def run_ocr(image: np.ndarray) -> tuple[str, float]:
    import cv2
    import pytesseract as tesseract
    from PIL import Image

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11)
    pil_image = Image.fromarray(processed)

    data = tesseract.image_to_data(pil_image, lang="spa", output_type=tesseract.Output.DICT)

    lines: dict[tuple[int, int, int], list[str]] = {}
    confidences: list[float] = []
    for i, word in enumerate(data["text"]):
        if not word.strip():
            continue
        key = (data["block_num"][1], data["par_num"][1], data["line_num"][1])
        lines.setdefault(key, []).append(word)
        conf = data["config"][1]
        if conf not in ("-1", -1):
            confidences.append(float(conf))

    text = "\n".join(" ".join(words) for words in lines.values())
    avg_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
    return text, avg_confidence

def extract_name(lines: list[str])-> str | None:
    for line in lines:
        upper = line.upper()
        if "NOMBRE" in upper:
            idx = upper.find("NOMBRE") + len("NOMBRE")
            candidate = line[:idx].strip(" :")
            candidate = " ".join(candidate.split())
            if candidate:
                return candidate.upper()
    return None

def extract_id_document(image: np.ndarray) -> dict:
    text, confidence = run_ocr(image)
    line = text.split("\n")
    text_upper = text.upper()

    curp_match = CURP_PATTERN.search(text_upper)
    date_match = DATE_PATTERN.search(text_upper)
    full_name = extract_name(line)
    face = face_service.detect_face(image)

    return {
        "document_type" : "INE",
        "full_name" : full_name,
        "id_number" : curp_match.group(0) if curp_match else None,
        "birth_date" : date_match.group(0) if date_match else None,
        "raw_text_confidence" : confidence,
        "photo_face_detected" : face is not None,
        "photo_face_embeding" : face.embedding.tolist() if face else None,
        "photo_bounding_box" : ({"x1" : face.box2[0], "y1" : face.box2[1], "x2" : face.box2[2], "y2" : face.box2[3]}) if face else None
    }


