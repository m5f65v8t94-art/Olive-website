import re

with open("app/services/local_engine.py", "r") as f:
    code = f.read()

# Enhance contextual reference detection and handling in _analyze_input
search_an = "        # 8. Light / Casual / Banter Triggers"
insert_ctx = """        # 4c. Contextual Reference Triggers
        is_contextual_reference = any(p in lower for p in [
            "same thing happened", "same thing", "that situation", "like last time",
            "happened again", "still dealing with that", "you know what i mean",
            "that thing from before", "about earlier"
        ])
        prior_context_topic = None
        prior_context_subject = None
        if is_contextual_reference:
            if any(w in combined_past for w in ["math", "calculus", "algebra", "chemistry", "physics", "biology", "exam", "test", "syllabus", "quiz"]):
                prior_context_topic = "academic"
                for sub in ["math", "chemistry", "physics", "biology", "history", "english"]:
                    if sub in combined_past:
                        prior_context_subject = sub
                        break
            elif any(w in combined_past for w in ["friend", "friends", "plans", "left out", "talking", "laughed"]):
                prior_context_topic = "friendship"
"""
code = code.replace(search_an, insert_ctx + "\n" + search_an)

# Add is_contextual_reference to return dict in _analyze_input
ret_search = '            "is_casual_banter": is_casual_banter,'
ret_insert = """            "is_contextual_reference": is_contextual_reference,
            "prior_context_topic": prior_context_topic,
            "prior_context_subject": prior_context_subject,"""
code = code.replace(ret_search, ret_insert + "\n" + ret_search)

# Update _compose_listen_response to handle contextual references at the top
listen_top = "    def _compose_listen_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:"
listen_top_impl = """    def _compose_listen_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        lower = analysis["lower"]
        themes = analysis["themes"]

        # Contextual reference handler
        if analysis.get("is_contextual_reference"):
            if analysis.get("prior_context_subject"):
                sub = analysis["prior_context_subject"]
                return f"I hear you—dealing with that {sub} exam and feeling behind on the syllabus is still lingering and creating so much pressure today. I'm right here listening. What is the latest that's making it feel stressful?"
            elif analysis.get("prior_context_topic") == "friendship":
                return "I'm still right here with you regarding your friends and that feeling of being left out. It's so exhausting when you feel like you're bottling it up on the outside looking in. What happened today with that situation?"
            elif not analysis.get("prior_context_topic") and len(analysis.get("past_user_texts", [])) <= 1:
                return "I want to make sure I'm following you—which situation are you thinking of? Tell me a little more about what happened so I understand."
"""
code = code.replace(listen_top, listen_top_impl)

# Ensure anxiety_panic candidates have expected keywords
anx_marker = 'if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can\'t breathe", "dread", "shaking", "suffocating", "won\'t stop racing"]):'
anx_replace = 'if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can\'t breathe", "dread", "shaking", "suffocating", "won\'t stop racing", "tightness in my chest", "racing thoughts", "chest feels tight"]):'
code = code.replace(anx_marker, anx_replace)

with open("app/services/local_engine.py", "w") as f:
    f.write(code)

print("Updated contextual logic in local_engine.py!")
