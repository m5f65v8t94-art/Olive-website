import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_guest_pin_setup_change_and_verify():
    """Verify guest PIN setup, verification, changing PIN, old PIN invalidation, and new PIN access."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Setup PIN as guest
        res = await client.post("/api/auth/setup-pin", json={"pin": "1234"})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        hashed_pin = data["hashed_pin"]
        assert hashed_pin is not None

        # 2. Verify correct initial PIN
        verify_res = await client.post("/api/auth/verify-pin", json={"pin": "1234", "hashed_pin": hashed_pin})
        assert verify_res.status_code == 200
        assert verify_res.json()["authenticated"] is True

        # 3. Verify wrong current PIN when changing fails
        wrong_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "9999",
            "new_pin": "4321",
            "hashed_pin": hashed_pin
        })
        assert wrong_change.status_code == 401

        # 4. Change PIN with correct current PIN
        change_res = await client.post("/api/auth/change-pin", json={
            "current_pin": "1234",
            "new_pin": "4321",
            "hashed_pin": hashed_pin
        })
        assert change_res.status_code == 200
        new_hashed_pin = change_res.json()["hashed_pin"]
        assert new_hashed_pin is not None

        # 5. Old PIN must FAIL now
        old_verify = await client.post("/api/auth/verify-pin", json={"pin": "1234", "hashed_pin": new_hashed_pin})
        assert old_verify.status_code == 401

        # 6. New PIN must SUCCEED
        new_verify = await client.post("/api/auth/verify-pin", json={"pin": "4321", "hashed_pin": new_hashed_pin})
        assert new_verify.status_code == 200
        assert new_verify.json()["authenticated"] is True

@pytest.mark.asyncio
async def test_authenticated_user_pin_and_history():
    """Verify that a registered user can set up PIN, change PIN, verify old PIN fails, and access their history."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:6]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        reg_res = await client.post("/api/auth/register", json={
            "username": f"pinuser_{uid}",
            "email": f"pinuser_{uid}@example.com",
            "password": "password123"
        })
        assert reg_res.status_code == 200
        token = reg_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup PIN on user account
        set_res = await client.post("/api/auth/setup-pin", json={"pin": "5678"}, headers=headers)
        assert set_res.status_code == 200

        # Verify PIN on user account
        ver_res = await client.post("/api/auth/verify-pin", json={"pin": "5678"}, headers=headers)
        assert ver_res.status_code == 200
        assert ver_res.json()["authenticated"] is True

        # Change PIN with wrong current PIN fails
        bad_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "0000",
            "new_pin": "8765"
        }, headers=headers)
        assert bad_change.status_code == 401

        # Change PIN with correct current PIN succeeds
        good_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "5678",
            "new_pin": "8765"
        }, headers=headers)
        assert good_change.status_code == 200

        # Old PIN fails
        old_ver = await client.post("/api/auth/verify-pin", json={"pin": "5678"}, headers=headers)
        assert old_ver.status_code == 401

        # New PIN succeeds
        new_ver = await client.post("/api/auth/verify-pin", json={"pin": "8765"}, headers=headers)
        assert new_ver.status_code == 200

        # Send a chat message
        chat_res = await client.post("/api/chat/turn", json={
            "message": "Testing private history",
            "mode": "just_listen"
        }, headers=headers)
        assert chat_res.status_code == 200

        # Fetch history sessions
        hist_res = await client.get("/api/chat/sessions", headers=headers)
        assert hist_res.status_code == 200
        sessions = hist_res.json()
        assert len(sessions) >= 1
