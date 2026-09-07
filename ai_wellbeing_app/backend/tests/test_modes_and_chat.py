import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_get_modes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/chat/modes")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4
        mode_ids = [m["id"] for m in data]
        assert "just_listen" in mode_ids
        assert "give_me_advice" in mode_ids
        assert "help_me_understand" in mode_ids
        assert "help_me_tell_someone" in mode_ids

@pytest.mark.asyncio
async def test_chat_turn_just_listen_loneliness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I feel like I don't have any friends",
            "mode": "just_listen"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        assert "lonely" in content.lower() or "anyone" in content.lower()
        # Ensure no bullet points or worksheets in Just Listen
        assert "•" not in content
        assert "1." not in content
        # Ensure it has a gentle question
        assert "?" in content

@pytest.mark.asyncio
async def test_chat_turn_grief():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I miss someone who died recently",
            "mode": "just_listen"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        assert "grief" in content.lower() or "loss" in content.lower() or "miss" in content.lower()
        assert "?" in content

@pytest.mark.asyncio
async def test_chat_turn_body_image_listen():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I have been starving myself as I feel fat and ugly",
            "mode": "just_listen"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        assert "•" not in content
        assert "hurts" in content.lower() or "pain" in content.lower() or "judgment" in content.lower() or "alone" in content.lower()
        assert "?" in content

@pytest.mark.asyncio
async def test_chat_turn_give_me_advice():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I'm having a lot of anxiety and my heart is beating fast.",
            "mode": "give_me_advice"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        assert len(content) > 30

@pytest.mark.asyncio
async def test_get_help_privately_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/resources/private-help")
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        service_names = [s["name"] for s in data["services"]]
        assert "Tele-MANAS" in service_names
        assert "Child Helpline" in service_names
        assert "Meri Trustline" in service_names
        assert "National Cyber Crime Helpline" in service_names
        assert "Emergency Services" in service_names

@pytest.mark.asyncio
async def test_chat_turn_vitiligo_specific_recognition():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I’m stressed as my vitiligo is increasing and people keep on saying that looks matter but it’s easy for them to say because they don’t feel the stares or looks people give me or the restrictions.",
            "mode": "just_listen"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        # Must specifically recognize vitiligo, stares/looks, dismissive comments, and restrictions
        assert "vitiligo" in content.lower()
        assert any(w in content.lower() for w in ["stares", "staring", "eyes", "looks"])
        assert any(w in content.lower() for w in ["easy for", "platitudes", "dismiss", "frustrat", "unsolicited"])
        # Must not be a generic breathing or meditation response in Just Listen mode
        assert "breathe" not in content.lower()
        assert "grounding" not in content.lower()
        assert "1." not in content
        # Must ask a relevant follow-up question
        assert "?" in content

@pytest.mark.asyncio
async def test_chat_turn_academic_subject_specific():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I'm failing my chemistry exam tomorrow and I'm totally panicked",
            "mode": "just_listen"
        }
        response = await client.post("/api/chat/turn", json=payload)
        assert response.status_code == 200
        data = response.json()
        content = data["assistant_message"]["content"]
        assert "chemistry" in content.lower() or "school" in content.lower() or "exam" in content.lower()
        assert "?" in content
