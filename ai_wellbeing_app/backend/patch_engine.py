import os

with open("app/services/local_engine_backup.py", "r") as f:
    code = f.read()

# 1. Add has_embarrassment to analysis
search_marker = "        # 5. Social Exclusion / Loneliness / Friendship Alienation"
new_embarrassment = """        # 4b. Embarrassment / Mocking Triggers
        has_embarrassment = any(p in lower for p in [
            "laughed at me", "laughing at me", "made fun of me", "laughed at",
            "too embarrassing", "so embarrassing", "embarrassed", "humiliated",
            "humiliation", "clowned on", "mocked me", "everybody laughed", "everyone laughed"
        ])
"""
code = code.replace(search_marker, new_embarrassment + "\n" + search_marker)

# 2. Add to themes
theme_marker = "        if has_friendship_exclusion:"
theme_embarrass = """        if has_embarrassment:
            themes.append("embarrassment")
        elif has_friendship_exclusion:"""
code = code.replace(theme_marker, theme_embarrass)

# 3. Add embarrassment handler in _compose_listen_response
listen_marker = "        # 1. Vitiligo & Visible Conditions / Appearance"
listen_embarrass = """        # 0. Embarrassment / Being Laughed at
        if "embarrassment" in themes or any(w in lower for w in ["laughed at me", "laughing at me", "too embarrassing", "so embarrassing", "embarrassed", "humiliated"]):
            candidates = [
                "I am so sorry that happened to you. Being laughed at and dealing with that kind of public embarrassment is genuinely one of the most painful, humiliating feelings, and it stings deeply. Nobody deserves to be mocked or laughed at like that.\\n\\n"
                "You have every right to feel hurt and upset. I'm right here in your corner listening.\\n\\n"
                "Do you want to vent about what happened, or just take a minute to breathe and get it out?",

                "Ugh, that hurts so deeply. Having people laugh at you leaves this horrible, burning embarrassment where you just want to disappear, and it's completely unfair.\\n\\n"
                "Please know that other people acting like that says everything about them, not your worth.\\n\\n"
                "What happened today that made things feel so humiliating?"
            ]
            return self._select_non_repeating(candidates, past_texts)
"""
code = code.replace(listen_marker, listen_embarrass + "\n" + listen_marker)

# 4. Add "why do i feel overwhelmed even when i havent done that much" to understand mode
understand_marker = "        # 1. Unanswered Messages / Texting Anxiety"
understand_overwhelm = """        # 0. Overwhelmed without doing much
        if any(p in lower for p in ["haven't done that much", "havent done that much", "haven't done much", "havent done much", "didn't do much", "didnt do much", "barely did anything", "haven't done anything", "havent done anything"]) or (("why do i feel" in lower or "why am i" in lower) and "overwhelm" in lower):
            return (
                "Here is why you can feel completely overwhelmed even when you haven't done that much physically:\\n\\n"
                "1. **Invisible Background Processing:** Your brain doesn't just use energy when you are actively doing homework or chores. Constantly holding onto worries, anticipating problems, managing social dynamics, or feeling anxious runs heavy 'background apps' in your nervous system. That drains your battery just as much as physical effort.\\n\\n"
                "2. **Sensory & Digital Overload:** Constant screen time, notifications, and environmental noise keep your nervous system in a subtle state of high alert. Even when you are 'resting' in bed, your brain might not be getting true nervous system recovery.\\n\\n"
                "3. **Cumulative Emotional Fatigue:** Overwhelm is rarely caused by what happened today alone. It's usually the result of days or weeks of accumulated tension finally reaching the surface.\\n\\n"
                "Feeling exhausted without a clear 'reason' does NOT mean you are lazy or broken—it simply means your nervous system is asking for quiet downtime.\\n\\n"
                "Has your mind been racing with background worries lately, or is it more of a deep physical and mental heaviness?"
            )
"""
code = code.replace(understand_marker, understand_overwhelm + "\n" + understand_marker)

with open("app/services/local_engine.py", "w") as f:
    f.write(code)
print("Updated local_engine.py successfully!")
