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
async def test_complete_olive_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Test Static Index & Assets Serving
        index_res = await client.get("/")
        assert index_res.status_code == 200
        assert "Olive" in index_res.text
        assert "Quick Privacy Hide" in index_res.text
        assert "btn-theme-toggle" in index_res.text
        assert "btn-change-pin-modal" not in index_res.text

        # 2. Test Get Help Privately (India Helplines)
        resources_res = await client.get("/api/resources/private-help")
        assert resources_res.status_code == 200
        res_data = resources_res.json()
        service_names = [s["name"] for s in res_data.get("services", [])]
        assert "Tele-MANAS" in service_names
        assert "Child Helpline" in service_names
        assert "Meri Trustline" in service_names
        assert "National Cyber Crime Helpline" in service_names
        assert "Emergency Services" in service_names
        # Ensure 988 is NOT in resources
        assert not any("988" in s.get("phone", "") for s in res_data.get("services", []))

        # 3. Test Study Notes for Quick Privacy Hide
        study_res = await client.get("/api/resources/study-notes")
        assert study_res.status_code == 200
        notes = study_res.json()
        assert len(notes) >= 1
        assert "Cell Structure" in notes[0]["topic"] or "Biology" in notes[0]["subject"]

        # 4. Test 4 Modes of Liv AI
        modes_res = await client.get("/api/chat/modes")
        assert modes_res.status_code == 200
        modes = [m["id"] for m in modes_res.json()]
        assert "just_listen" in modes
        assert "give_me_advice" in modes
        assert "help_me_understand" in modes
        assert "help_me_tell_someone" in modes

        # 4a. Mode 1: Just Listen
        sess_id = str(uuid.uuid4())
        listen_res = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "I have a big biology exam tomorrow and I feel so stressed",
            "mode": "just_listen"
        })
        assert listen_res.status_code == 200
        l_data = listen_res.json()
        assert l_data["assistant_message"]["role"] == "assistant"
        assert len(l_data["assistant_message"]["content"]) > 10

        # 4b. Mode 2: Give Me Advice
        advice_res = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "What is one small thing I can do right now to prepare?",
            "mode": "give_me_advice"
        })
        assert advice_res.status_code == 200
        adv_data = advice_res.json()
        assert adv_data["assistant_message"]["role"] == "assistant"

        # 4c. Mode 3: Help Me Understand
        und_res = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "Why do I always put off studying until the last night?",
            "mode": "help_me_understand"
        })
        assert und_res.status_code == 200

        # 4d. Mode 4: Help Me Tell Someone
        tell_res = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "Can you help me tell my mom that I am struggling with school stress?",
            "mode": "help_me_tell_someone"
        })
        assert tell_res.status_code == 200

        # 5. Test Conversation Title Editing (In-Place, No Redirect)
        rename_res = await client.patch(f"/api/chat/sessions/{sess_id}", json={
            "title": "Biology Exam Preparation & Support"
        })
        assert rename_res.status_code == 200
        assert rename_res.json()["title"] == "Biology Exam Preparation & Support"

        # 6. Test Account Registration, Login, and Authenticated Session
        test_uid = uuid.uuid4().hex[:6]
        user_payload = {
            "username": f"olive_user_{test_uid}",
            "email": f"olive_{test_uid}@school.org",
            "password": "SecurePassword123!"
        }
        reg_res = await client.post("/api/auth/register", json=user_payload)
        assert reg_res.status_code == 200
        auth_data = reg_res.json()
        token = auth_data["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Verify /api/auth/me
        me_res = await client.get("/api/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["username"] == user_payload["username"]

        # 7. Test Setup PIN, Change PIN, Old PIN Invalidation, and New PIN Verification
        # Setup PIN 1234
        pin_setup = await client.post("/api/auth/setup-pin", json={"pin": "1234"}, headers=headers)
        assert pin_setup.status_code == 200

        # Verify PIN 1234 works
        ver_ok = await client.post("/api/auth/verify-pin", json={"pin": "1234"}, headers=headers)
        assert ver_ok.status_code == 200
        assert ver_ok.json()["authenticated"] is True

        # Change PIN: Bad current PIN (9999) fails
        bad_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "9999",
            "new_pin": "4321"
        }, headers=headers)
        assert bad_change.status_code == 401

        # Change PIN: Good current PIN (1234) to new PIN (4321) succeeds
        good_change = await client.post("/api/auth/change-pin", json={
            "current_pin": "1234",
            "new_pin": "4321"
        }, headers=headers)
        assert good_change.status_code == 200

        # Verify Old PIN 1234 fails with 401
        old_pin_ver = await client.post("/api/auth/verify-pin", json={"pin": "1234"}, headers=headers)
        assert old_pin_ver.status_code == 401

        # Verify New PIN 4321 succeeds with 200
        new_pin_ver = await client.post("/api/auth/verify-pin", json={"pin": "4321"}, headers=headers)
        assert new_pin_ver.status_code == 200
        assert new_pin_ver.json()["authenticated"] is True

        # 8. Test Journal Save, Reopen, and Delete
        j_create = await client.post("/api/journal", json={
            "title": "Evening Reflection",
            "content": "Today felt busy, but taking a quiet moment helped."
        }, headers=headers)
        assert j_create.status_code == 200
        j_id = j_create.json()["id"]

        j_list = await client.get("/api/journal", headers=headers)
        assert j_list.status_code == 200
        assert any(j["id"] == j_id for j in j_list.json())

        j_update = await client.put(f"/api/journal/{j_id}", json={
            "title": "Evening Reflection (Updated)",
            "content": "Updated content: Feeling much calmer now."
        }, headers=headers)
        assert j_update.status_code == 200

        j_del = await client.delete(f"/api/journal/{j_id}", headers=headers)
        assert j_del.status_code in [200, 204]

        # 9. Test Feelings Check-in
        mood_res = await client.post("/api/mood", json={
            "mood_score": 4,
            "mood_label": "Calm",
            "emotion_tags": ["Calm", "Happy"],
            "notes": "Finished my study session"
        }, headers=headers)
        assert mood_res.status_code == 200

        mood_hist = await client.get("/api/mood/history", headers=headers)
        assert mood_hist.status_code == 200
        assert len(mood_hist.json()) >= 1

        # 10. Test Single and Purge Session Deletion
        del_sess = await client.delete(f"/api/chat/sessions/{sess_id}", headers=headers)
        assert del_sess.status_code in [200, 204]

        purge_res = await client.delete("/api/chat/sessions", headers=headers)
        assert purge_res.status_code in [200, 204]
