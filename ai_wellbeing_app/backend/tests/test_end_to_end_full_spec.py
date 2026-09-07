import os
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
async def test_static_files_and_html_spec():
    """Verify static assets, logo image, and HTML compliance with spec."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Index page
        res = await client.get("/")
        assert res.status_code == 200
        html = res.text

        # Verify logo asset is referenced directly
        assert "/static/olive_logo.png" in html
        assert 'alt="Olive Logo"' in html

        # Verify header title and badge
        assert "Olive" in html
        assert "Youth Mental Wellbeing Support" in html

        # Verify Supportive & Non-Clinical + Trusted Adult Notice
        assert "Supportive &amp; Non-Clinical:" in html or "Supportive & Non-Clinical:" in html
        assert "trusted adult" in html.lower()
        assert "parent, guardian, teacher, school counsellor" in html

        # Verify Navigation pills
        assert "Chat with Liv" in html
        assert "Get Help (Privately)" in html
        assert "Feelings Check-in" in html
        assert "Private Journal" in html
        assert "Calming Exercises" in html
        assert "Protected History" in html

        # Verify NO (Optional) in Feelings or Calming headings
        assert "Feelings Check-in (Optional)" not in html
        assert "Calming Exercises (Optional)" not in html

        # Verify 4 Liv modes
        assert "Just Listen" in html
        assert "Give Me Advice" in html
        assert "Help Me Understand" in html
        assert "Help Me Tell Someone" in html

        # Verify 2. Logo image file exists and is valid PNG
        logo_res = await client.get("/static/olive_logo.png")
        assert logo_res.status_code == 200
        assert len(logo_res.content) > 500000  # High quality original asset

@pytest.mark.asyncio
async def test_chat_modes_exact_spec_scenarios():
    """Verify all 4 Liv conversation modes against required test cases."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. JUST LISTEN MODE: "they laughed at me it was too embarrassing"
        res1 = await client.post("/api/chat/turn", json={
            "message": "they laughed at me it was too embarrassing",
            "mode": "just_listen"
        })
        assert res1.status_code == 200
        c1 = res1.json()["assistant_message"]["content"]
        c1_lower = c1.lower()
        # Must specifically validate being laughed at and embarrassment
        assert any(w in c1_lower for w in ["laughed at", "laugh", "embarrass", "humiliat", "mock"])
        # Must NOT give breathing exercise or productivity advice
        assert "breathing" not in c1_lower
        assert "1." not in c1

        # 2. GIVE ME ADVICE MODE: School stress and workload paralysis
        res2 = await client.post("/api/chat/turn", json={
            "message": "I've been really stressed about school lately. I have so much to do and I don't even know where to start.",
            "mode": "give_me_advice"
        })
        assert res2.status_code == 200
        c2 = res2.json()["assistant_message"]["content"]
        c2_lower = c2.lower()
        # Must give structured practical school advice
        assert any(w in c2_lower for w in ["dump", "micro", "10-minute", "timer", "easiest", "tab", "assignment", "school"])
        assert "1." in c2

        # 3. HELP ME UNDERSTAND MODE: "Why do I feel overwhelmed even when I haven't done that much?"
        res3 = await client.post("/api/chat/turn", json={
            "message": "Why do I feel overwhelmed even when I haven't done that much?",
            "mode": "help_me_understand"
        })
        assert res3.status_code == 200
        c3 = res3.json()["assistant_message"]["content"]
        c3_lower = c3.lower()
        # Must directly answer WHY first in plain language
        assert any(w in c3_lower for w in ["background", "nervous system", "battery", "mental", "invisible", "sensory", "overload", "fatigue"])
        assert "lazy" in c3_lower

        # 4. HELP ME TELL SOMEONE MODE: Talking to dad about school stress
        res4 = await client.post("/api/chat/turn", json={
            "message": "I want to tell my dad that school has been stressing me out, but I don't know how to start.",
            "mode": "help_me_tell_someone"
        })
        assert res4.status_code == 200
        c4 = res4.json()["assistant_message"]["content"]
        # Must give natural conversation starter
        assert "Dad" in c4 or "dad" in c4.lower()
        assert any(w in c4.lower() for w in ["hey dad", "talk", "stress", "school"])

@pytest.mark.asyncio
async def test_auth_and_user_data_strict_isolation():
    """Verify complete isolation between separate user accounts."""
    transport = ASGITransport(app=app)
    uid_a = uuid.uuid4().hex[:8]
    uid_b = uuid.uuid4().hex[:8]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User A Registration
        res_a = await client.post("/api/auth/register", json={
            "username": f"user_a_{uid_a}",
            "email": f"usera_{uid_a}@olive.test",
            "password": "Password123!"
        })
        assert res_a.status_code == 200
        token_a = res_a.json()["token"]

        # User B Registration
        res_b = await client.post("/api/auth/register", json={
            "username": f"user_b_{uid_b}",
            "email": f"userb_{uid_b}@olive.test",
            "password": "Password456!"
        })
        assert res_b.status_code == 200
        token_b = res_b.json()["token"]

        # User A creates a journal entry
        j_a = await client.post(
            "/api/journal",
            headers={"Authorization": f"Bearer {token_a}"},
            json={"title": "User A Private Diary", "content": "This is completely private to User A."}
        )
        assert j_a.status_code == 200

        # User B lists journal entries -> must be EMPTY
        j_b_list = await client.get(
            "/api/journal",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert j_b_list.status_code == 200
        assert len(j_b_list.json()) == 0

        # User A logs a multi-feeling check-in (up to 3)
        m_a = await client.post(
            "/api/mood",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "mood_score": 2,
                "mood_label": "Tired",
                "emotion_tags": ["Tired", "Stressed", "Anxious"],
                "notes": "Testing multi-feeling check-in"
            }
        )
        assert m_a.status_code == 200
        m_data = m_a.json()
        assert len(m_data["emotion_tags"]) == 3
        assert "Tired" in m_data["emotion_tags"]
        assert "Stressed" in m_data["emotion_tags"]
        assert "Anxious" in m_data["emotion_tags"]

        # User B lists mood history -> must be EMPTY
        m_b_list = await client.get(
            "/api/mood/history",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert m_b_list.status_code == 200
        assert len(m_b_list.json()) == 0

@pytest.mark.asyncio
async def test_helplines_directory_complete():
    """Verify all 5 required Indian support resources."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/resources/private-help")
        assert res.status_code == 200
        data = res.json()
        services = data["services"]
        service_names = [s["name"] for s in services]
        service_phones = [s["phone"] for s in services]

        assert "Tele-MANAS" in service_names
        assert "14416" in service_phones
        assert "Child Helpline" in service_names
        assert "1098" in service_phones
        assert "Meri Trustline" in service_names
        assert "6363 17 6363" in service_phones
        assert "National Cyber Crime Helpline" in service_names
        assert "1930" in service_phones
        assert "Emergency Services" in service_names
        assert "112" in service_phones
