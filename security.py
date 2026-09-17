import hmac
from fastapi import Header, HTTPException, status
from core.config import get_settings

async def verify_api_key(api_key: str = Header(default=""))->None:
    settings = get_settings()
    if not hmac.compare_digest(api_key , settings.api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

