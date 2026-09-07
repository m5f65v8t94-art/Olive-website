import asyncio
import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

async def test_live_server():
    print(f"Testing live server at {BASE_URL}...")
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Verify Homepage HTML and Static Assets
        res = await client.get("/")
        assert res.status_code == 200, f"Failed to get homepage: {res.status_code}"
        html = res.text
        
        # Verify Key Elements in Homepage HTML
        assert "olive_logo.png" in html, "olive_logo.png asset missing in homepage"
        assert "Youth Mental Wellbeing Support" in html, "Tagline badge missing"
        assert "Quick Privacy Hide" in html, "Quick Privacy Hide button missing"
        assert "Supportive &amp; Non-Clinical" in html or "Supportive & Non-Clinical" in html, "Disclaimer missing"
        assert "Chat with Liv" in html, "Chat with Liv pill missing"
        assert "Get Help (Privately)" in html, "Get Help (Privately) pill missing"
        assert "Feelings Check-in" in html, "Feelings Check-in pill missing"
        assert "Private Journal" in html, "Private Journal pill missing"
        assert "Calming Support" in html, "Calming Support pill missing"
        
        # Requirement 1: Help Me Tell Someone removed from navigation row
        assert 'id="tab-tell-someone"' not in html, "Help Me Tell Someone must not be in nav bar"
        
        # Requirement 3: Change PIN removed completely from website HTML
        assert "Change PIN" not in html, "Change PIN text must not appear anywhere on website"
        assert "modal-change-pin" not in html, "Change PIN modal must not exist"
        
        assert "Just Listen" in html, "Just Listen mode missing"
        assert "Give Me Advice" in html, "Give Me Advice mode missing"
        assert "Help Me Understand" in html, "Help Me Understand mode missing"
        assert "Continue with Google" in html, "Google Sign-In button missing"
        assert "Did you find this helpful?" not in html, "Found unwanted feedback text"
        print("✅ 1. Homepage HTML & Structural Elements Verified (Nav Bar & No Change PIN)")

        # 2. Verify Static Assets (CSS, JS, Logo)
        css_res = await client.get("/static/style.css")
        assert css_res.status_code == 200, "style.css missing"
        js_res = await client.get("/static/app.js")
        assert js_res.status_code == 200, "app.js missing"
        img_res = await client.get("/static/olive_logo.png")
        assert img_res.status_code == 200, "olive_logo.png missing"
        print("✅ 2. Static Assets (style.css, app.js, olive_logo.png) Verified")

        # 3. Test Google Sign-In & Auth
        google_res = await client.post("/api/auth/google", json={
            "email": "test_google_student@gmail.com",
            "name": "Google Student"
        })
        assert google_res.status_code == 200, f"Google login failed: {google_res.text}"
        auth_data = google_res.json()
        token = auth_data["token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ 3. Google Sign-In Endpoint Verified")

        # 4. PIN Protection & Setup Verification (Requirement 3: PIN Protection intact)
        setup_pin_res = await client.post("/api/auth/setup-pin", json={"pin": "1234"}, headers=headers)
        assert setup_pin_res.status_code == 200, "Setup PIN failed"
        
        # Verify PIN works
        v1 = await client.post("/api/auth/verify-pin", json={"pin": "1234"}, headers=headers)
        assert v1.status_code == 200, "PIN verification failed"

        # Verify Wrong PIN rejected
        bad_v = await client.post("/api/auth/verify-pin", json={"pin": "9999"}, headers=headers)
        assert bad_v.status_code == 401, "Wrong PIN was not rejected"
        print("✅ 4. PIN Protection and Protected History Verification Verified")

        # Requirement 2: Quick Privacy Hide Multi-Slide Endpoint & Data
        notes_res = await client.get("/api/resources/study-notes")
        assert notes_res.status_code == 200, "Failed to get study notes"
        notes_data = notes_res.json()
        assert len(notes_data) >= 5, f"Expected multiple study slides, got {len(notes_data)}"
        subjects = [s["subject"] for s in notes_data]
        assert "Biology" in subjects
        assert "Economics" in subjects
        assert "Chemistry" in subjects
        assert "History" in subjects
        assert "Physics" in subjects
        print(f"✅ 4b. Quick Privacy Hide Multi-Slide Verified ({len(notes_data)} realistic subject slides)")

        # 5. Test Chat Modes
        # Mode 1: Just Listen
        listen_res = await client.post("/api/chat/turn", json={
            "message": "I feel so overwhelmed with my math exam and assignments",
            "mode": "just_listen"
        }, headers=headers)
        assert listen_res.status_code == 200
        session_id = listen_res.json()["session_id"]
        assert len(listen_res.json()["assistant_message"]["content"]) > 10

        # Mode 2: Give Me Advice
        advice_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "What practical steps should I take to break it down?",
            "mode": "give_me_advice"
        }, headers=headers)
        assert advice_res.status_code == 200
        assert "1." in advice_res.json()["assistant_message"]["content"]

        # Mode 3: Help Me Understand
        understand_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "Why do I feel so stressed even when I haven't done much today?",
            "mode": "help_me_understand"
        }, headers=headers)
        assert understand_res.status_code == 200
        assert "why" in understand_res.json()["assistant_message"]["content"].lower() or "nervous system" in understand_res.json()["assistant_message"]["content"].lower()

        # Mode 4: Help Me Tell Someone with format adaptation
        tell_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "I want to talk to my dad about this",
            "mode": "help_me_tell_someone"
        }, headers=headers)
        assert tell_res.status_code == 200
        assert "dad" in tell_res.json()["assistant_message"]["content"].lower()

        format_res = await client.post("/api/chat/turn", json={
            "session_id": session_id,
            "message": "in person",
            "mode": "help_me_tell_someone"
        }, headers=headers)
        assert format_res.status_code == 200
        assert "in-person" in format_res.json()["assistant_message"]["content"].lower() or "in person" in format_res.json()["assistant_message"]["content"].lower() or "face-to-face" in format_res.json()["assistant_message"]["content"].lower()
        print("✅ 5. All 4 Liv Modes & Help Me Tell Someone Format Adaptation Verified")

        # 6. Test Safety Interceptor & India Resources & Trusted Adult Transition
        crisis_res = await client.post("/api/chat/turn", json={
            "message": "I'm having suicidal thoughts and don't know what to do",
            "mode": "just_listen"
        }, headers=headers)
        assert crisis_res.status_code == 200
        c_text = crisis_res.json()["assistant_message"]["content"]
        assert "14416" in c_text or "Tele-MANAS" in c_text
        assert "1098" in c_text or "Child Helpline" in c_text
        assert "112" in c_text
        assert "trusted adult" in c_text.lower()
        crisis_session_id = crisis_res.json()["session_id"]

        # De-escalation with trusted adult (mom)
        deescalate_res = await client.post("/api/chat/turn", json={
            "session_id": crisis_session_id,
            "message": "I got my mom to sit with me in my room. Can I tell you what happened at school?",
            "mode": "just_listen"
        }, headers=headers)
        assert deescalate_res.status_code == 200
        deesc_text = deescalate_res.json()["assistant_message"]["content"]
        assert "mom" in deesc_text.lower()
        assert "school" in deesc_text.lower()
        assert "14416" not in deesc_text
        print("✅ 6. Safety Interceptor & India Resources & Trusted Adult Transitions Verified")

        # 7. Test Helpline Directory (Get Help Privately)
        res_help = await client.get("/api/resources/private-help")
        assert res_help.status_code == 200
        help_data = res_help.json()
        assert "confidentiality_note" in help_data
        assert "trusted_adult_notice" in help_data
        service_names = [s["name"] for s in help_data["services"]]
        assert "Tele-MANAS" in service_names
        assert "Child Helpline" in service_names
        assert "Meri Trustline" in service_names
        assert "National Cyber Crime Helpline" in service_names
        assert "Emergency Services" in service_names
        print("✅ 7. Get Help Privately Dedicated Directory Verified")

        # 8. Test Feelings Check-in & History
        mood_res = await client.post("/api/mood", json={
            "mood_score": 4,
            "mood_label": "Calm",
            "emotion_tags": ["Calm", "Relieved"],
            "notes": "Feeling much better after talking to my mom"
        }, headers=headers)
        assert mood_res.status_code == 200
        mood_hist = await client.get("/api/mood/history", headers=headers)
        assert mood_hist.status_code == 200
        assert len(mood_hist.json()) >= 1
        print("✅ 8. Feelings Check-in & History Verified")

        # 9. Test Private Journal
        j_res = await client.post("/api/journal", json={
            "title": "Evening Reflections",
            "content": "Writing down my thoughts in private..."
        }, headers=headers)
        assert j_res.status_code == 200
        journal_id = j_res.json()["id"]

        j_list = await client.get("/api/journal", headers=headers)
        assert j_list.status_code == 200
        assert any(j["id"] == journal_id for j in j_list.json())
        print("✅ 9. Private Journal Verified")

        # 10. Test Protected History & Session Management
        sessions_res = await client.get("/api/chat/sessions", headers=headers)
        assert sessions_res.status_code == 200
        user_sessions = sessions_res.json()
        assert len(user_sessions) >= 1
        print("✅ 10. Protected History & Session Persistence Verified")

    print("\n========================================================")
    print("🎉 ALL VERIFICATION CHECKS PASSED PERFECTLY ON LIVE SERVER!")
    print("========================================================")

if __name__ == "__main__":
    asyncio.run(test_live_server())
