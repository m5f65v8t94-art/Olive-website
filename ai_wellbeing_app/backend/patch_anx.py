with open("app/services/local_engine.py", "r") as f:
    code = f.read()

marker = "        # 12. Conflict / Venting"
anxiety_block = """        # 11b. Anxiety / Panic / Nervousness
        if "anxiety_panic" in themes or any(w in lower for w in ["heart racing", "overthinking", "spiraling", "nervous", "anxious", "racing", "tightness"]):
            if analysis["academic_subjects"]:
                sub = analysis["academic_subjects"][0]
                candidates = [
                    f"That wave of nervousness creeping back in when you thought you were in the clear is so frustrating. Is the anxiety about {sub} or your upcoming quiz starting to ramp back up again?\\n\\n"
                    f"Your nervous system is just feeling on edge. I'm right here with you—what thought popped up that triggered that nervous feeling again?",

                    f"Oof, that sudden spike of nervousness around {sub} is so unsettling. You don't have to fight it off alone. What does the nervousness feel like right now?"
                ]
                return self._select_non_repeating(candidates, past_texts)
            else:
                candidates = [
                    "Having your heart racing and feeling your mind spiral into worst-case scenarios is so exhausting. When your nervous system gets stuck in overdrive like that and your chest feels tight, everything feels urgent and threatening even when you're physically safe.\\n\\n"
                    "You don't have to solve every 'what if' question your brain is throwing at you right now. I'm right here in the room with you.\\n\\n"
                    "What is the loudest worry that keeps looping in your head right now?",

                    "That spiraling sensation where your thoughts won't stop racing and tight dread takes over is really frightening. It's so hard to catch your breath when your body is sounding an alarm.\\n\\n"
                    "I'm listening with zero pressure to fix it this second. What is making you feel the most on edge today?"
                ]
                return self._select_non_repeating(candidates, past_texts)
"""

code = code.replace(marker, anxiety_block + "\n" + marker)

with open("app/services/local_engine.py", "w") as f:
    f.write(code)

print("Added anxiety handler to _compose_listen_response!")
