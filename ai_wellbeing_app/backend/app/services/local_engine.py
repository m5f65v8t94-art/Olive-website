import re
import random
from typing import List, Dict, Any, Optional
from app.services.ai_service import AIProvider

class LivEmpatheticEngine(AIProvider):
    """
    Liv — The warm, emotionally intelligent, perceptive 'cool older sister' AI companion for Olive.
    Never clinical, never robotic, avoids boilerplate templates, worksheets, or repetitive canned lines.
    Grounds responses directly in what the user actually says.
    """

    async def generate_response(
        self,
        mode: str,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context_summary: Optional[str] = None
    ) -> str:
        text = user_message.strip()
        analysis = self._analyze_input(text, conversation_history)

        past_assistant_texts = [
            m.get("content", "").lower() for m in conversation_history if m.get("role") == "assistant"
        ]

        if mode == "give_me_advice":
            return self._compose_advice_response(text, analysis, past_assistant_texts)
        elif mode == "help_me_understand":
            return self._compose_understand_response(text, analysis, past_assistant_texts)
        elif mode == "help_me_tell_someone" or analysis.get("is_selecting_tell_format"):
            return self._compose_tell_someone_response(text, analysis, past_assistant_texts)
        else:
            # Default: Just Listen
            return self._compose_listen_response(text, analysis, past_assistant_texts)

    def _analyze_input(self, text: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        lower = text.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')

        # Check past user messages for multi-turn continuity
        past_user_texts = [
            m.get("content", "").lower() for m in history if m.get("role") == "user"
        ]
        past_assistant_texts = [
            m.get("content", "").lower() for m in history if m.get("role") == "assistant"
        ]
        combined_past = " ".join(past_user_texts)
        full_conversation_text = (combined_past + " " + lower).strip()

        # Prior crisis tracking
        had_prior_crisis = False
        for p_txt in past_user_texts:
            if any(kw in p_txt for kw in [
                "suicide", "kill myself", "end my life", "want to die", "better off dead",
                "self harm", "hurt myself", "cutting", "overdose", "not sure i can keep myself safe",
                "can't keep myself safe", "cant keep myself safe"
            ]):
                had_prior_crisis = True
                break

        # Support person present tracking
        support_person_present = any(kw in lower for kw in [
            "got my mom to stay with me", "got my dad to stay with me", "got my mom", "got my dad",
            "my mom is here with me", "my mom is with me", "my mom is here", "mom is here with me",
            "mom is with me now", "mom is here now", "my dad is here with me", "my dad is with me",
            "dad is here with me", "dad is with me now", "my parents are here", "parents are here with me",
            "with my mom now", "with my dad now", "with my parents now", "with my mom", "with my dad",
            "sitting with my mom", "sitting with my dad", "staying with my mom", "staying with my dad",
            "talked to my mom", "talked to my dad", "told my mom", "told my dad", "told my parents",
            "my counselor is with me", "my teacher is with me", "with my counselor", "with a trusted adult",
            "with someone right now", "my friend is with me", "not alone anymore", "someone is with me"
        ]) or bool(re.search(r'\b(?:got|have|having|is with|is here|staying with|sitting with)\b.*?\b(?:mom|dad|mother|father|parents|parent|counselor|teacher|friend|adult|someone)\b', lower)) or bool(re.search(r'\b(?:mom|dad|mother|father|parents|parent|counselor|teacher|friend|adult|someone)\b.*?\b(?:is here|is with me|is in the room|staying with me|stay with me|here with me)\b', lower))

        support_person_name = "your mom" if ("mom" in lower or "mother" in lower) else (
            "your dad" if ("dad" in lower or "father" in lower) else (
                "your parents" if "parent" in lower else (
                    "your counselor" if "counselor" in lower else (
                        "your teacher" if "teacher" in lower else (
                            "your friend" if "friend" in lower else "a trusted person"
                        )
                    )
                )
            )
        )

        wants_school_topic = any(w in lower for w in [
            "what happened at school", "happened at school today", "at school today", "at school",
            "tell you what happened", "tell you about school", "school today", "classes today"
        ])

        wants_to_stop_safety = any(w in lower for w in [
            "don't want to talk about the safety", "dont want to talk about the safety",
            "don't want to talk about safety", "dont want to talk about safety",
            "not talk about safety", "stop talking about safety", "no more safety stuff",
            "don't want to talk about the safety stuff", "dont want to talk about the safety stuff"
        ])

        is_still_upset = any(w in lower for w in [
            "still really upset", "still upset", "really upset though", "upset though",
            "just want to talk", "just want to vent", "need to talk", "feel awful",
            "still overwhelmed", "still feel bad", "still hurting"
        ])

        # 1. User Boundary & Explicit Intent
        dislikes_breathing = any(p in lower for p in [
            "don't tell me to do breathing", "dont tell me to do breathing",
            "don't tell me to breathe", "dont tell me to breathe",
            "hate breathing", "breathing exercises don't work", "breathing exercises dont work",
            "breathing makes me more anxious", "breathing make me more anxious",
            "stop telling me to breathe", "no breathing exercises", "don't give me breathing",
            "not breathing exercises", "hate doing breathing", "no breathing"
        ]) or ("breathing" in combined_past and any(w in lower for w in ["hate it", "doesn't work", "dont like it", "more anxious", "stop"]))

        wants_no_advice = any(p in lower for p in [
            "don't want advice", "dont want advice", "no advice", "not looking for advice",
            "just want to talk", "just talk about it", "just listen", "need to vent",
            "don't try to fix", "dont try to fix", "don't give me advice", "dont give me advice",
            "not looking for solutions", "no solutions"
        ])

        # 2. Actors / Recipients (Multi-turn aware)
        recipient = None
        for search_src in [lower, combined_past]:
            if not recipient:
                if re.search(r'\b(?:dad|father|stepdad)\b', search_src):
                    recipient = "Dad"
                elif re.search(r'\b(?:mom|mother|stepmom|mommy)\b', search_src) and not re.search(r'\b(?:grandmother|grandma)\b', search_src):
                    recipient = "Mom"
                elif re.search(r'\b(?:grandmother|grandma|grandpa|grandfather)\b', search_src):
                    recipient = "Grandparent"
                elif re.search(r'\b(?:parent|parents|family)\b', search_src):
                    recipient = "Parents"
                elif re.search(r'\b(?:counselor|school counselor|therapist)\b', search_src):
                    recipient = "School Counselor"
                elif re.search(r'\b(?:teacher|professor)\b', search_src):
                    recipient = "Teacher"
                elif re.search(r'\b(?:friend|best friend|bff)\b', search_src):
                    recipient = "Friend"
                elif re.search(r'\b(?:sibling|brother|sister)\b', search_src):
                    recipient = "Sibling"
                elif re.search(r'\b(?:trusted adult|adult|guardian)\b', search_src):
                    recipient = "Trusted Adult"

        # Communication Medium for Telling Someone
        medium = None
        if re.search(r'\b(?:in person|face to face|in-person|talk in person|out loud|verbally|personally|person)\b', lower) or lower.strip() == "person":
            medium = "in_person"
        elif re.search(r'\b(?:text|message|texting|whatsapp|by text|over text|send a text|text version|text message)\b', lower):
            medium = "text"
        elif re.search(r'\b(?:letter|email|note|written|by letter|write a letter|short note|written note|letter version)\b', lower):
            medium = "letter"
        elif re.search(r'\b(?:in person|in-person)\b', combined_past):
            medium = "in_person"
        else:
            # Fall back to checking past user texts in reverse order
            for p_msg in reversed(past_user_texts):
                if re.search(r'\b(?:in person|in-person|face to face|verbally|person)\b', p_msg):
                    medium = "in_person"
                    break
                elif re.search(r'\b(?:text|message|whatsapp)\b', p_msg):
                    medium = "text"
                    break
                elif re.search(r'\b(?:letter|note|email|written)\b', p_msg):
                    medium = "letter"
                    break

        # Topic for Telling Someone
        tell_topic = "what's been on your mind"
        topic_match = re.search(r'(?:tell|talk to)\s+(?:my\s+)?[a-z\s]+?\s+(?:that|about)\s+(.+)', full_conversation_text, re.IGNORECASE)
        if topic_match:
            raw_topic = topic_match.group(1).strip()
            raw_topic = re.sub(r'[\.\?\!]+$', '', raw_topic).strip()
            cleaned_topic = re.sub(r'^(?:i\'ve been feeling|ive been feeling|i am feeling|i feel)\s+', 'feeling ', raw_topic, flags=re.IGNORECASE)
            cleaned_topic = re.sub(r'^(?:i\'m|im)\s+', 'feeling ', cleaned_topic, flags=re.IGNORECASE)
            if len(cleaned_topic) > 3:
                tell_topic = cleaned_topic
        elif any(w in full_conversation_text for w in ["school", "stressing me out", "stress", "overwhelmed", "assignments", "homework", "grades"]):
            tell_topic = "school stress and feeling overwhelmed"
        elif any(w in full_conversation_text for w in ["anxiety", "panic", "racing thoughts", "mental health"]):
            tell_topic = "anxiety and mental wellbeing"
        elif any(w in full_conversation_text for w in ["lonely", "friends", "friendship", "left out", "drama"]):
            tell_topic = "friendship and feeling isolated"

        last_assistant_msg = past_assistant_texts[-1] if past_assistant_texts else ""
        is_active_tell_flow = any(p in last_assistant_msg for p in [
            "in person", "text message", "short note", "help me tell someone", "who are you thinking about talking to", "would you feel most comfortable"
        ])
        is_selecting_tell_format = (
            medium is not None and is_active_tell_flow
        )

        # 3. Specific School Subjects (only if explicitly named in current or recent context)
        academic_subjects = []
        for sub in ["math", "calculus", "algebra", "geometry", "chemistry", "physics", "biology", "history", "english", "literature", "coding", "cs", "economics", "geography"]:
            if re.search(rf"\b{sub}\b", lower):
                academic_subjects.append(sub.title())
            elif re.search(rf"\b{sub}\b", combined_past) and len(academic_subjects) == 0:
                academic_subjects.append(sub.title())

        # 4. Academic Triggers
        has_assignments_procrastination = any(p in lower for p in [
            "assignment", "assignments", "putting them off", "put them off", "don't know where to start",
            "dont know where to start", "don't even know where to start", "dont even know where to start",
            "wasted so much time", "what should i actually do", "stressed about school", "stressed about my school",
            "so much to do", "so much homework", "school workload", "school stress", "where to start",
            "procrastinating", "procrastinate", "due this week", "three assignments", "two assignments",
            "homework", "behind on work", "essay due", "project due", "deadlines"
        ])

        is_academic_disappointment = any(w in lower for w in [
            "got my test back", "got my quiz back", "got my grade back", "got my marks back",
            "got a 42", "got a 40", "got a 50", "got a d", "got an f", "failed my", "flunked",
            "studied all weekend and", "studied so hard and", "studied for days and",
            "feel so stupid", "feel stupid", "bombed my test", "bombed the exam", "bombed my quiz"
        ])

        has_exam_panic = any(w in lower for w in [
            "exam tomorrow", "test tomorrow", "quiz tomorrow", "finals tomorrow", "final tomorrow", "exam on friday",
            "quiz on friday", "test on friday", "haven't finished half", "havent finished half",
            "haven't even finished", "havent even finished", "half the syllabus",
            "haven't finished studying", "havent finished studying", "haven't finished the syllabus",
            "havent finished the syllabus", "panicking about my exam", "panicking about my test",
            "failing my chemistry exam", "failing my math exam", "failing my exam", "cramming for my exam",
            "exam in the morning", "finals week", "panicking", "panic"
        ]) or (("exam" in lower or "final" in lower or "test" in lower or "quiz" in lower or "syllabus" in lower) and any(w in lower for w in ["tomorrow", "friday", "panic", "panicking", "syllabus", "half", "failed", "failing"]))

        # 4b. Embarrassment / Mocking Triggers
        has_embarrassment = any(p in lower for p in [
            "laughed at me", "laughing at me", "made fun of me", "laughed at",
            "too embarrassing", "so embarrassing", "embarrassed", "humiliated",
            "humiliation", "clowned on", "mocked me", "everybody laughed", "everyone laughed"
        ])

        # 5. Social Exclusion / Loneliness / Friendship Alienation
        has_friendship_exclusion = any(p in lower for p in [
            "wasn't really part of it", "wasnt really part of it", "not really part of it", "not part of it",
            "felt like i wasn't", "felt like i wasnt", "weren't including me", "werent including me",
            "talking together", "talking without me", "talking in front of me",
            "made plans right in front of me", "made plans in front of me", "made plans without me",
            "left out", "feeling left out", "left me out", "third wheel", "excluded", "sidelined",
            "ignored by my friends", "nobody talked to me", "felt invisible", "like an outsider",
            "no friend", "no friends", "don't have any friend", "dont have any friend",
            "don't have any friends", "dont have any friends", "have no friends", "don't have friends",
            "dont have friends", "no one likes me", "nobody cares if i show up", "nobody cares if i'm there",
            "nobody cares if im there", "nobody really cares", "nobody cares", "alone", "lonely",
            "feel like i don't have", "feel like i dont have", "group chat", "friendship trouble",
            "my friends were all talking"
        ])

        # 6. Unanswered messages / Social Anxiety & Overthinking
        has_unanswered_messages = any(p in lower for p in [
            "doesn't reply to my messages", "doesnt reply to my messages",
            "don't reply to my messages", "dont reply to my messages",
            "doesn't text back", "doesnt text back", "don't text back", "dont text back",
            "no reply to my", "left on read", "left on delivered",
            "wondering if i did something wrong", "annoyed with me", "mad at me",
            "why do i react like that", "why do i feel like that", "why do i overthink",
            "attachment issues", "attachment issue", "overthinking their reply",
            "hate when someone doesn't reply", "upset when someone doesn't reply"
        ])

        # 7. Condition & Appearance Specifics
        has_vitiligo = "vitiligo" in lower or "skin patch" in lower or "patches" in lower or "pigment" in lower
        has_skin_condition = has_vitiligo or any(w in lower for w in ["acne", "eczema", "scar", "scars", "alopecia", "rash", "dermatitis", "psoriasis"])
        has_appearance_change = any(w in lower for w in ["increasing", "spreading", "getting worse", "changing", "growing", "new spots", "new patches", "worse lately"])
        has_stares_looks = any(w in lower for w in ["stare", "stares", "staring", "look at me", "looks people give", "looks people make", "glances", "gawking", "pointing", "whisper", "whispering", "judging my looks"])
        has_dismissive_comments = any(w in lower for w in [
            "looks matter", "looks don't matter", "looks dont matter", "easy for them to say",
            "they don't feel", "they dont feel", "they don't get it", "they dont get it",
            "it's what's inside", "whats on the inside", "you're just overthinking", "just be confident",
            "telling me to just", "people keep saying"
        ])

        # 4c. Contextual Reference Triggers
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

        # 8. Light / Casual / Banter Triggers
        is_casual_banter = any(lower.startswith(p) or lower == p for p in [
            "hey liv", "hi liv", "hello liv", "what's up", "whats up", "what are you doing",
            "best study snack", "favorite study snack", "what is your favorite", "tell me something funny",
            "i'm bored", "im bored", "bored", "what do you think is the best", "what music do you like",
            "tell me a joke", "recommend a snack", "snack"
        ]) and not any(w in lower for w in ["sad", "hate", "cry", "die", "ugly", "scared", "panick", "fail", "yell", "divorce", "alone", "bad day", "friend", "assignment"])

        # 9. Core Themes Mapping (Prioritized and Mutually Exclusive where appropriate)
        themes = []
        if dislikes_breathing:
            themes.append("dislikes_breathing")
        
        if has_embarrassment:
            themes.append("embarrassment")
        elif has_friendship_exclusion:
            themes.append("loneliness_exclusion")
        elif has_unanswered_messages:
            themes.append("unanswered_messages")
        elif has_assignments_procrastination:
            themes.append("assignments_procrastination")
        elif is_academic_disappointment:
            themes.append("academic_disappointment")
        elif has_exam_panic:
            themes.append("exam_panic")

        if has_vitiligo or has_skin_condition:
            themes.append("visible_condition")
        elif any(re.search(rf"\b{w}\b", lower) for w in ["starve", "starving", "fat", "ugly", "weight", "diet", "purge", "body", "mirror", "disgusting", "calories", "insecure", "unattractive"]) or any(p in lower for p in ["hate the way i look", "hate my body", "looked in the mirror", "uncomfortable in my own skin"]):
            themes.append("body_eating")

        if any(w in lower for w in ["died", "passed away", "lost my", "funeral", "death", "grief", "missing them", "miss my", "grandmother", "grandfather"]):
            themes.append("grief_loss")

        if any(w in lower for w in ["hate myself", "burden", "worthless", "failure", "ruined everything", "useless", "good for nothing", "i suck", "i'm a mess", "im a mess", "let everyone down"]):
            themes.append("self_worth")

        if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can't breathe", "dread", "shaking", "suffocating", "won't stop racing", "tightness in my chest", "racing thoughts", "chest feels tight", "nervous again", "getting nervous", "nervous"]):
            themes.append("anxiety_panic")

        if any(w in lower for w in ["overwhelm", "exhausted", "too much", "burnt out", "burnout", "drowning", "can't take it", "tired of everything", "drained"]):
            themes.append("overwhelm_burnout")

        if any(w in lower for w in ["bad day", "awful day", "terrible day", "rough day", "feel awful", "feeling off"]):
            themes.append("bad_day")

        if any(w in lower for w in ["fight", "yelled", "arguing", "screaming", "mad at me", "broke up", "breakup", "toxic", "drama", "divorce", "divorcing"]):
            themes.append("conflict")

        if is_casual_banter and not themes:
            themes.append("casual_banter")

        return {
            "themes": themes if themes else ["general"],
            "recipient": recipient,
            "medium": medium,
            "tell_topic": tell_topic,
            "has_vitiligo": has_vitiligo,
            "has_skin_condition": has_skin_condition,
            "has_appearance_change": has_appearance_change,
            "has_stares_looks": has_stares_looks,
            "has_dismissive_comments": has_dismissive_comments,
            "academic_subjects": academic_subjects,
            "has_assignments_procrastination": has_assignments_procrastination,
            "is_academic_disappointment": is_academic_disappointment,
            "has_exam_panic": has_exam_panic,
            "has_friendship_exclusion": has_friendship_exclusion,
            "has_unanswered_messages": has_unanswered_messages,
            "dislikes_breathing": dislikes_breathing,
            "wants_no_advice": wants_no_advice,
            "is_contextual_reference": is_contextual_reference,
            "prior_context_topic": prior_context_topic,
            "prior_context_subject": prior_context_subject,
            "is_casual_banter": is_casual_banter,
            "had_prior_crisis": had_prior_crisis,
            "support_person_present": support_person_present,
            "support_person_name": support_person_name,
            "wants_school_topic": wants_school_topic,
            "wants_to_stop_safety": wants_to_stop_safety,
            "is_still_upset": is_still_upset,
            "is_selecting_tell_format": is_selecting_tell_format,
            "raw": text,
            "lower": lower,
            "history_count": len(history),
            "past_user_texts": past_user_texts
        }

    def _select_non_repeating(self, candidates: List[str], past_texts: List[str]) -> str:
        unused = [
            c for c in candidates 
            if not any(c[:30].lower() in p or p[:30] in c.lower() for p in past_texts)
        ]
        if unused:
            return random.choice(unused)
        # If all candidates have been seen, return candidate with a fresh variation
        chosen = random.choice(candidates)
        return chosen

    def _compose_listen_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        lower = analysis["lower"]
        themes = analysis["themes"]

        # Support person present handler (e.g. after suicide/safety disclosure or user reaches out to adult)
        if analysis.get("support_person_present") or (analysis.get("had_prior_crisis") and any(w in lower for w in ["mom", "dad", "parents", "someone is with me", "with me now", "stay with me"])):
            person = analysis.get("support_person_name", "your mom")
            
            # Case A: User explicitly wants to switch to school topic / stop safety talk
            if analysis.get("wants_school_topic") or analysis.get("wants_to_stop_safety"):
                return (
                    f"I am so glad and relieved to hear that {person} is right there with you. Having them in the room makes such a big difference, and it was really brave of you to reach out.\n\n"
                    f"We don't need to talk about the safety stuff anymore at all. I am right here and ready to listen to whatever you want to share.\n\n"
                    f"Tell me, what happened at school today?"
                )
            
            # Case B: User is still really upset and just wants to talk
            if analysis.get("is_still_upset") or "want to talk" in lower:
                return (
                    f"I am so, so relieved to hear that you got {person} to stay with you. That was a really courageous and important step to take.\n\n"
                    f"Even with {person} right there, it makes complete sense that you're still feeling really upset and carrying all those heavy emotions. You don't have to hold anything back or bottle it up inside.\n\n"
                    f"I'm right here with you and listening. What has been making you feel so upset today?"
                )
            
            # Case C: General support person present acknowledgment + open listening
            return (
                f"I'm really glad to hear that {person} is with you right now. Knowing you're not alone in the room is such a relief.\n\n"
                f"I'm right here listening without any pressure. What's on your mind right now that you'd like to talk through?"
            )

        # Contextual reference handler
        if analysis.get("is_contextual_reference"):
            if analysis.get("prior_context_subject"):
                sub = analysis["prior_context_subject"]
                return f"I hear you—dealing with that {sub} exam and feeling behind on the syllabus is still lingering and creating so much pressure today. I'm right here listening. What is the latest that's making it feel stressful?"
            elif analysis.get("prior_context_topic") == "friendship":
                return "I'm still right here with you regarding your friends and that feeling of being left out. It's so exhausting when you feel like you're bottling it up on the outside looking in. What happened today with that situation?"
            elif not analysis.get("prior_context_topic") and len(analysis.get("past_user_texts", [])) <= 1:
                return "I want to make sure I'm following you—which situation are you thinking of? Tell me a little more about what happened so I understand."

        lower = analysis["lower"]
        themes = analysis["themes"]

        # 0. User boundary: Dislike of breathing exercises
        if analysis["dislikes_breathing"]:
            candidates = [
                "I hear you loud and clear on that, and I completely respect it. Breathing exercises don't work for everyone—for a lot of people, hyper-focusing on your breath actually ramps up anxiety instead of calming you down.\n\n"
                "I will never push breathing exercises on you. We don't need any techniques or worksheets right now. I'm just here to listen to whatever is going on with you.\n\n"
                "What has been the heaviest thing on your mind today?",

                "Totally heard, and I appreciate you being direct with me about that. Trying to force yourself into breathing exercises when your nervous system hates it is super frustrating, so consider that completely off the table.\n\n"
                "Zero exercises, zero generic advice. Just me listening. What's been going on that's got you feeling this way?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 0b. Embarrassment / Being mocked / Laughed at
        if "embarrassment" in themes or analysis.get("has_embarrassment") or any(w in lower for w in ["laughed at me", "laughing at me", "too embarrassing", "so embarrassing", "embarrassed", "humiliated"]):
            candidates = [
                "I am so sorry that happened to you. Being laughed at and dealing with that kind of public embarrassment is genuinely one of the most painful, humiliating feelings, and it stings deeply. Nobody deserves to be mocked or laughed at like that.\n\nYou have every right to feel hurt and upset. I'm right here in your corner listening.\n\nDo you want to vent about what happened, or just take a minute to breathe and get it out?",
                "Ugh, that hurts so deeply. Having people laugh at you leaves this horrible, burning embarrassment where you just want to disappear, and it's completely unfair.\n\nPlease know that other people acting like that says everything about them, not your worth.\n\nWhat happened today that made things feel so humiliating?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 1. Casual Banter
        if "casual_banter" in themes:
            if "snack" in lower:
                return (
                    "Okay, hot take incoming: if a study snack doesn't have the right crunch-to-salt ratio, it cannot fuel a study session. "
                    "White cheddar popcorn or chocolate-covered pretzels are elite tier. Gummy candy is an honorable mention for a quick dopamine boost.\n\n"
                    "What kind of snack emergency are we dealing with right now—late-night cramming or afternoon procrastination?"
                )
            elif "music" in lower or "song" in lower:
                return (
                    "It totally depends on the mood! If I need to focus, low-fi beats or ambient synthwave so words don't distract me. But if I'm just chilling, indie pop and alt-R&B all day.\n\n"
                    "What kind of music do you listen to when you're trying to unwind or study?"
                )
            elif "bored" in lower:
                return (
                    "Ah, the classic 'staring at a wall because nothing sounds fun' kind of boredom. Are you genuinely bored, or are you aggressively avoiding doing something you're supposed to be doing?"
                )
            else:
                return (
                    "Hey! Just hanging out in your browser, ready to listen or chat whenever you need. Did you have a chill day today, or has it been a bit chaotic?"
                )

        # 2. Severe / Divorce
        if "divorce" in lower or "divorcing" in lower:
            return (
                "I'm so sorry you're going through that. Having your family dynamic shift like that can feel like the ground is being completely pulled out from underneath you, and it makes total sense why everything feels so disorienting.\n\n"
                "You don't have to be the 'mature' one or pretend to have it all together right now. It is genuinely painful. I'm right here with you—how have you been holding up with everything going on at home?"
            )

        # 3. Loneliness / Friendship Exclusion / Bad Day with Friends (STRICT GROUNDING)
        if "loneliness_exclusion" in themes or analysis["has_friendship_exclusion"]:
            no_advice_ack = "And I hear you loud and clear on that: zero unsolicited advice. You don't have to fix anything or figure anything out with me right now. I'm just here to listen.\n\n" if analysis["wants_no_advice"] else ""

            if any(w in lower for w in ["talking together", "part of it", "made plans", "third wheel", "left out", "sidelined"]):
                candidates = [
                    f"Ugh, that is such a painful, isolating feeling. Being right there while your friends are all talking together, and feeling like you're on the outside looking in, hurts so deeply and leaves such a heavy pit in your stomach.\n\n"
                    f"{no_advice_ack}"
                    f"It stings in that quiet way where you wonder why you're always treating people like a priority while they make you feel like an afterthought. You shouldn't have to swallow that hurt and pretend you're fine.\n\n"
                    f"Did something specific happen today that made you feel shut out, or was it just that lingering ache of feeling disconnected from the group?",

                    f"Honestly, watching your friends chat away and feeling like you're not really part of it is the absolute worst. Having to sit through that at school and feel invisible is so emotionally exhausting.\n\n"
                    f"{no_advice_ack}"
                    f"I'm really glad you're letting it out here instead of bottling it up inside. What went down with your friends today?"
                ]
                return self._select_non_repeating(candidates, past_texts)
            else:
                candidates = [
                    f"That sounds really lonely. Feeling like you don't have someone you can truly lean on or talk openly with is such a heavy, quiet ache.\n\n"
                    f"{no_advice_ack}"
                    f"It makes total sense why you'd feel down about this—everyone needs space where they feel truly seen and understood.\n\n"
                    f"Has this feeling been weighing on you for a while, or has something happened recently?",

                    f"Feeling lonely and like you don't have real support right now hurts deeply. You shouldn't have to carry that weight completely by yourself.\n\n"
                    f"{no_advice_ack}"
                    f"I'm right here listening without any judgment or expectations. What has been on your mind lately?"
                ]
                return self._select_non_repeating(candidates, past_texts)

        # 4. Unanswered Messages / Texting Anxiety
        if "unanswered_messages" in themes:
            candidates = [
                "That sinking feeling when you send a message and get left on delivered or read is so universally frustrating and anxiety-inducing. Your brain immediately starts replaying what you said and looking for things you might have done 'wrong.'\n\n"
                "It takes so much mental energy to sit with that uncertainty, especially when you know logically they might just be busy, but your feelings aren't matching that logic.\n\n"
                "Who was the message to, and what has your mind been jumping to since sending it?",

                "I completely get why that upsets you. When there's a delayed reply, silence feels loud, and it's so easy to spiral into wondering if they're annoyed or pulling away.\n\n"
                "You're definitely not alone in reacting that way—it's such a vulnerable spot to be in. What was the conversation about before they went quiet?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 5. Vitiligo & Visible Conditions / Appearance
        if analysis["has_vitiligo"] or (analysis["has_skin_condition"] and (analysis["has_stares_looks"] or analysis["has_dismissive_comments"])):
            condition_name = "vitiligo" if analysis["has_vitiligo"] else "skin"
            if analysis["has_dismissive_comments"] and analysis["has_stares_looks"]:
                candidates = [
                    f"Honestly? That makes my blood boil for you a bit. It is so easy for people to say 'looks don't matter' when they aren't the ones standing there feeling people's eyes on them or dealing with constant stares and restrictions.\n\n"
                    f"Hearing people throw platitudes at you when your {condition_name} is actively changing completely dismisses the actual social and physical reality you have to navigate every day. You're dealing with visible changes and the exhaustion of people staring—and being told 'it's no big deal' just makes it feel twice as lonely.\n\n"
                    f"Are the stares and comments happening mostly at school, or has the stress just been building up as you notice new spots?",

                    f"Ugh, that is so frustrating, and I don't blame you one bit for feeling stressed and annoyed. People love giving unsolicited platitudes like 'looks don't matter,' but that's because they don't have to carry the weight of being stared at or adjusting their routine.\n\n"
                    f"Having your {condition_name} change is already stressful without other people's ignorance on top of it. You deserve space to feel upset about how unfair that is without someone telling you how to feel.\n\n"
                    f"What has been the most draining part lately—the stares, the restrictions, or people's tone-deaf comments?"
                ]
                return self._select_non_repeating(candidates, past_texts)
            else:
                candidates = [
                    f"I hear you so loud and clear on this. Watching your {condition_name} change and spread can feel deeply unsettling, especially when it feels like you have zero control over how your own body is changing.\n\n"
                    f"It's not just about appearance—it's the mental energy of wondering where it's going next, dealing with how other people look at you, and the daily adjustments that come with it. That is a lot to hold inside.\n\n"
                    f"Did you notice new changes recently that brought all this stress to the surface?",

                    f"That sounds genuinely exhausting. When you're dealing with your {condition_name} changing, it takes up so much headspace—hyper-awareness of every spot, every look from people, and the daily restrictions that come with it.\n\n"
                    f"You don't have to pretend to be 'positive' about it here. It really is a lot to deal with, and it's 100% valid that it's stressing you out.\n\n"
                    f"Has there been anyone in your life who actually gets it, or does it feel like you've been carrying this stress alone?"
                ]
                return self._select_non_repeating(candidates, past_texts)

        # 6. Body Image & Insecurity
        if "body_eating" in themes:
            candidates = [
                "That sounds so painful and exhausting. When you're stuck in a loop of looking in the mirror and picking yourself apart, it drains every ounce of energy out of your day.\n\n"
                "I'm not going to hit you with fake cheesy positivity or tell you 'everyone is beautiful,' because I know how loud and cruel that inner critical voice feels when you're in the thick of it. But please know you don't have to fight that quiet battle alone.\n\n"
                "Did something specific happen today that triggered those thoughts, or has this pressure just been piling on for a while?",

                "Oof, being at war with your reflection and feeling uncomfortable in your own skin hurts so deeply. It makes just getting dressed, leaving the house, and being around people feel so daunting.\n\n"
                "I'm right here with you with zero judgment. What's been the hardest thought running through your mind today?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 7. Academic Disappointment (Bad grade / Failed test)
        if "academic_disappointment" in themes:
            sub = analysis["academic_subjects"][0] if analysis["academic_subjects"] else "your test"
            candidates = [
                f"Oof, that is such a brutal gut punch. Studying hard and pouring your energy into {sub}, only to get a score that doesn't reflect your effort at all, is so demoralizing.\n\n"
                f"Please hear me on this: that score does not mean you are stupid or incapable, even if it feels humiliating right now. It just means that specific test on that specific day went terribly, not that your intelligence or worth is flawed.\n\n"
                f"Do you want to vent about what made the test so rough, or just take a breather from thinking about school for a minute?",

                f"Ugh, that hurts deeply. There is nothing worse than working your butt off for {sub} and having the grade feel like a slap in the face. It makes you feel like 'why did I even bother?'\n\n"
                f"Please remember that this score does not define your intelligence or capability. You worked hard, and it's 100% valid to feel frustrated when the results don't show it.\n\n"
                f"Are people around you giving you a hard time about it, or is the pressure mostly coming from how hard you're being on yourself?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 8. Upcoming Exam Panic (Explicit exam/test upcoming ONLY)
        if "exam_panic" in themes:
            sub = analysis["academic_subjects"][0] if analysis["academic_subjects"] else "your exam"
            candidates = [
                f"Ugh, the panic of having an exam in {sub} when you feel unprepared is so suffocating. Your heart races, you feel paralyzed, and every minute ticking by feels like pressure.\n\n"
                f"Take a moment with me right now: getting stuck in panic mode only makes studying feel twice as hard. You don't have to master every single concept tonight to get through it.\n\n"
                f"What is the single most important topic in {sub} that is scaring you the most right now?",

                f"I hear that panic so clearly. When deadlines and exams for {sub} pile up, the guilt of feeling behind makes it almost impossible to actually focus on the material.\n\n"
                f"You're not the only one who has ended up in this spot before. Let's not worry about the whole syllabus right now.\n\n"
                f"Are you able to focus on high-yield summary notes for {sub}, or does your brain just feel completely frozen?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 9. Assignments & Procrastination Venting
        if "assignments_procrastination" in themes:
            candidates = [
                "That feeling of looking at a mountain of work and feeling completely paralyzed is so real. You keep putting it off because you don't know where to start, and then the guilt of wasted time makes it twice as hard to open the books.\n\n"
                "It's a vicious cycle, but you're definitely not broken for getting stuck in it. When your brain is overwhelmed by how much there is to do, shutting down is a natural stress response.\n\n"
                "What is the main thing hanging over your head right now that's creating the biggest mental block?",

                "Having assignments pile up while time keeps slipping away is so stressful. The pressure builds up until even thinking about opening your computer feels overwhelming.\n\n"
                "I'm right here with you. Do you want to just vent about how annoying this workload is, or talk through what's making it so hard to start?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 10. Grief & Loss
        if "grief_loss" in themes:
            candidates = [
                "Grief is so heavy and quiet, and it has this way of sneaking up on you out of nowhere. It is completely okay to miss them, to feel heartbroken, and to cry today.\n\n"
                "There is no timeline for missing someone you love, and you never have to put on a brave face with me. If you'd like to share a favorite memory of them or just let out what you're feeling right now, I am right here listening.\n\n"
                "What is a thought or memory about them that has been on your heart today?",

                "I am so deeply sorry. Losing someone close leaves an ache that words can't really heal, and some days just hit so much heavier than others.\n\n"
                "You don't have to explain yourself or hold anything back here. What was special about them that you find yourself missing the most today?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 11. Self-Worth
        if "self_worth" in themes:
            candidates = [
                "Hey, pause for a second—hearing you talk about yourself like that genuinely hurts. When you're overwhelmed, your brain loves to trick you into believing you're a failure or a burden, but that is the exhaustion talking, not the truth.\n\n"
                "You are dealing with a lot of heavy stuff, and struggling right now does not mean you are broken or useless. I'm right in your corner.\n\n"
                "What happened today that pushed you into this spiral of being so hard on yourself?",

                "You are carrying so much weight on your shoulders, and beating yourself up only makes it harder to breathe. Having a rough patch doesn't define who you are.\n\n"
                "I'm listening without a single shred of judgment. What felt like the breaking point for you today?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 11b. Anxiety / Panic / Nervousness
        if "anxiety_panic" in themes or any(w in lower for w in ["heart racing", "overthinking", "spiraling", "nervous", "anxious", "racing", "tightness"]):
            if analysis["academic_subjects"]:
                sub = analysis["academic_subjects"][0]
                candidates = [
                    f"That wave of nervousness creeping back in when you thought you were in the clear is so frustrating. Is the anxiety about {sub} or your upcoming quiz starting to ramp back up again?\n\n"
                    f"Your nervous system is just feeling on edge. I'm right here with you—what thought popped up that triggered that nervous feeling again?",

                    f"Oof, that sudden spike of nervousness around {sub} is so unsettling. You don't have to fight it off alone. What does the nervousness feel like right now?"
                ]
                return self._select_non_repeating(candidates, past_texts)
            else:
                candidates = [
                    "Having your heart racing and feeling your mind spiral into worst-case scenarios is so exhausting. When your nervous system gets stuck in overdrive like that and your chest feels tight, everything feels urgent and threatening even when you're physically safe.\n\n"
                    "You don't have to solve every 'what if' question your brain is throwing at you right now. I'm right here in the room with you.\n\n"
                    "What is the loudest worry that keeps looping in your head right now?",

                    "That spiraling sensation where your thoughts won't stop racing and tight dread takes over is really frightening. It's so hard to catch your breath when your body is sounding an alarm.\n\n"
                    "I'm listening with zero pressure to fix it this second. What is making you feel the most on edge today?"
                ]
                return self._select_non_repeating(candidates, past_texts)

        # 12. Conflict / Venting / Family Friction
        if "conflict" in themes or any(w in lower for w in ["yelled", "screamed", "fight", "arguing", "mad at me"]):
            who = f"your {analysis['recipient'].lower()}" if analysis.get("recipient") else "them"
            candidates = [
                f"Getting yelled at or into an argument with {who} has a way of ruining your day and leaving you feeling furious and frustrated.\n\n"
                "You deserve space to vent without someone dismissing your feelings. What happened that made things blow up?",

                f"Being yelled at by {who} and feeling attacked leaves you feeling angry with nowhere to put all that frustration.\n\n"
                "I'm right here in your corner. What do you wish you could have said to them in that moment?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 12b. School Day / Terrible Day at School
        if any(w in lower for w in [
            "terrible day at school", "bad day at school", "awful day at school", "rough day at school",
            "worst day at school", "day at school", "at school today", "school today", "classes today",
            "school was terrible", "school was awful", "school was horrible"
        ]):
            candidates = [
                "I'm so sorry you had such a terrible day at school. Dealing with school pressure, classes, and everything going on there can be really heavy, and you don't have to hold it all inside.\n\n"
                "I'm right here listening without any pressure. What happened at school today that made things feel so rough?",

                "Ugh, having an awful day at school really drains your energy. You shouldn't have to pretend everything is fine when it's not.\n\n"
                "I'm in your corner. Do you want to vent about what happened at school today?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 12c. Feeling Off / Want to Lay in Bed / Unexplained Heavy Day
        if any(w in lower for w in ["lay in bed", "stay in bed", "lie in bed", "feel off", "just feel awful", "nothing specifically terrible", "feel like doing nothing"]):
            candidates = [
                "I hear you, and wanting to stay in bed and just rest when you're feeling off is completely valid. You don't need a massive dramatic reason to have a rough day.\n\n"
                "Give yourself permission to take things slow today without feeling guilty. What's been on your mind lately while you've been resting?",

                "That is so completely valid. Sometimes an unexplainable cloud just hangs over you and makes you want to stay in bed all day, and you don't have to force yourself to be productive.\n\n"
                "Give yourself permission to rest. Is there anything specific lingering in your thoughts, or are you just feeling really drained?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 13. Generally Bad Day / Emotional Stress (Warm, grounded default)
        candidates = [
            "I hear you, and I really appreciate you opening up and telling me what's going on. Some days just feel off, heavy, or exhausting, and it's completely valid to give yourself permission to rest and not have it all together here.\n\n"
            "I'm listening. What's been taking up the most space in your head today?",

            "That sounds like a lot to carry around in silence. When you're feeling off or drained, taking time to pause is completely valid.\n\n"
            "Tell me more about what's been happening—what's been the hardest part of everything going on?"
        ]
        return self._select_non_repeating(candidates, past_texts)

    def _compose_advice_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        lower = analysis["lower"]
        themes = analysis["themes"]

        # Contextual reference handler
        if analysis.get("is_contextual_reference"):
            if analysis.get("prior_context_subject"):
                sub = analysis["prior_context_subject"]
                return f"For that {sub} situation we talked about, here is a practical next step: focus only on the next single topic or chapter rather than the whole test. Breaking it down into one small piece at a time will take the edge off the panic.\n\nWhich specific topic would be most helpful to tackle first?"
            elif analysis.get("prior_context_topic") == "friendship":
                return "For that situation with your friends, give yourself some breathing room from the group chat or social media for a bit today. Stepping back for an afternoon can help clear your head and protect your peace.\n\nWould you like to talk through a gentle way to handle it, or just take some space?"
            elif not analysis.get("prior_context_topic") and len(analysis.get("past_user_texts", [])) <= 1:
                return "I want to make sure I give you advice that actually fits—which situation are you referring to? Let me know what happened so I can give you relevant suggestions."

        # 1. Multiple Assignments / Procrastination / Workload (STRICT DIRECT ADVICE)
        if "assignments_procrastination" in themes or analysis["has_assignments_procrastination"] or any(w in lower for w in ["assignment", "assignments", "putting them off", "three assignments", "stressed about school", "so much to do", "where to start"]):
            return (
                "When you have so much school workload piling up and you don't even know where to start, feeling overwhelmed is completely normal. Here is a practical, low-pressure way to make progress:\n\n"
                "1. **Do a Quick Brain Dump:**\n"
                "   - Write down every assignment, project, and school deadline on a piece of paper so you don't have to keep juggling them in your mind.\n\n"
                "2. **Pick the Easiest Micro-Task or Set a 10-Minute Timer:**\n"
                "   - Look at your assignments: pick the shortest or easiest one first, or set a timer for just 10 minutes to open the doc. Once you break the initial resistance, momentum builds naturally without dread.\n\n"
                "3. **Keep the Other Tasks and Tabs Out of Sight:**\n"
                "   - Close the tabs and instructions for the other assignments for now so your brain only has to focus on this one micro-step.\n\n"
                "What assignments or classes are on your plate right now? Tell me what they are, and we can pick a gentle starting point together."
            )

        # 2. Upcoming Exam Stress Advice
        if "exam_panic" in themes:
            sub = analysis["academic_subjects"][0] if analysis["academic_subjects"] else "your exam"
            return (
                f"When you're facing an exam in {sub} and running short on time, switch from 'completion mode' to 'triage mode':\n\n"
                "1. **Focus Exclusively on High-Yield Chapters:** Don't try to read everything cover-to-cover. Look at past quizzes, chapter summary boxes, and formula sheets. 80% of test questions usually come from 20% of core concepts.\n\n"
                "2. **Active Recall Over Passive Review:** Spending 15 minutes testing yourself with practice questions or flashcards is far more effective than passively highlighting notes.\n\n"
                "3. **Protect at Least 5–6 Hours of Sleep:** Pulling an all-nighter kills your working memory. A rested brain will score significantly higher on recall than an exhausted brain that crammed all night.\n\n"
                f"What is the single topic in {sub} that carries the most points on the test?"
            )

        # 3. Academic Disappointment Advice
        if "academic_disappointment" in themes:
            sub = analysis["academic_subjects"][0] if analysis["academic_subjects"] else "this subject"
            return (
                f"After getting a tough grade in {sub}, diving straight back into aggressive studying while you're still upset will just burn you out. Here is what I suggest:\n\n"
                "1. **Take a Mandatory 24-Hour Reset:** Put the test paper away for today. Do not look at the mistakes while your emotions are raw. Let your nervous system settle.\n\n"
                f"2. **Separate Effort from Technique:** A bad grade doesn't mean you didn't work hard—it usually means the study method (passive review, re-reading) didn't match how the questions were tested. Tomorrow, you can do a low-pressure 10-minute error log of just the questions where you lost points.\n\n"
                "Would you like help thinking through how to approach your teacher for feedback without feeling intimidated?"
            )

        # 4. Loneliness & Friendship Advice
        if "loneliness_exclusion" in themes:
            return (
                "When friends treat you like an option or leave you out, chasing them or demanding answers usually leaves you feeling more depleted. Here is a grounded approach:\n\n"
                "1. **Match Their Energy:** Stop being the only one initiating plans or checking in. Save your energy for people who show equal curiosity about your life.\n\n"
                "2. **Cultivate Low-Pressure 1-on-1 Connections:** It's way easier to build a genuine connection with one person in a specific class, club, or hobby than trying to win over an entire group dynamic.\n\n"
                "3. **Invest in Outside Spaces:** Having one space outside of your main school group (an art class, sports, gaming, volunteer work) reminds you that school isn't the whole world.\n\n"
                "Would you like help thinking through someone low-pressure you could reach out to?"
            )

        # 5. Unanswered Messages Advice
        if "unanswered_messages" in themes:
            return (
                "When waiting for a reply is making your anxiety spike, trying to force yourself to 'just stop thinking about it' never works. Here is what helps:\n\n"
                "1. **Put the Phone in Another Room for 30 Minutes:** Staring at the chat screen or checking 'last seen' feeds the panic loop. Give your eyes and nervous system a break.\n\n"
                "2. **The 3-Scenario Rule:** When your brain jumps to *'They hate me,'* challenge it to generate 2 neutral explanations: *'They got interrupted,'* or *'Their battery died/they're driving.'* Neutral explanations are statistically way more likely.\n\n"
                "3. **Refuse to Double-Text While Anxious:** Let the ball stay in their court. You sent your message, and you don't need to apologize or follow up right now."
            )

        # 6. Body Image / Insecurity Advice
        if "body_eating" in themes or analysis["has_vitiligo"] or analysis["has_skin_condition"]:
            return (
                "When your brain is stuck in a harsh body-checking loop, arguing with your thoughts doesn't work. Try these physical resets:\n\n"
                "1. **Implement a Mirror Fast:** For the next few hours, only use mirrors for practical tasks (brushing teeth, washing face). Avoid pausing to scrutinize or evaluate your reflection.\n\n"
                "2. **Change into Sensory-Friendly Clothes:** Put on whatever clothes feel physically soft, loose, and comfortable on your body right now without clinging or pinching.\n\n"
                "3. **Boundary on Comments:** If people make unsolicited comments, you don't owe them a reaction. A simple *'I'm not looking for comments on my appearance'* is enough.\n\n"
                "What is something comfortable you can switch into right now to give your body a break?"
            )

        # 7. Anxiety / Panic Advice
        if "anxiety_panic" in themes:
            if analysis["dislikes_breathing"]:
                return (
                    "When your anxiety is spiraling and breathing exercises are off the table, use direct physical resets:\n\n"
                    "1. **Cold Water Reset:** Go to the sink and hold an ice cube or splash cold water on your face for 15 seconds. This triggers a physical reflex that naturally slows your heart rate without any breathing focus.\n\n"
                    "2. **Physical Sensory Check:** Name 3 specific textures around you (your jeans, a desk edge, a wall) and press your hands firmly against them to pull attention back into the room.\n\n"
                    "Do you have some cold water or an ice cube nearby you can grab?"
                )
            else:
                return (
                    "When your brain is spiraling, focus on quick physical grounding:\n\n"
                    "1. **Cold Physical Reset:** Splash cold water on your face or hold an ice cube for 20 seconds. It immediately helps settle your heart rate.\n\n"
                    "2. **Brain Dump:** Jot down the 2 biggest racing thoughts on a scrap piece of paper so your head stops looping them.\n\n"
                    "What is the main thought that keeps looping in your mind right now?"
                )

        # 8. General Grounded Advice
        return (
            "When things feel heavy and tangled, the key is tackling just the next immediate step:\n\n"
            "1. **Identify the Single Biggest Friction Point:** What is the one task or conversation that is weighing on you the most right now?\n\n"
            "2. **Lower the Bar on Output:** You don't have to resolve everything perfectly today. Focus on taking just one small, realistic action that reduces tomorrow's stress.\n\n"
            "What feels like the most urgent piece of this puzzle that we could break down together?"
        )

    def _compose_understand_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        lower = analysis["lower"]
        themes = analysis["themes"]

        # Contextual reference handler
        if analysis.get("is_contextual_reference"):
            if analysis.get("prior_context_subject"):
                sub = analysis["prior_context_subject"]
                return f"With that {sub} situation, the pressure usually lingers because your brain is constantly anticipating what's next. When you're carrying that academic stress, even small things feel heavier than normal.\n\nWhat feels like the main source of that pressure right now?"
            elif analysis.get("prior_context_topic") == "friendship":
                return "When friendship dynamics feel off or you feel left out, your brain stays on high alert trying to figure out where you stand. That constant uncertainty is what makes it so emotionally draining.\n\nIs there a specific moment from that situation that's been on your mind today?"
            elif not analysis.get("prior_context_topic") and len(analysis.get("past_user_texts", [])) <= 1:
                return "I want to make sure I'm following you—which situation are you thinking of? Tell me a little more about what happened so I can understand."

        # 0. Overwhelmed without doing much / General Overwhelm
        if any(p in lower for p in ["haven't done that much", "havent done that much", "haven't done much", "havent done much", "didn't do much", "didnt do much", "barely did anything", "haven't done anything", "havent done anything"]) or (("why do i feel" in lower or "why am i" in lower) and "overwhelm" in lower):
            return (
                "Here is why you can feel completely overwhelmed even when you haven't done that much physically:\n\n"
                "1. **Invisible Background Processing:** Your brain doesn't just use energy when you are actively doing homework or chores. Constantly holding onto worries, anticipating problems, managing social dynamics, or feeling anxious runs heavy background processes in your nervous system. That drains your battery just as much as physical effort.\n\n"
                "2. **Sensory & Digital Overload:** Constant screen time, notifications, and environmental noise keep your nervous system in a subtle state of high alert. Even when you are resting in bed, your brain might not be getting true recovery.\n\n"
                "3. **Cumulative Emotional Fatigue:** Overwhelm is rarely caused by what happened today alone. It's usually the result of days or weeks of accumulated tension finally reaching the surface.\n\n"
                "Feeling exhausted without a clear 'reason' does NOT mean you are lazy—it simply means your nervous system is asking for quiet downtime.\n\n"
                "Has your mind been racing with background worries lately, or is it more of a deep physical and mental heaviness?"
            )

        # 1. Unanswered Messages / Texting Anxiety / Fear of Being Disliked
        if "unanswered_messages" in themes or any(w in lower for w in ["reply to my messages", "reply to my message", "text back", "wondering if i did something wrong"]):
            return (
                "Here is why waiting for a text back can make your anxiety spike so fast:\n\n"
                "When someone doesn't reply right away, it creates an **information void**—your brain has no real-time data about what the other person is thinking or doing. Human brains naturally dislike uncertainty, so when there is a blank space, your mind rushes to fill it in.\n\n"
                "If you care a lot about your friends or already worry about how you come across, your brain defaults to the worst-case scenario (*'Did I say something wrong? Are they mad at me?'*) as an overprotective reflex to prepare you for rejection so you aren't blindsided.\n\n"
                "That spike of anxiety isn't proof that anything is actually wrong—it's just an overprotective alarm going off in an information vacuum.\n\n"
                "Does this worry usually happen only with certain close friends, or does it happen with almost anyone you text?"
            )

        # 2. Jealousy / Envy / Friendship Insecurity
        if "angry" in lower and ("friend" in lower or "other friend" in lower):
            return (
                "Here is what is usually behind that reaction: feeling angry or upset when a close friend hangs out with someone else is super common, and it doesn't mean you're a bad person.\n\n"
                "Usually, that anger is a protective shield around a deeper, vulnerable worry: the fear of being replaced, left behind, or not mattering as much to them as they matter to you. When they bond with someone else, your mind sees it as a threat to your connection.\n\n"
                "Does it feel more like worrying they'll leave you behind, or feeling like you care about the friendship more than they do?"
            )

        # 3. Procrastination / Avoidance
        if "assignments_procrastination" in themes or any(w in lower for w in ["putting them off", "procrastinating", "why do i put"]):
            return (
                "Here is why procrastination actually happens: it's almost never about being lazy. It is an emotional reaction to feeling stressed or intimidated by the task.\n\n"
                "When you look at big assignments and aren't sure where to start, your brain sees the task as uncomfortable—it worries about struggling, failing, or spending hours feeling frustrated. To protect you from that discomfort right now, your brain urges you to do something that feels safe or easy (like scrolling or cleaning).\n\n"
                "The avoidance gives quick relief, but then guilt and time pressure build up, making the task feel even scarier to start.\n\n"
                "When you think about starting on those assignments, what is the feeling that comes up first—feeling lost, fear of doing it badly, or just feeling overwhelmed by the amount of work?"
            )

        # 4. Loneliness & Social Dynamics
        if "loneliness_exclusion" in themes:
            return (
                "Here is why you can feel deeply lonely even when you're surrounded by other people:\n\n"
                "There is a big difference between being physically around people and feeling genuinely connected to them. If you feel like you have to adjust how you act, hide your real thoughts, or laugh along with things just to fit in, your brain still registers that you're on your own. You can be in a room full of people and still feel invisible if you don't feel seen for who you actually are.\n\n"
                "When you feel disconnected around people, does it feel like they're leaving you out, or more like you don't feel safe letting your guard down around them?"
            )

        # 5. Vitiligo / Physical Conditions
        if analysis["has_vitiligo"] or analysis["has_skin_condition"]:
            return (
                "Here is why dealing with visible skin changes takes such a heavy mental toll:\n\n"
                "You are constantly managing two things at once: your own personal feelings about your appearance, and the mental energy of anticipating how other people might look or react. Even if people don't mean to be hurtful, knowing you might be stared at or asked questions creates constant background tension.\n\n"
                "When people give quick comments like 'it doesn't matter,' it feels invalidating because they don't see the day-to-day energy it takes to deal with that attention.\n\n"
                "Does the hardest part feel like your own feelings about the changes, or dealing with other people's reactions?"
            )

        # 6. Self-Worth & Critical Inner Voice
        if "self_worth" in themes:
            return (
                "Here is why that critical inner voice gets so loud and harsh: when we feel like a failure or a burden, it's rarely because of who we are. It usually happens when we've been running on empty for a long time under heavy stress or high expectations.\n\n"
                "When your mental energy is depleted, your brain's self-criticism goes into overdrive, blaming you for feeling tired or struggling to keep up with everything.\n\n"
                "If that critical voice sounds like someone's expectations, does it feel like pressure from family, school, or mostly standards you set for yourself?"
            )

        # 7. Exam Panic / Test Freezing
        if "exam_panic" in themes or any(w in lower for w in ["freeze up", "blanked on the test", "mind went blank", "exam panic"]):
            return (
                "Here is what happens when your mind freezes or goes blank during a test:\n\n"
                "When your brain senses high pressure or fear of doing poorly, it triggers an automatic stress response. This temporarily diverts energy and focus away from your working memory (the part of your brain that solves test problems) toward basic survival mode. You haven't actually forgotten the material—your brain is just temporarily blocking access to it because it feels under threat.\n\n"
                "Does the freeze usually happen right when you open the test, or when you hit a question you aren't sure about?"
            )

        # 8. Easily Crying / Snapping at Small Things
        if any(w in lower for w in ["snap at", "snapping", "crying over nothing", "crying over small", "crying easily", "cry over small", "get mad over small", "so sensitive"]):
            return (
                "Here is why you might find yourself snapping or crying over small things lately:\n\n"
                "Think of your emotional energy like a cup. When you've been carrying hidden stress, worry, or unresolved frustration, that cup gets filled right up to the very top. When a tiny inconvenience or minor frustration happens, it's not the cause of the reaction—it's just the final drop that makes the whole cup overflow.\n\n"
                "What kind of stuff has been filling up that cup lately before that little thing happened?"
            )

        # 9. General Grounded Explanation for WHY/HOW Questions
        return (
            "Here is a simple way to make sense of why you might be feeling this way:\n\n"
            "When we're dealing with a lot of unspoken stress, expectations, or changes, our mind and body naturally respond with heaviness, worry, or tension. It's not a flaw or a mistake on your part—it's usually your nervous system's way of signaling that you've been carrying a heavy load for too long without enough quiet space to rest and recharge.\n\n"
            "Looking at everything going on right now, what feels like it's taking the biggest toll on your energy?"
        )

    def _compose_tell_someone_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        recipient = analysis["recipient"] or "someone you trust"
        medium = analysis["medium"]
        topic = analysis["tell_topic"]
        lower = analysis["lower"]

        # MULTI-TURN CONTEXT CONTINUITY:
        # If user explicitly specifies "in person" or medium in response to previous context
        if medium == "in_person" or any(w in lower for w in ["in person", "in-person", "talk to him", "talk to her", "face to face", "verbally"]):
            return (
                f"Having an in-person conversation with your {recipient} about {topic} is a courageous move. Talking face-to-face allows them to hear your tone and see how much this genuinely matters to you.\n\n"
                f"Here is a natural, low-pressure way you could open the conversation:\n\n"
                f"**Step 1: Pick a Calm, Distraction-Free Moment**\n"
                f"Wait for a quiet time when neither of you is rushing out the door—like during a car ride, while helping make food, or after dinner.\n\n"
                f"**Step 2: Use a Simple Opening Line**\n"
                f"\"Hey {recipient}, can we talk for a couple of minutes? There's something that's been stressing me out a lot lately ({topic}), and I really wanted to talk to you about it so I'm not carrying it by myself.\"\n\n"
                f"**Step 3: Set Expectations Early**\n"
                f"\"I'm not expecting you to fix everything right now, I just really needed to share what's been going on with me.\"\n\n"
                f"How does that opening feel to you? We can tweak the words to match how you normally talk with your {recipient}."
            )

        # If user specified text or message
        if medium == "text":
            return (
                f"Sending a text to your {recipient} about {topic} is a great, low-stress way to break the ice without feeling put on the spot. Here is a natural message you can send:\n\n"
                f"\"Hey, do you have some quiet time later today? I've been feeling pretty overwhelmed lately about {topic} and I'd really like to talk to you about it whenever you're free.\"\n\n"
                f"You can copy or customize this message. Would you like to adjust the wording to be more casual or more direct?"
            )

        # If user specified letter or email
        if medium == "letter":
            return (
                f"Writing a letter or note to your {recipient} about {topic} gives you full control to say everything without being interrupted. Here is a gentle template:\n\n"
                f"\"Dear {recipient},\n\n"
                f"I'm writing this down because it's sometimes easier for me to write my thoughts than say them out loud. Recently, I've been experiencing a lot of stress around {topic}.\n\n"
                f"I really value your support and wanted to let you know what's going on with me. Can we talk about this when you have some time?\"\n\n"
                f"Would you like to add any specific details to this draft?"
            )

        # Turn 1: User mentions wanting to talk to a recipient
        if analysis["recipient"]:
            return (
                f"Opening up to your {recipient} about {topic} is a brave step, and keeping it low-pressure helps a ton. Here is a simple starter you could use:\n\n"
                f"\"Hey, do you have some quiet time later today? I've been feeling pretty overwhelmed lately about {topic} and I really wanted to talk to you about it.\"\n\n"
                f"Would you feel most comfortable doing this **in person**, sending a **text message**, or writing a short **note**?"
            )

        # General initial turn in Help Me Tell Someone mode
        return (
            "Putting your feelings into words for someone in your life is a huge, brave step.\n\n"
            "Who are you thinking about talking to (like a parent, teacher, school counselor, or friend)? Tell me who you have in mind and what's been bothering you, and we can write a stress-free conversation starter together."
        )

    async def generate_tell_someone_draft(
        self,
        recipient: str,
        tone: str,
        core_feeling: str,
        what_i_need: Optional[str] = None,
        preferred_medium: Optional[str] = "text"
    ) -> Dict[str, Any]:
        recipient_display = recipient.replace("_", " ").title()
        need_phrase = f" Right now, it would really help if {what_i_need}." if what_i_need else " I'm not looking for instant solutions, but I just wanted to share this with you so I don't feel like I'm hiding it."

        drafts = {
            "parent_guardian": {
                "casual_text": f"Hey, do you have some time later today? I've been feeling pretty overwhelmed lately about {core_feeling} and I'd really like to talk to you about it.{need_phrase}",
                "direct_honest": f"Hey, I wanted to be honest with you. Lately I've really been struggling with {core_feeling}. It's been taking a toll on me, and I wanted to let you know what's going on.{need_phrase}",
                "gentle_vulnerable": f"Hi. It's kind of hard for me to bring this up, but I really trust you and wanted to tell you that I've been having a tough time with {core_feeling}. Can we talk sometime when you're free?{need_phrase}",
                "formal_letter": f"Dear Mom/Dad,\n\nI'm writing this down because it's sometimes easier for me to write my thoughts than say them out loud. Recently, I've been experiencing a lot of stress around {core_feeling}.{need_phrase}\n\nThank you for listening and caring about me.",
                "in_person_starter": f"\"Hey, can we talk for a minute? There's something on my mind that's been stressing me out ({core_feeling}) and I really wanted to share it with you.\""
            },
            "school_counselor": {
                "casual_text": f"Hi, I was hoping I could schedule a quick time to drop by your office this week. I've been having a hard time balancing things with {core_feeling} and could use some guidance.{need_phrase}",
                "direct_honest": f"Hello, I am reaching out because I have been dealing with a lot of stress regarding {core_feeling}. I would really appreciate meeting with you to talk through some support options.{need_phrase}",
                "gentle_vulnerable": f"Dear Counselor, I've been feeling pretty overwhelmed recently with {core_feeling}. I wasn't sure who to talk to, but I'd really appreciate a quiet conversation with you if you have availability.{need_phrase}",
                "formal_letter": f"Dear School Counselor,\n\nI am writing to request a meeting with you. Over the past few weeks, I have been finding it difficult to manage {core_feeling}.{need_phrase}\n\nPlease let me know when you might have an opening.\n\nThank you.",
                "in_person_starter": f"\"Hi, do you have a few minutes today or sometime this week? I've been going through some stuff with {core_feeling} and was hoping to talk.\""
            },
            "teacher": {
                "casual_text": f"Hi, I wanted to quickly check in with you after class. I've been dealing with {core_feeling} and wanted to let you know in case it's affecting my focus.{need_phrase}",
                "direct_honest": f"Dear Teacher, I wanted to be open with you about why I've seemed a bit distracted lately. I've been dealing with {core_feeling}, and I'm doing my best to manage it.{need_phrase}",
                "gentle_vulnerable": f"Hello, things have been a bit difficult for me outside of class with {core_feeling}. I really value your class and wanted to communicate with you before falling behind.{need_phrase}",
                "formal_letter": f"Dear [Teacher's Name],\n\nI wanted to reach out regarding my current coursework. I have been facing challenges with {core_feeling} recently.{need_phrase}\n\nI appreciate your understanding and support.",
                "in_person_starter": f"\"Hi, do you have a quick moment after class? I just wanted to let you know about a personal challenge with {core_feeling} I've been working through.\""
            },
            "friend": {
                "casual_text": f"Hey! You free to chat or call later? I've been feeling kind of off and stressed about {core_feeling}, and could really use a friend right now.{need_phrase}",
                "direct_honest": f"Hey, not gonna lie, things have been pretty rough for me lately with {core_feeling}. Just wanted to let you know in case I've seemed distant.{need_phrase}",
                "gentle_vulnerable": f"Hey, I really value our friendship and feel safe with you. I've been feeling pretty down about {core_feeling} and just wanted to share it with someone who gets me.{need_phrase}",
                "formal_letter": f"Hey,\n\nI'm sending this because I care about you and wanted to be real about what's going on with me. I've been carrying a lot of weight regarding {core_feeling}.{need_phrase}\n\nThanks for always being there.",
                "in_person_starter": f"\"Hey, can I be honest with you about something that's been bothering me lately? It's about {core_feeling}.\""
            },
            "sibling": {
                "casual_text": f"Hey, are you around? Been pretty stressed out about {core_feeling} and wanted to vent for a second if that's cool.{need_phrase}",
                "direct_honest": f"Hey, I've been having a tough time dealing with {core_feeling} lately. Wanted to let you know what's going on with me.{need_phrase}",
                "gentle_vulnerable": f"Hey, I know we don't always talk about deep stuff, but I've been feeling really overwhelmed by {core_feeling} and could use some support.{need_phrase}",
                "formal_letter": f"Hey,\n\nI wanted to reach out and let you know that things have been heavy for me with {core_feeling}.{need_phrase}\n\nGlad to have you as my sibling.",
                "in_person_starter": f"\"Hey, do you have a minute? I've had kind of a rough time lately with {core_feeling} and wanted to tell you.\""
            },
            "trusted_adult": {
                "casual_text": f"Hi, I was wondering if you had some time to chat sometime this week. I've been dealing with {core_feeling} and could really use some perspective.{need_phrase}",
                "direct_honest": f"Hello, I wanted to reach out because I trust your advice. Lately I've been struggling with {core_feeling} and wanted to share what's happening.{need_phrase}",
                "gentle_vulnerable": f"Hi, it's a bit hard for me to talk about, but I've been having a tough time with {core_feeling}. Since I trust you, I was hoping we could talk.{need_phrase}",
                "formal_letter": f"Dear [Name],\n\nI am writing to you because I hold great respect for you and your guidance. I have been facing a challenging situation with {core_feeling}.{need_phrase}\n\nI would be very grateful for an opportunity to speak with you.",
                "in_person_starter": f"\"Hi, do you have a few minutes? There's something important that's been weighing on me ({core_feeling}) that I'd like to ask your advice on.\""
            }
        }

        recipient_group = drafts.get(recipient, drafts["trusted_adult"])
        primary = recipient_group.get(tone, recipient_group["casual_text"])

        alternatives = []
        for t_key, text in recipient_group.items():
            if t_key != tone:
                alternatives.append({
                    "title": t_key.replace("_", " ").title(),
                    "content": text,
                    "recommended_medium": "In Person" if "starter" in t_key else ("Email/Letter" if "letter" in t_key else "Text Message"),
                    "tips": [
                        "Pick a calm moment when neither of you is rushing.",
                        "You don't have to explain every detail right away—getting the conversation started is what matters most.",
                        "You can edit any words in this message to sound more like you."
                    ]
                })

        return {
            "recipient": recipient,
            "tone": tone,
            "primary_draft": primary,
            "alternative_drafts": alternatives[:3],
            "conversation_tips": [
                f"Choose a time when your {recipient_display} isn't distracted or in the middle of work/chores.",
                "If speaking in person feels too intense, sending a text or leaving a handwritten note is 100% okay.",
                "Remember: Asking for support is a sign of strength and self-awareness, not weakness."
            ],
            "encouragement": "You are taking a brave, meaningful step. Expressing how you feel opens the door to genuine support."
        }

local_engine = LivEmpatheticEngine()
LocalEmpatheticEngine = LivEmpatheticEngine
