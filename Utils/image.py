import os
import tempfile
from contextlib import contextmanager
from typing import Iterator
import numpy as np
from fastapi import HTTPException, UploadFile, status
from core.config import get_settings

async def read_image(fle: UploadFile) -> np.ndarray:
    import cv2
    settings = get_settings()

    if fle.content_type not in settings.allowed_content_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="File type not allowed")

    raw = await fle.read()
    if not raw:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    if len(raw) > settings.max_upload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too big")

    buffer = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant read image, please verify that the file is in a valid format")
    return image

@contextmanager
def temp_file(suffix: str = "jpg")->Iterator[str]:
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    os.chmod(path, 0o600)
    try:
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)