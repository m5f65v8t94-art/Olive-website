import pytest
import re
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.utils.constants import GET_HELP_PRIVATELY_GUIDANCE, CRISIS_RESOURCES, STUDY_NOTES_SUBJECTS
from app.services.local_engine import local_engine
from app.services.safety_service import safety_service

@pytest.mark.asyncio
async def test_30_spec_item_1_and_2_logo_and_title():
    # Verify index.html contains the brand home link for logo and title
    with open("app/static/index.html", "r") as f:
        html = f.read()
    assert 'id="brand-home-link"' in html
    assert 'class="brand-logo-img"' in html
    assert 'class="brand-name"' in html
    assert "/static/olive_logo.png" in html

@pytest.mark.asyncio
async def test_30_spec_item_3_and_4_quick_privacy_hide_decoy():
    # Verify study notes disguise has realistic content and NO mention of mental health, therapy, olive, liv
    with open("app/static/index.html", "r") as f:
        html = f.read()
    
    # Check decoy container
    assert 'id="privacy-hide-overlay"' in html
    assert 'StudyNotes • Academic Workspace' in html
    assert 'Grade 11 Biology' in html
    assert 'Cell Structure &amp; Organelles' in html or 'Cell Structure & Organelles' in html
    assert 'study-scratchpad' in html
    
    # Extract decoy section
    decoy_start = html.find('id="privacy-hide-overlay"')
    decoy_end = html.find('<!-- Main Application Script -->')
    decoy_html = html[decoy_start:decoy_end].lower()
    
    # Ensure no forbidden words in decoy
    for forbidden in ["olive", "liv", "mental health", "wellbeing", "therapy", "counselling", "counseling", "chatbot", "privacy mode"]:
        assert forbidden not in decoy_html, f"Forbidden word '{forbidden}' found in decoy"

@pytest.mark.asyncio
async def test_30_spec_item_5_6_7_auth_signup_signin_persistence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        import uuid
        uname = f"testuser_{uuid.uuid4().hex[:6]}"
        email = f"{uname}@example.com"
        pwd = "SecurePassword123!"

        # Sign Up
        res_reg = await client.post("/api/auth/register", json={
            "username": uname,
            "email": email,
            "password": pwd
        })
        assert res_reg.status_code == 200
        token1 = res_reg.json()["token"]

        # Sign In
        res_login = await client.post("/api/auth/login", json={
            "username_or_email": uname,
            "password": pwd
        })
        assert res_login.status_code == 200
        token2 = res_login.json()["token"]
        assert token2 is not None

        # Verify profile persistence
        res_me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token2}"})
        assert res_me.status_code == 200
        assert res_me.json()["username"] == uname

