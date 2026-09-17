from fastapi import APIRouter, Depends, File, UploadFile
from core.security import verify_api_key
from schemas.document import DocumentExtractionResponse
from services import document_service
from Utils.image import read_image

router = APIRouter(prefix="/document", tags=["document"], dependencies=[Depends(verify_api_key)])

@router.post("/extract", response_model=DocumentExtractionResponse)
async def extract_document(document: UploadFile = File(...))->DocumentExtractionResponse:
    image = await read_image(document)
    data = document_service.extract_id_document(image)
    return DocumentExtractionResponse(**data)