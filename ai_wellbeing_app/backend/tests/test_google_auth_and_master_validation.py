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
async def test_google_sign_in_and_pin_flow():
    """Verify Google sign-in creates account, retrieves profile, sets/changes PIN, and manages history."""
    transport = ASGITransport(app=app)
    uid = uuid.uuid4().hex[:6]
    google_email = f"student_{uid}@gmail.com"
    
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sign in with Google (First time -> auto registers)
        res = await client.post("/api/auth/google", json={
            "email": google_email,
            "name": f"Student {uid}"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["token"] is not None
        assert data["user"]["email"] == google_email
        token = data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check /me
        me_res = await client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == google_email
        assert me_res.json()["has_pin"] is False

        # 3. Google Sign in again (Existing user -> logs in)
        login_res = await client.post("/api/auth/google", json={
            "email": google_email,
            "name": f"Student {uid}"
        })
        assert login_res.status_code == 200
        assert login_res.json()["user"]["id"] == data["user"]["id"]

        # 4. Set up PIN on Google user account
        set_pin_res = await client.post("/api/auth/setup-pin", json={"pin": "2468"}, headers=headers)
        assert set_pin_res.status_code == 200
        assert set_pin_res.json()["has_pin"] is True

        # 5. Verify PIN
        ver_res = await client.post("/api/auth/verify-pin", json={"pin": "2468"}, headers=headers)
        assert ver_res.status_code == 200

        # 6. Change PIN: test rejection of wrong current PIN
        wrong_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "1111",
            "new_pin": "1357"
        }, headers=headers)
        assert wrong_change.status_code == 401

        # 7. Change PIN: correct current PIN
        good_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "2468",
            "new_pin": "1357"
        }, headers=headers)
        assert good_change.status_code == 200

        # 8. Verify old PIN fails
        old_ver = await client.post("/api/auth/verify-pin", json={"pin": "2468"}, headers=headers)
        assert old_ver.status_code == 401

        # 9. Verify new PIN succeeds
        new_ver = await client.post("/api/auth/verify-pin", json={"pin": "1357"}, headers=headers)
        assert new_ver.status_code == 200

@pytest.mark.asyncio
async def test_tell_someone_format_adaptation_flow():
    """Verify that Help Me Tell Someone remembers format selection (e.g. in person or text)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1: User mentions wanting to talk to Mom about school stress
        t1 = await client.post("/api/chat/turn", json={
            "message": "I want to talk to my mom about school stress and feeling overwhelmed",
            "mode": "help_me_tell_someone"
        })
        assert t1.status_code == 200
        session_id = t1.json()["session_id"]
        t1_reply = t1.json()["assistant_message"]["content"]
        assert "mom" in t1_reply.lower()

        # Turn 2: User selects format 'in person'
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "in person",
            "mode": "help_me_tell_someone"
        })
        assert t2.status_code == 200
        t2_reply = t2.json()["assistant_message"]["content"]
        assert "in-person" in t2_reply.lower() or "in person" in t2_reply.lower() or "face-to-face" in t2_reply.lower()
        # Should provide direct opening lines/steps
        assert "mom" in t2_reply.lower()

@pytest.mark.asyncio
async def test_safety_deescalation_and_india_hotlines():
    """Verify safety interceptor returns India hotlines and transitions topic upon adult presence."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Suicidal ideation turn -> returns India hotlines & trusted adult guidance
        t1 = await client.post("/api/chat/turn", json={
            "message": "I've been having suicidal thoughts lately",
            "mode": "just_listen"
        })
        assert t1.status_code == 200
        t1_reply = t1.json()["assistant_message"]["content"]
        assert "14416" in t1_reply or "Tele-MANAS" in t1_reply
        assert "1098" in t1_reply or "Child Helpline" in t1_reply
        assert "112" in t1_reply
        assert "trusted adult" in t1_reply.lower()

        session_id = t1.json()["session_id"]

        # 2. User gets mom to stay with them and wants to talk about what happened at school
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I got my mom to stay with me in my room. Can I tell you what happened at school today?",
            "mode": "just_listen"
        })
        assert t2.status_code == 200
        t2_reply = t2.json()["assistant_message"]["content"]
        # Must acknowledge mom being with user and follow new topic naturally
        assert "mom" in t2_reply.lower()
        assert "school" in t2_reply.lower()
        # Must NOT re-paste emergency numbers
        assert "14416" not in t2_reply
