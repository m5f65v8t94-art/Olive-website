import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_contextual_reference_with_prior_context():
    """
    Test that Liv understands short references ('same thing happened', 'like last time')
    when the context was discussed in the active session.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1: Discuss math exam panic
        t1 = await client.post("/api/chat/turn", json={
            "message": "I have my math exam tomorrow and I'm panicking because I haven't finished the syllabus.",
            "mode": "just_listen"
        })
        assert t1.status_code == 200
        session_id = t1.json()["session_id"]
        c1 = t1.json()["assistant_message"]["content"].lower()
        assert "math" in c1

        # Turn 2: User says "same thing happened again"
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "Same thing happened again today.",
            "mode": "just_listen"
        })
        assert t2.status_code == 200
        c2 = t2.json()["assistant_message"]["content"].lower()
        # Must connect to the math / exam context discussed in Turn 1
        assert "math" in c2 or "exam" in c2 or "syllabus" in c2

@pytest.mark.asyncio
async def test_contextual_reference_friendship_with_prior_context():
    """
    Test contextual reference for friendship exclusion.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1: Discuss feeling left out by friends
        t1 = await client.post("/api/chat/turn", json={
            "message": "My friends made plans right in front of me and left me out.",
            "mode": "just_listen"
        })
        assert t1.status_code == 200
        session_id = t1.json()["session_id"]

        # Turn 2: User references "that situation"
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I'm still dealing with that situation from before.",
            "mode": "just_listen"
        })
        assert t2.status_code == 200
        c2 = t2.json()["assistant_message"]["content"].lower()
        assert any(w in c2 for w in ["friends", "left out", "outside", "bottling it up"])

@pytest.mark.asyncio
async def test_contextual_reference_without_prior_context_asks_clarification():
    """
    Test that when user says 'like last time' or 'that situation' in a clean session
    without prior context, Liv does NOT invent memories; she asks a natural clarification question.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat/turn", json={
            "message": "That situation happened again.",
            "mode": "just_listen"
        })
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"].lower()
        # Must ask clarification naturally
        assert any(w in content for w in ["which situation", "following you", "tell me a little more", "remind me", "what happened"])

@pytest.mark.asyncio
async def test_multi_feelings_check_in_logging():
    """
    Test logging multiple emotion tags in a single check-in.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "mood_score": 2,
            "mood_label": "Tired",
            "emotion_tags": ["Tired", "Stressed", "Anxious"],
            "notes": "Long day studying for tests."
        }
        res = await client.post("/api/mood", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["mood_score"] == 2
        assert "Tired" in data["emotion_tags"]
        assert "Stressed" in data["emotion_tags"]
        assert "Anxious" in data["emotion_tags"]

@pytest.mark.asyncio
async def test_pin_hash_and_verification():
    """
    Test PIN creation hash and verification endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Hash a 4-digit PIN
        hash_res = await client.post("/api/history/hash-pin", json={"pin": "2468"})
        assert hash_res.status_code == 200
        hashed_pin = hash_res.json()["hashed_pin"]

        # Verify correct PIN
        verify_res = await client.post("/api/history/verify-pin", json={
            "pin": "2468",
            "hashed_pin": hashed_pin
        })
        assert verify_res.status_code == 200
        assert verify_res.json()["authenticated"] is True

        # Verify incorrect PIN
        bad_res = await client.post("/api/history/verify-pin", json={
            "pin": "9999",
            "hashed_pin": hashed_pin
        })
        assert bad_res.status_code == 401