@pytest.mark.asyncio
async def test_30_spec_item_8_9_conversation_persistence():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        import uuid
        uname = f"conv_user_{uuid.uuid4().hex[:6]}"
        email = f"{uname}@example.com"
        pwd = "Password123!"

        res_reg = await client.post("/api/auth/register", json={"username": uname, "email": email, "password": pwd})
        token = res_reg.json()["token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Send message
        res_msg = await client.post("/api/chat/turn", json={
            "message": "I'm having a quiet afternoon today.",
            "mode": "just_listen"
        }, headers=auth_headers)
        assert res_msg.status_code == 200
        sess_id = res_msg.json()["session_id"]

        # List sessions
        res_sess = await client.get("/api/chat/sessions", headers=auth_headers)
        assert res_sess.status_code == 200
        sessions = res_sess.json()
        assert any(s["id"] == sess_id for s in sessions)

        # Get messages in session
        res_msgs = await client.get(f"/api/chat/sessions/{sess_id}/messages", headers=auth_headers)
        assert res_msgs.status_code == 200
        assert len(res_msgs.json()) >= 2

@pytest.mark.asyncio
async def test_30_spec_item_10_and_11_pin_and_change_pin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        import uuid
        uname = f"pin_user_{uuid.uuid4().hex[:6]}"
        email = f"{uname}@example.com"
        pwd = "Password123!"

        res_reg = await client.post("/api/auth/register", json={"username": uname, "email": email, "password": pwd})
        token = res_reg.json()["token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Setup PIN 1234
        res_pin = await client.post("/api/auth/setup-pin", json={"pin": "1234"}, headers=auth_headers)
        assert res_pin.status_code == 200

        # Verify PIN 1234
        res_ver = await client.post("/api/auth/verify-pin", json={"pin": "1234"}, headers=auth_headers)
        assert res_ver.status_code == 200
        assert res_ver.json()["authenticated"] is True

        # Incorrect PIN fails
        res_bad = await client.post("/api/auth/verify-pin", json={"pin": "9999"}, headers=auth_headers)
        assert res_bad.status_code == 401

        # Change PIN: Current=1234, New=5678
        res_chg = await client.post("/api/auth/change-pin", json={"current_pin": "1234", "new_pin": "5678"}, headers=auth_headers)
        assert res_chg.status_code == 200

        # Old PIN 1234 no longer works
        res_old = await client.post("/api/auth/verify-pin", json={"pin": "1234"}, headers=auth_headers)
        assert res_old.status_code == 401

        # New PIN 5678 works
        res_new = await client.post("/api/auth/verify-pin", json={"pin": "5678"}, headers=auth_headers)
        assert res_new.status_code == 200

@pytest.mark.asyncio
async def test_30_spec_item_12_just_listen_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat/turn", json={
            "message": "I've had such a terrible day at school.",
            "mode": "just_listen"
        })
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["school", "terrible", "listening", "what happened"])
        assert "1." not in content  # No unsolicited list
        assert "?" in content

@pytest.mark.asyncio
async def test_30_spec_item_13_give_me_advice_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat/turn", json={
            "message": "I keep putting off my homework even though I know it's important.",
            "mode": "give_me_advice"
        })
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["homework", "micro", "timer", "start", "putting off", "resistance"])
        assert "1." in content

@pytest.mark.asyncio
async def test_30_spec_item_14_help_me_understand_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat/turn", json={
            "message": "Why do I keep procrastinating even when I know my homework is important?",
            "mode": "help_me_understand"
        })
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert "here is why" in content.lower()
        # No clinical diagnosing
        assert not any(d in content.lower() for d in ["you have adhd", "you have clinical depression", "you have anxiety disorder"])

@pytest.mark.asyncio
async def test_30_spec_item_15_help_me_tell_someone_format_memory():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1
        res1 = await client.post("/api/chat/turn", json={
            "message": "I want to tell my dad that I've been really stressed about school, but I don't know how.",
            "mode": "help_me_tell_someone"
        })
        assert res1.status_code == 200
        sess_id = res1.json()["session_id"]

        # Turn 2: User says "Person"
        res2 = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "Person",
            "mode": "help_me_tell_someone"
        })
        assert res2.status_code == 200
        content2 = res2.json()["assistant_message"]["content"]
        assert "dad" in content2.lower()
        assert any(w in content2.lower() for w in ["in-person", "in person", "face-to-face", "face to face", "step 1", "opening"])
        assert "would you feel most comfortable doing this in person" not in content2.lower()

