import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_mood_logging_and_summary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a mood log
        log_payload = {
            "mood_score": 4,
            "mood_label": "Hopeful",
            "emotion_tags": ["relieved", "calm"],
            "notes": "Had a good walk today."
        }
        res = await client.post("/api/mood", json=log_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["mood_score"] == 4
        assert "relieved" in data["emotion_tags"]

        # Get summary
        summary_res = await client.get("/api/mood/summary")
        assert summary_res.status_code == 200
        sum_data = summary_res.json()
        assert sum_data["total_entries"] >= 1
        assert sum_data["average_score"] > 0

@pytest.mark.asyncio
async def test_journal_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Prompts list
        p_res = await client.get("/api/journal/prompts")
        assert p_res.status_code == 200
        prompts = p_res.json()
        assert len(prompts) > 0

        # Create entry
        create_payload = {
            "title": "Evening Reflection",
            "content": "Today felt a bit lighter after taking deep breaths.",
            "prompt_used": prompts[0]["prompt_text"],
            "emotion_tag": "Calm"
        }
        c_res = await client.post("/api/journal", json=create_payload)
        assert c_res.status_code == 200
        entry = c_res.json()
        assert entry["title"] == "Evening Reflection"
        entry_id = entry["id"]

        # Get entry
        g_res = await client.get(f"/api/journal/{entry_id}")
        assert g_res.status_code == 200
        assert g_res.json()["content"] == create_payload["content"]

        # Delete entry
        d_res = await client.delete(f"/api/journal/{entry_id}")
        assert d_res.status_code == 204

@pytest.mark.asyncio
async def test_history_pin_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Hash a PIN
        hash_res = await client.post("/api/history/hash-pin", json={"pin": "1234"})
        assert hash_res.status_code == 200
        hashed_pin = hash_res.json()["hashed_pin"]

        # Verify correct PIN
        verify_res = await client.post(
            "/api/history/verify-pin",
            json={"pin": "1234", "hashed_pin": hashed_pin}
        )
        assert verify_res.status_code == 200
        assert verify_res.json()["authenticated"] is True

        # Verify incorrect PIN
        wrong_res = await client.post(
            "/api/history/verify-pin",
            json={"pin": "9999", "hashed_pin": hashed_pin}
        )
        assert wrong_res.status_code == 401
