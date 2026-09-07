from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any
from app.utils.security import hash_pin, verify_pin

router = APIRouter(prefix="/api/history", tags=["Protected History & PIN"])

class PinSetupRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")

class PinVerifyRequest(BaseModel):
    pin: str
    hashed_pin: str

@router.post("/hash-pin")
async def create_hashed_pin(request: PinSetupRequest) -> Dict[str, str]:
    """Generates a secure bcrypt hash for the user-selected privacy PIN."""
    hashed = hash_pin(request.pin)
    return {"hashed_pin": hashed}

@router.post("/verify-pin")
async def verify_privacy_pin(request: PinVerifyRequest) -> Dict[str, Any]:
    """Validates entered PIN against the device's stored bcrypt hash."""
    is_valid = verify_pin(request.pin, request.hashed_pin)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN. Please try again."
        )
    return {"authenticated": True, "message": "Access granted to conversation history."}
