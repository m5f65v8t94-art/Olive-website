import hashlib
import hmac
import base64
import json
import time
import os
import secrets
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

SECRET_KEY = os.environ.get("OLIVE_SECRET_KEY", "olive-wellbeing-super-secret-key-2026-safe-privacy")

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hash a user password using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Format: salt$hash_hex
    """
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify a plain password against its stored PBKDF2-HMAC-SHA256 hash.
    """
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, expected_hash = stored_hash.split("$", 1)
        calculated_hash = hash_password(plain_password, salt=salt).split("$", 1)[1]
        return secrets.compare_digest(calculated_hash, expected_hash)
    except Exception:
        return False

def hash_pin(pin: str, salt: Optional[str] = None) -> str:
    """
    Hash a 4-to-6 digit privacy PIN using PBKDF2-HMAC-SHA256 with 100,000 iterations.
    Format: salt$hash_hex
    """
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        pin.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}${key.hex()}"

def verify_pin(plain_pin: str, stored_hash: str) -> bool:
    """
    Verify a plain PIN against its stored PBKDF2-HMAC-SHA256 hash.
    """
    try:
        if not stored_hash or "$" not in stored_hash:
            return False
        salt, expected_hash = stored_hash.split("$", 1)
        calculated_hash = hash_pin(plain_pin, salt=salt).split("$", 1)[1]
        return secrets.compare_digest(calculated_hash, expected_hash)
    except Exception:
        return False

def create_access_token(user_id: str, username: str, expires_in_seconds: int = 86400 * 30) -> str:
    """
    Create a cryptographically signed HMAC-SHA256 bearer token.
    Payload: base64(json({user_id, username, exp})) . signature
    """
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": int(time.time()) + expires_in_seconds
    }
    payload_json = json.dumps(payload, separators=(',', ':'))
    b64_payload = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{signature}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a signed bearer token.
    """
    try:
        if not token or "." not in token:
            return None
        parts = token.strip().split(".")
        if len(parts) != 2:
            return None
        b64_payload, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        if not secrets.compare_digest(signature, expected_sig):
            return None
        
        # Add padding back if necessary
        padded = b64_payload + '=' * (-len(b64_payload) % 4)
        payload_data = json.loads(base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8'))
        
        if payload_data.get("exp", 0) < time.time():
            return None
        
        return payload_data
    except Exception:
        return None
