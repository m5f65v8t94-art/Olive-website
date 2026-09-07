import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_tell_someone_parent_draft():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "recipient": "parent_guardian",
            "tone": "gentle_vulnerable",
            "core_feeling": "feeling really drained and failing my classes",
            "what_i_need": "we can talk without getting mad",
            "preferred_medium": "text"
        }
        response = await client.post("/api/help-me-tell-someone", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["recipient"] == "parent_guardian"
        assert data["tone"] == "gentle_vulnerable"
        assert len(data["alternative_drafts"]) > 0
        assert len(data["conversation_tips"]) > 0

@pytest.mark.asyncio
async def test_tell_someone_format_selection_multi_turn():
    """
    Test from user request:
    User: “I want to tell my dad that I've been feeling really stressed about school.”
    User chooses: “In person”
    Problem: Liv repeats the original response instead of giving an in-person version.
    Make Liv remember the selected format and adapt immediately.
    """
    import uuid
    transport = ASGITransport(app=app)
    session_id = str(uuid.uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1: User says who and what they want to tell
        t1_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I want to tell my dad that I've been feeling really stressed about school.",
            "mode": "help_me_tell_someone"
        })
        assert t1_res.status_code == 200
        t1_reply = t1_res.json()["assistant_message"]["content"]
        assert "Dad" in t1_reply or "dad" in t1_reply
        assert "in person" in t1_reply.lower()

        # Turn 2: User chooses "In person"
        t2_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "In person",
            "mode": "help_me_tell_someone"
        })
        assert t2_res.status_code == 200
        t2_reply = t2_res.json()["assistant_message"]["content"]
        # Must give in-person conversation guide for Dad and school stress
        assert "in-person" in t2_reply.lower() or "in person" in t2_reply.lower() or "face-to-face" in t2_reply.lower()
        assert "Dad" in t2_reply
        assert "Step" in t2_reply or "opening" in t2_reply.lower()
        # Must NOT just repeat the format question
        assert "Would you feel most comfortable doing this in person" not in t2_reply

        # Turn 3: User switches format to "Text"
        t3_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "Actually let's do a text message instead",
            "mode": "help_me_tell_someone"
        })
        assert t3_res.status_code == 200
        t3_reply = t3_res.json()["assistant_message"]["content"]
        assert "text" in t3_reply.lower()
        assert "Dad" in t3_reply

