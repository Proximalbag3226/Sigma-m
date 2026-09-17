from pydantic import BaseModel
from schemas.face import Box

class DocumentExtractionResponse(BaseModel):
    document_type: str
    full_name : str | None = None
    id_numer: str | None = None
    birth_date: str | None = None
    raw_text: float | None = None
    photo_detected : bool= False
    photo_face_embedding: list[float] | None = None
    photo_box: Box | None = None