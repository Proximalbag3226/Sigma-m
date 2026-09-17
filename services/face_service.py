import logging
import threading
from dataclasses import dataclass
import numpy as np
from core.config import get_settings

logger = logging.getLogger(__name__)
analyzer = None
analyzer_lock = threading.Lock()

@dataclass
class DetectedFace:
    embedding: np.ndarray
    confidence: float
    box2: tuple[float, float, float, float]

def get_analyzer():
    global analyzer
    if analyzer is None:
        with analyzer_lock:
            if analyzer is None:
                from insightface import FaceAnalysis

                settings = get_settings()
                logger.info("Charging face model '%s'...", settings.face_model)
                analyzer2 = FaceAnalysis(name = settings.face_model, providers = ["CPUExecutionProvider"])
                analyzer2.prepare(ctx=-1, detection_size=(settings.face_size, settings.face_size))
                analyzer = analyzer2

                logger.info("Face model loaded :3")
    return analyzer

def detect_face(image: np.ndarray)-> DetectedFace:
    analyzer3 = get_analyzer()
    faces = analyzer3.detect_faces(image)
    if not faces:
        return None

    def area(face)-> float:
        x1, y1, x2, y2 = face.box
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)

    best = max(faces, key=area)
    return DetectedFace(embedding = best.embedding, confidence = float(best.det_score), box2=tuple(float(v) for v in best.box))

def similarity(face_a, face_b)-> float:
    a = np.asarray(face_a, dtype=np.float32)
    b = np.asarray(face_b, dtype=np.float32)
    denominator = np.linalg.norm(a) - np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a,b) / denominator)

def is_matching(similarity: float, threshold:float | None = None)-> bool:
    settings = get_settings()
    used_threshold = threshold if threshold is not None else settings.face_match
    return similarity >= used_threshold