@pytest.mark.asyncio
async def test_30_spec_item_16_to_21_safety_and_topic_switching():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 17. Initial disclosure
        res1 = await client.post("/api/chat/turn", json={
            "message": "I've been having thoughts about suicide lately, and I don't know who I can talk to about it.",
            "mode": "just_listen"
        })
        assert res1.status_code == 200
        c1 = res1.json()["assistant_message"]["content"]
        assert any(w in c1 for w in ["14416", "1098", "112"])
        assert "safe" in c1.lower()
        assert "exhausted" not in c1.lower()  # No invented feeling
        sess_id = res1.json()["session_id"]

        # 18. User says safe right now
        res2 = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "I'm safe right now, but I really don't want to tell anyone.",
            "mode": "just_listen"
        })
        assert res2.status_code == 200
        c2 = res2.json()["assistant_message"]["content"]
        assert "glad to hear that you are safe" in c2.lower()

        # 19. Increased urgency
        res3 = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "Actually, I'm not sure I can keep myself safe tonight.",
            "mode": "just_listen"
        })
        assert res3.status_code == 200
        c3 = res3.json()["assistant_message"]["content"]
        assert any(w in c3.lower() for w in ["urgent", "112", "trusted adult right now", "not stay alone"])

        # 20. Support person present (Mom with user)
        res4 = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "I got my mom to stay with me. I'm still really upset though, and I just want to talk.",
            "mode": "just_listen"
        })
        assert res4.status_code == 200
        c4 = res4.json()["assistant_message"]["content"]
        assert "mom" in c4.lower()
        assert any(w in c4.lower() for w in ["listening", "upset", "with you", "talk"])
        assert "112" not in c4  # Shifts to listening without repeating emergency numbers

        # 21. Topic change to school
        res5 = await client.post("/api/chat/turn", json={
            "session_id": sess_id,
            "message": "My mom is here with me now. I don't want to talk about the safety stuff anymore. I just want to tell you what happened at school today.",
            "mode": "just_listen"
        })
        assert res5.status_code == 200
        c5 = res5.json()["assistant_message"]["content"]
        assert "school" in c5.lower()
        assert "what happened at school" in c5.lower()

@pytest.mark.asyncio
async def test_30_spec_item_22_23_24_get_help_privately():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/resources/private-help")
        assert res.status_code == 200
        data = res.json()
        
        # 22. Trusted adult notice
        assert "trusted adult" in data["trusted_adult_notice"].lower()
        assert "parent, guardian, teacher, school counsellor" in data["trusted_adult_notice"].lower()
        
        # 23. Confidentiality policy inquiry
        assert "confidentiality policy" in data["confidentiality_note"].lower()
        assert "before you tell them anything personal" in data["confidentiality_note"].lower()
        
        # 24. Resources
        srv_names = [s["name"] for s in data["services"]]
        assert "Tele-MANAS" in srv_names
        assert "Child Helpline" in srv_names
        assert "Meri Trustline" in srv_names
        assert "National Cyber Crime Helpline" in srv_names
        assert "Emergency Services" in srv_names

@pytest.mark.asyncio
async def test_30_spec_item_25_feelings_check_in():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/mood", json={
            "mood_score": 4,
            "mood_label": "Calm",
            "emotion_tags": ["Calm", "Hopeful"],
            "notes": "Feeling centered today."
        })
        assert res.status_code == 200
        
        res_hist = await client.get("/api/mood/history")
        assert res_hist.status_code == 200
        assert len(res_hist.json()) >= 1

@pytest.mark.asyncio
async def test_30_spec_item_26_private_journal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        res_c = await client.post("/api/journal", json={
            "title": "Private Reflection",
            "content": "Today was quiet and peaceful."
        })
        assert res_c.status_code == 200
        j_id = res_c.json()["id"]

        # List
        res_l = await client.get("/api/journal")
        assert res_l.status_code == 200
        assert any(j["id"] == j_id for j in res_l.json())

        # Update
        res_u = await client.put(f"/api/journal/{j_id}", json={
            "title": "Updated Reflection",
            "content": "Added more reflections."
        })
        assert res_u.status_code == 200
        assert res_u.json()["title"] == "Updated Reflection"

        # Delete
        res_d = await client.delete(f"/api/journal/{j_id}")
        assert res_d.status_code == 204

@pytest.mark.asyncio
async def test_30_spec_item_27_to_30_theme_and_features():
    # Verify style.css includes light and dark theme variables with proper contrasts
    with open("app/static/style.css", "r") as f:
        css = f.read()
    assert ':root' in css
    assert '[data-theme="dark"]' in css
    assert '--bg-page' in css
    assert '--olive-primary' in css
    assert '--primary' in css
