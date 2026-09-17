from pydantic import BaseModel, Field

class Box(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class Face(BaseModel):
    Face_detected: bool
    detection_confidence: float | None = None
    bounding_box: Box | None = None
    embedding: list[float] | None = Field(default = None, description="Face vector, null if no face was detected")

class FaceCompareRequest(BaseModel):
    face1: list[float]
    face2: list[float]

class FaceCompareResponse(BaseModel):
    similarity: float
    is_match: bool
    threshold_used:float