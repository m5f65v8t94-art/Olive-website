import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_scenario_1_loneliness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I feel like I don't have any friends and nobody really cares if I show up or not.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["lonely", "invisible", "disconnected", "quiet"])
        assert "1." not in content
        assert "breathing" not in content.lower()
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_2_friendship_problems():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "My two closest friends made plans right in front of me and didn't invite me. I had to pretend I didn't care.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["sting", "plans", "pretend", "afterthought", "invisible", "hurt"])
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_3_exam_study_stress():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I have my chemistry final tomorrow and I'm totally panicking. I haven't even finished half the syllabus.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert "chemistry" in content.lower() or "syllabus" in content.lower() or "exam" in content.lower()
        assert "1." not in content
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_4_academic_disappointment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I got my math test back and I got a 42%. I studied all weekend and I feel so completely stupid.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["math", "gut punch", "score", "demoralizing", "effort", "stupid"])
        assert any(w in content.lower() for w in ["does not define", "does not mean", "not that your intelligence"])
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_5_body_image_insecurity():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I looked in the mirror today and I just felt so ugly and uncomfortable in my own skin.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["mirror", "skin", "critical", "exhausting", "judgment", "alone"])
        assert "1." not in content
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_6_grief_missing_someone():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I really miss my grandmother today. She passed away last year and out of nowhere it just hit me so hard.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["grief", "timeline", "missing", "memory", "sorry", "heart"])
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_7_anxiety_spiraling():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "My heart won't stop racing and I keep overthinking everything that could go wrong.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["racing", "spiraling", "exhausting", "nervous system", "tight"])
        assert "1." not in content
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_8_generally_bad_day():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Nothing specifically terrible happened, but I just feel awful and want to lay in bed all day.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["bed", "exhausting", "off", "guilty", "permission", "rest", "valid"])
        assert "1." not in content
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_9_just_listen_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "My mom yelled at me for forgetting chores and I'm just so mad.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["yelled", "frustrat", "unfair", "vent", "mom"])
        # No advice bullets
        assert "1." not in content

@pytest.mark.asyncio
async def test_scenario_10_give_me_advice_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I can't stop procrastinating on my history essay and it's due in 4 hours.",
            "mode": "give_me_advice"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert "1." in content
        assert any(w in content.lower() for w in ["essay", "timer", "draft", "history", "outline"])

@pytest.mark.asyncio
async def test_scenario_11_help_me_understand_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Why do I get so angry every time my friend talks about her other friends?",
            "mode": "help_me_understand"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["anger", "shield", "replaced", "fear", "emotional safety", "threat"])
        assert "?" in content

@pytest.mark.asyncio
async def test_scenario_12_help_me_tell_someone_mode():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I want to tell my school counselor that I've been feeling overwhelmed, but I don't know what to write.",
            "mode": "help_me_tell_someone"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["counselor", "email", "office", "drop by", "schedule"])

@pytest.mark.asyncio
async def test_scenario_13_dislikes_breathing_boundary():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Please don't tell me to do breathing exercises, they always make me feel more anxious.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["respect", "don't work for everyone", "never push", "off the table", "zero exercises"])
        assert "4-7-8" not in content
        assert "box breathing" not in content.lower()

@pytest.mark.asyncio
async def test_scenario_14_conversation_memory_continuity():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1: mention algebra
        t1 = await client.post("/api/chat/turn", json={
            "message": "I have an algebra quiz on Friday.",
            "mode": "just_listen"
        })
        session_id = t1.json()["session_id"]
        
        # Turn 2: general feeling
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I'm feeling much better today.",
            "mode": "just_listen"
        })

        # Turn 3: nervousness returns
        t3 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I'm getting nervous again.",
            "mode": "just_listen"
        })
        content3 = t3.json()["assistant_message"]["content"]
        assert "algebra" in content3.lower() or "quiz" in content3.lower() or "school" in content3.lower() or "test" in content3.lower()

@pytest.mark.asyncio
async def test_scenario_15_light_casual_banter():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Hey Liv, what do you think is the best study snack?",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["popcorn", "pretzels", "snack", "crunch", "cramming", "procrastination"])

@pytest.mark.asyncio
async def test_scenario_16_serious_shift_drop_sass():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User shares deep family struggle
        payload = {
            "message": "Actually... my parents are getting divorced and everything is falling apart.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        assert any(w in content.lower() for w in ["sorry", "ground", "pulled out", "falling apart", "painful", "home"])
        # Ensure no playful banter
        assert "snack" not in content.lower()
        assert "joke" not in content.lower()

@pytest.mark.asyncio
async def test_fresh_session_friendship_bad_day_no_advice():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I had a really bad day at school. My friends were all talking together and I felt like I wasn't really part of it. I don't want advice right now, I just want to talk about it.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        
        # 1. Must validate friendship exclusion & feeling left out
        assert any(w in content.lower() for w in ["friends", "isolat", "outside", "part of it", "shut out", "talking", "invisible", "disconnected", "stomach", "stings"])
        
        # 2. Must acknowledge explicit no advice preference
        assert any(w in content.lower() for w in ["zero unsolicited advice", "no advice", "just here to listen", "don't have to fix", "dont have to fix"])
        
        # 3. Must NOT hallucinate exams, syllabus, or deadline panic
        assert "exam" not in content.lower()
        assert "syllabus" not in content.lower()
        assert "deadline" not in content.lower()
        assert "chemistry" not in content.lower()
        assert "math" not in content.lower()
        assert "42%" not in content

