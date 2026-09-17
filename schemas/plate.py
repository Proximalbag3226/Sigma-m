from pydantic import BaseModel
from schemas.face import Box

class PlateReadRequest(BaseModel):
    plate_detected: bool
    plate_text: str | None = None
    confidence: float | None = None
    bounding_box: Box | None = None

class PlateReadResponse(BaseModel):
    plate_detected: bool
    plate_text: str | None = None
