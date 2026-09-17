from fastapi import APIRouter, Depends, File, UploadFile
from core.security import verify_api_key
from schemas.plate import PlateReadResponse
from services import plate_service
from Utils.image import read_image

router = APIRouter(prefix="/plate", tags=["plate"], dependencies=[Depends(verify_api_key)])

@router.post("/plate", response_model=PlateReadResponse)
async def plate(file: UploadFile = File(...))->PlateReadResponse:
    image = await read_image(file)
    data = plate_service.read_plate(image)
    return PlateReadResponse(**data)

