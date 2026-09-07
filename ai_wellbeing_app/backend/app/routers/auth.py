from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.user import UserModel
from app.utils.security import (
    hash_password,
    verify_password,
    hash_pin,
    verify_pin,
    create_access_token,
    decode_access_token
)

router = APIRouter(prefix="/api/auth", tags=["Authentication & User Security"])

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class PinSetupRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")

class PinVerifyRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")
    hashed_pin: Optional[str] = None

class PinChangeRequest(BaseModel):
    current_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")
    new_pin: str = Field(..., min_length=4, max_length=6, pattern=r"^\d{4,6}$")
    hashed_pin: Optional[str] = None

class GoogleLoginRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    name: Optional[str] = None
    credential: Optional[str] = None
    google_id: Optional[str] = None

class AuthResponse(BaseModel):
    token: str
    user: Dict[str, Any]

async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[UserModel]:
    """Resolves authenticated user from Bearer header if provided."""
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        return None
    
    stmt = select(UserModel).where(UserModel.id == payload["user_id"])
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> UserModel:
    """Strictly enforces authentication for protected endpoints."""
    user = await get_current_user_optional(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to continue."
        )
    return user

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new private user account."""
    clean_username = request.username.strip()
    clean_email = request.email.strip().lower()

    # Check existing user
    stmt = select(UserModel).where(
        (UserModel.username == clean_username) | (UserModel.email == clean_email)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with that username or email already exists."
        )

    new_user = UserModel(
        id=str(uuid.uuid4()),
        username=clean_username,
        email=clean_email,
        hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(new_user.id, new_user.username)
    return AuthResponse(
        token=token,
        user={
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "has_pin": bool(new_user.pin_hash),
            "created_at": new_user.created_at.isoformat()
        }
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Log in to an existing user account."""
    query_id = request.username_or_email.strip()
    stmt = select(UserModel).where(
        (UserModel.username == query_id) | (UserModel.email == query_id.lower())
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    token = create_access_token(user.id, user.username)
    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "has_pin": bool(user.pin_hash),
            "created_at": user.created_at.isoformat()
        }
    )

@router.post("/google", response_model=AuthResponse)
async def google_login(request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate or register a user via Google Sign-In."""
    clean_email = request.email.strip().lower()
    stmt = select(UserModel).where(UserModel.email == clean_email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raw_name = request.name or clean_email.split("@")[0]
        base_username = "".join(c for c in raw_name if c.isalnum() or c in "_-").strip()
        if len(base_username) < 3:
            base_username = f"user_{base_username}"[:15]
        
        username = base_username
        counter = 1
        while True:
            u_stmt = select(UserModel).where(UserModel.username == username)
            u_res = await db.execute(u_stmt)
            if not u_res.scalar_one_or_none():
                break
            username = f"{base_username}_{counter}"
            counter += 1

        import secrets
        user = UserModel(
            id=str(uuid.uuid4()),
            username=username,
            email=clean_email,
            hashed_password=hash_password(secrets.token_hex(16))
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = create_access_token(user.id, user.username)
    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "has_pin": bool(user.pin_hash),
            "created_at": user.created_at.isoformat()
        }
    )

@router.get("/me")
async def get_me(user: UserModel = Depends(get_current_user)):
    """Return profile info of currently logged in user."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "has_pin": bool(user.pin_hash),
        "created_at": user.created_at.isoformat()
    }

@router.post("/setup-pin")
async def setup_pin(
    request: PinSetupRequest,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Setup or reset the Protected History privacy PIN."""
    new_hash = hash_pin(request.pin)
    if current_user:
        current_user.pin_hash = new_hash
        await db.commit()
    return {
        "success": True,
        "has_pin": True,
        "hashed_pin": new_hash,
        "message": "Privacy PIN configured securely."
    }

@router.post("/verify-pin")
async def verify_privacy_pin(
    request: PinVerifyRequest,
    current_user: Optional[UserModel] = Depends(get_current_user_optional)
):
    """
    Validates entered PIN against user's stored hash or device hash.
    Used every time Protected History is opened.
    """
    target_hash = None
    if current_user and current_user.pin_hash:
        target_hash = current_user.pin_hash
    elif request.hashed_pin:
        target_hash = request.hashed_pin

    if not target_hash:
        return {"authenticated": True, "message": "No PIN configured yet."}

    if not verify_pin(request.pin, target_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN. Please try again."
        )

    return {"authenticated": True, "message": "PIN verified successfully."}

@router.post("/change-pin")
async def change_privacy_pin(
    request: PinChangeRequest,
    current_user: Optional[UserModel] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Securely change the Protected History PIN after validating the current PIN."""
    if current_user:
        if current_user.pin_hash:
            if not verify_pin(request.current_pin, current_user.pin_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current PIN is incorrect."
                )
        elif request.hashed_pin:
            if not verify_pin(request.current_pin, request.hashed_pin):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current PIN is incorrect."
                )
        new_hash = hash_pin(request.new_pin)
        current_user.pin_hash = new_hash
        await db.commit()
        return {"success": True, "hashed_pin": new_hash, "message": "PIN updated successfully."}
    else:
        if request.hashed_pin:
            if not verify_pin(request.current_pin, request.hashed_pin):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Current PIN is incorrect."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No existing PIN found to change. Please set up a PIN first."
            )
        new_hash = hash_pin(request.new_pin)
        return {"success": True, "hashed_pin": new_hash, "message": "PIN updated successfully."}
