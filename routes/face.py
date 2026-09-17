from fastapi import APIRouter, Depends, File, UploadFile
from core.config import get_settings
from core.security import verify_api_key
from schemas.face import (Box, Face, FaceCompareRequest, FaceCompareResponse)
from services import face_service
from Utils.image import read_image

router = APIRouter(
    prefix="/face",
    tags=["face"],
    dependencies=[Depends(verify_api_key)],
)

@router.post("/embed", response_model=Face)
async def face_embed(file: UploadFile = File(...))->Face:
    image = await read_image(file)
    face = face_service.detect_face(image)
    if face is None:
        return Face(Face_detected=False)
    return Face(Face_detected=True, detection_confidence = face.confidence, bounding_box = Box(x1=face.box2[0], y1 = face.box2[1], x2=face.box2[2], y2=face.box2[3]), embedding = face.embedding.tolist())

@router.post("/compare", response_model=FaceCompareResponse)
async def compare_faces(payload: FaceCompareRequest)->FaceCompareResponse:
    settings = get_settings()
    similarity = face_service.similarity(payload.face1, payload.face2)
    return FaceCompareResponse(similarity=similarity, is_match=face_service.is_matching(similarity), threshold_used=settings.face_match)