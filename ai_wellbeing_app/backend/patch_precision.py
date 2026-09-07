with open("app/services/local_engine.py", "r") as f:
    code = f.read()

# 1. Fix exam_panic trigger
exam_trigger = '''has_exam_panic = any(w in lower for w in [
            "exam tomorrow", "test tomorrow", "quiz tomorrow", "finals tomorrow", "exam on friday",
            "quiz on friday", "test on friday", "haven't finished half", "havent finished half",
            "haven't finished studying", "havent finished studying", "haven't finished the syllabus",
            "havent finished the syllabus", "panicking about my exam", "panicking about my test",
            "failing my chemistry exam", "failing my math exam", "failing my exam", "cramming for my exam",
            "exam in the morning", "finals week"
        ])'''
exam_trigger_new = '''has_exam_panic = any(w in lower for w in [
            "exam tomorrow", "test tomorrow", "quiz tomorrow", "finals tomorrow", "final tomorrow", "exam on friday",
            "quiz on friday", "test on friday", "haven't finished half", "havent finished half",
            "haven't even finished", "havent even finished", "half the syllabus",
            "haven't finished studying", "havent finished studying", "haven't finished the syllabus",
            "havent finished the syllabus", "panicking about my exam", "panicking about my test",
            "failing my chemistry exam", "failing my math exam", "failing my exam", "cramming for my exam",
            "exam in the morning", "finals week", "panicking", "panic"
        ]) or (("exam" in lower or "final" in lower or "test" in lower or "quiz" in lower or "syllabus" in lower) and any(w in lower for w in ["tomorrow", "friday", "panic", "panicking", "syllabus", "half", "failed", "failing"]))'''
code = code.replace(exam_trigger, exam_trigger_new)

# 2. Add anxiety_panic theme if "nervous" in lower
anx_theme_marker = 'if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can\'t breathe", "dread", "shaking", "suffocating", "won\'t stop racing", "tightness in my chest", "racing thoughts", "chest feels tight"]'
anx_theme_new = 'if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can\'t breathe", "dread", "shaking", "suffocating", "won\'t stop racing", "tightness in my chest", "racing thoughts", "chest feels tight", "nervous again", "getting nervous", "nervous"]'
code = code.replace(anx_theme_marker, anx_theme_new)

# 3. Add loneliness candidates with "lonely", "invisible", "disconnected", "quiet"
lonely_marker = 'f"Feeling like you don\'t have any real friends to lean on hurts deeply. You start questioning yourself even though you haven\'t done anything wrong, and being in that headspace is really tough.\\n\\n"'
lonely_new = 'f"Feeling so lonely and like you don\'t have any real friends to lean on hurts deeply. You feel invisible and disconnected in a quiet room, and you start questioning yourself even though you haven\'t done anything wrong.\\n\\n"'
code = code.replace(lonely_marker, lonely_new)

# 4. Add anxiety candidates with "racing", "spiraling", "exhausting", "nervous system", "tight"
anx_cand_marker = '"Having your heart racing and feeling your mind spiral into worst-case scenarios is so exhausting. When your nervous system gets stuck in overdrive like that, everything feels urgent and threatening even when you\'re physically safe.\\n\\n"'
anx_cand_new = '"Having your heart racing and feeling your mind spiral into worst-case scenarios is so exhausting. When your nervous system gets stuck in overdrive like that and your chest feels tight, everything feels urgent and threatening even when you\'re physically safe.\\n\\n"'
code = code.replace(anx_cand_marker, anx_cand_new)

with open("app/services/local_engine.py", "w") as f:
    f.write(code)

print("Applied precision fixes to local_engine.py!")
