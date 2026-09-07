import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_auth_registration_login_and_pin():
    transport = ASGITransport(app=app)
    uid1 = uuid.uuid4().hex[:8]
    uid2 = uuid.uuid4().hex[:8]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register User 1
        reg_res1 = await client.post("/api/auth/register", json={
            "username": f"teen_{uid1}",
            "email": f"teen_{uid1}@example.com",
            "password": "Password123!"
        })
        assert reg_res1.status_code == 200, reg_res1.text
        data1 = reg_res1.json()
        token1 = data1["token"]
        assert "token" in data1
        assert data1["user"]["username"] == f"teen_{uid1}"

        # 2. Setup PIN for User 1
        pin_res = await client.post(
            "/api/auth/setup-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"pin": "1234"}
        )
        assert pin_res.status_code == 200
        assert pin_res.json()["success"] is True

        # 3. Verify correct PIN
        v_res = await client.post(
            "/api/auth/verify-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"pin": "1234"}
        )
        assert v_res.status_code == 200
        assert v_res.json()["authenticated"] is True

        # 4. Verify incorrect PIN
        v_bad = await client.post(
            "/api/auth/verify-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"pin": "9999"}
        )
        assert v_bad.status_code == 401

        # 5. Change PIN
        ch_res = await client.post(
            "/api/auth/change-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"current_pin": "1234", "new_pin": "5678"}
        )
        assert ch_res.status_code == 200

        # Old PIN fails
        v_old = await client.post(
            "/api/auth/verify-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"pin": "1234"}
        )
        assert v_old.status_code == 401

        # New PIN works
        v_new = await client.post(
            "/api/auth/verify-pin",
            headers={"Authorization": f"Bearer {token1}"},
            json={"pin": "5678"}
        )
        assert v_new.status_code == 200

        # 6. User 2 Isolation Check
        reg_res2 = await client.post("/api/auth/register", json={
            "username": f"teen_{uid2}",
            "email": f"teen_{uid2}@example.com",
            "password": "Password456!"
        })
        assert reg_res2.status_code == 200
        token2 = reg_res2.json()["token"]

        # User 1 creates journal
        j_res1 = await client.post(
            "/api/journal",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "Private Entry User 1", "content": "Secret diary"}
        )
        assert j_res1.status_code == 200

        # User 2 lists journals -> should NOT see User 1's entry
        j_res2 = await client.get(
            "/api/journal",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert j_res2.status_code == 200
        assert len(j_res2.json()) == 0
