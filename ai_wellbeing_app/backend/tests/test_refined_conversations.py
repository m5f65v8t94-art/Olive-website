import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    await init_db()

@pytest.mark.asyncio
async def test_case_1_just_listen_loneliness():
    """
    Test Case 1: Liv must respond specifically to loneliness/friendship.
    Must NOT mention exams, deadlines, panic, breathing, drinking water, sleep.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I feel like I don't have any friends.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"].lower()

        # Must address friendship / loneliness
        assert any(w in content for w in ["friend", "lonely", "disconnected", "isolated", "people", "alone"])
        # Must NOT talk about exams, deadlines, breathing, water
        assert "exam" not in content
        assert "deadline" not in content
        assert "syllabus" not in content
        assert "chemistry" not in content
        assert "breathing" not in content
        assert "water" not in content

@pytest.mark.asyncio
async def test_case_2_just_listen_bad_day_at_school_no_advice():
    """
    Test Case 2: Friends talking together, user excluded, wants no advice.
    Liv must stay focused on feeling excluded/lonely and school friendship situation.
    She must NOT respond about exams, deadlines, panic, syllabus.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I had a really bad day at school. My friends were all talking together and I felt like I wasn't really part of it. I don't want advice right now, I just want to talk about it.",
            "mode": "just_listen"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"].lower()

        # Validates exclusion / outside looking in
        assert any(w in content for w in ["friends", "outside", "part of it", "shut out", "talking", "invisible", "left out", "isolat"])
        # Acknowledges no advice
        assert any(w in content for w in ["unsolicited advice", "no advice", "just here to listen", "don't have to fix", "dont have to fix"])
        # Zero school deadline / exam hallucinations
        assert "exam" not in content
        assert "deadline" not in content
        assert "syllabus" not in content
        assert "homework" not in content

@pytest.mark.asyncio
async def test_case_3_give_me_advice_three_assignments():
    """
    Test Case 3: Three assignments due this week, procrastination, don't know where to start.
    Liv must help prioritize, break into steps, and solve the assignments problem.
    Must NOT give generic 'drink water, take a break, low-output day'.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I have three assignments due this week and I keep putting them off because I don't know where to start. Now I'm stressed because I've wasted so much time. What should I actually do?",
            "mode": "give_me_advice"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        lower = content.lower()

        # Must give actionable assignment steps
        assert "1." in content
        assert any(w in lower for w in ["triage", "urgent", "friction", "easiest", "first step", "10-minute", "draft", "single-task"])
        assert any(w in lower for w in ["assignment", "assignments", "work"])
        
        # Must NOT replace with generic filler
        assert "drink water" not in lower
        assert "have a snack" not in lower
        assert "low-output day" not in lower

@pytest.mark.asyncio
async def test_case_4_help_me_understand_unanswered_messages():
    """
    Test Case 4: Why do I react upset/wondering if I did something wrong when someone doesn't reply?
    Liv explains the pattern (information void, uncertainty, overprotective reaction).
    Must NOT give vague filler like 'core emotional need is feeling threatened'.
    Must NOT diagnose.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "I get really upset when someone doesn't reply to my messages, even if I know they're probably just busy. Then I start wondering if I did something wrong or if they're annoyed with me. Why do I react like that?",
            "mode": "help_me_understand"
        }
        res = await client.post("/api/chat/turn", json=payload)
        assert res.status_code == 200
        content = res.json()["assistant_message"]["content"]
        lower = content.lower()

        # Explains uncertainty / information void / threat-detection / overprotective reaction
        assert any(w in lower for w in ["information void", "uncertainty", "blank space", "threat-detection", "overprotective", "defense mechanism", "fill in"])
        # No vague cliché
        assert "core emotional need is feeling threatened" not in lower
        # No medical diagnosis
        assert "you have borderline" not in lower
        assert "you have bipolar" not in lower

@pytest.mark.asyncio
async def test_case_5_help_me_tell_someone_multi_turn_dad():
    """
    Test Case 5:
    Turn 1: 'I want to tell my dad that school has been stressing me out a lot lately, but I don't know how to bring it up.'
    Turn 2: 'In person.'
    Liv must remember Dad, school stress, in-person conversation.
    Must NOT ask again who to talk to or tell user to switch tabs.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Turn 1
        t1 = await client.post("/api/chat/turn", json={
            "message": "I want to tell my dad that school has been stressing me out a lot lately, but I don't know how to bring it up.",
            "mode": "help_me_tell_someone"
        })
        assert t1.status_code == 200
        session_id = t1.json()["session_id"]
        c1 = t1.json()["assistant_message"]["content"]
        assert "dad" in c1.lower()

        # Turn 2
        t2 = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "In person.",
            "mode": "help_me_tell_someone"
        })
        assert t2.status_code == 200
        c2 = t2.json()["assistant_message"]["content"]
        lower2 = c2.lower()

        # Must remember Dad, school stress, in-person
        assert "dad" in lower2
        assert "school" in lower2 or "stress" in lower2
        assert "in-person" in lower2 or "in person" in lower2 or "face-to-face" in lower2
        
        # Must NOT re-ask who they want to talk to
        assert "who are you thinking about talking to" not in lower2
        # Must NOT tell user to switch to Help Me Tell Someone tab
        assert "switch to the help me tell someone tab" not in lower2

@pytest.mark.asyncio
async def test_clean_new_session_isolation():
    """
    Test Case 6: Verify a new conversation session has 100% clean context without previous baggage.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # User 1 talks about chemistry exam panic
        s1 = await client.post("/api/chat/turn", json={
            "message": "I'm panicking about my chemistry exam tomorrow.",
            "mode": "just_listen"
        })
        assert s1.status_code == 200

        # Completely fresh session talking about being lonely
        s2 = await client.post("/api/chat/turn", json={
            "message": "I feel lonely today and don't know what to do.",
            "mode": "just_listen"
        })
        assert s2.status_code == 200
        c2 = s2.json()["assistant_message"]["content"].lower()
        
        assert "lonely" in c2 or "connected" in c2 or "space" in c2
        assert "chemistry" not in c2
        assert "exam" not in c2
