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
        elif mode == "help_me_tell_someone":
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
        combined_past = " ".join(past_user_texts)
        full_conversation_text = (combined_past + " " + lower).strip()

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
        if any(w in full_conversation_text for w in ["dad", "father", "stepdad"]):
            recipient = "Dad"
        elif any(w in full_conversation_text for w in ["mom", "mother", "stepmom"]):
            recipient = "Mom"
        elif any(w in full_conversation_text for w in ["parent", "parents", "family"]):
            recipient = "Parents"
        elif any(w in full_conversation_text for w in ["counselor", "school counselor", "therapist"]):
            recipient = "School Counselor"
        elif any(w in full_conversation_text for w in ["teacher", "professor"]):
            recipient = "Teacher"
        elif any(w in full_conversation_text for w in ["friend", "best friend", "bff"]):
            recipient = "Friend"
        elif any(w in full_conversation_text for w in ["sibling", "brother", "sister"]):
            recipient = "Sibling"
        elif any(w in full_conversation_text for w in ["trusted adult", "adult", "guardian"]):
            recipient = "Trusted Adult"

        # Communication Medium for Telling Someone
        medium = None
        if any(w in lower for w in ["in person", "face to face", "in-person", "talk to him", "talk to her", "out loud", "verbally"]):
            medium = "in_person"
        elif any(w in lower for w in ["text", "message", "texting", "dm", "whatsapp"]):
            medium = "text"
        elif any(w in lower for w in ["letter", "email", "note", "written"]):
            medium = "letter"
        elif any(w in combined_past for w in ["in person", "in-person"]):
            medium = "in_person"

        # Topic for Telling Someone
        tell_topic = "what's been on your mind"
        if any(w in full_conversation_text for w in ["school", "stressing me out", "stress", "overwhelmed", "assignments", "homework", "grades"]):
            tell_topic = "school stress and feeling overwhelmed"
        elif any(w in full_conversation_text for w in ["anxiety", "panic", "racing thoughts", "mental health"]):
            tell_topic = "anxiety and mental wellbeing"
        elif any(w in full_conversation_text for w in ["lonely", "friends", "friendship", "left out", "drama"]):
            tell_topic = "friendship and feeling isolated"

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
            "dont know where to start", "wasted so much time", "what should i actually do",
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
            "exam tomorrow", "test tomorrow", "quiz tomorrow", "finals tomorrow", "exam on friday",
            "quiz on friday", "test on friday", "haven't finished half", "havent finished half",
            "haven't finished studying", "havent finished studying", "haven't finished the syllabus",
            "havent finished the syllabus", "panicking about my exam", "panicking about my test",
            "failing my chemistry exam", "failing my math exam", "failing my exam", "cramming for my exam",
            "exam in the morning", "finals week"
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
        
        if has_friendship_exclusion:
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

        if any(w in lower for w in ["heart racing", "overthinking", "spiraling", "can't breathe", "dread", "shaking", "suffocating", "won't stop racing"]):
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
            "is_casual_banter": is_casual_banter,
            "raw": text,
            "lower": lower,
            "history_count": len(history),
            "past_user_texts": past_user_texts
        }

    def _select_non_repeating(self, candidates: List[str], past_texts: List[str]) -> str:
        unused = [c for c in candidates if not any(c[:35].lower() in p for p in past_texts)]
        if unused:
            return random.choice(unused)
        return random.choice(candidates)

    def _compose_listen_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
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
                    f"That sounds really lonely. That feeling where you're surrounded by people, but feel like you don't really have anyone who genuinely understands you or checks in on you, is such a heavy, quiet ache.\n\n"
                    f"{no_advice_ack}"
                    f"It makes total sense why you'd feel down about this—everyone needs at least one person where they don't have to put on an act to feel included.\n\n"
                    f"Has it felt like this for a while, or has something shifted recently with the people around you?",

                    f"Feeling like you don't have any real friends to lean on hurts deeply. You start questioning yourself even though you haven't done anything wrong, and being in that headspace is really tough.\n\n"
                    f"{no_advice_ack}"
                    f"I'm right here listening without any judgment. What has your day-to-day felt like lately when you're around people?"
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

        # 12. Conflict / Venting
        if "conflict" in themes:
            candidates = [
                "Fighting with someone close has a way of ruining your whole day and looping in your mind for hours. It is so exhausting when you feel like they aren't even hearing what you're actually trying to say.\n\n"
                "You deserve space to vent without someone telling you to 'just calm down.' What happened that made things blow up?",

                "Getting into arguments and feeling misunderstood or attacked is so draining. It leaves you feeling angry and frustrated with nowhere to put all that energy.\n\n"
                "I'm right here listening. What do you wish you could have said to them in that moment?"
            ]
            return self._select_non_repeating(candidates, past_texts)

        # 13. Generally Bad Day / Emotional Stress (Warm, grounded default)
        candidates = [
            "I hear you, and I really appreciate you opening up and telling me what's going on. Some days just feel so heavy and weirdly exhausting, and you don't have to pretend to have it together here.\n\n"
            "I'm listening. What's been taking up the most space in your head today?",

            "That sounds like a lot to carry around in silence. Sometimes getting the mess out of your head and into words takes the edge off a little bit.\n\n"
            "Tell me more about what's been happening—what's been the hardest part of everything going on?"
        ]
        return self._select_non_repeating(candidates, past_texts)

    def _compose_advice_response(self, text: str, analysis: Dict[str, Any], past_texts: List[str]) -> str:
        lower = analysis["lower"]
        themes = analysis["themes"]

        # 1. Multiple Assignments / Procrastination / Workload (STRICT DIRECT ADVICE)
        if "assignments_procrastination" in themes or analysis["has_assignments_procrastination"] or any(w in lower for w in ["assignment", "assignments", "putting them off", "three assignments"]):
            return (
                "When you have multiple assignments piling up and deadline paralysis has set in, looking at all three at once will keep you frozen. Here is the exact game plan to break the deadlock:\n\n"
                "1. **Triage by Urgency & Friction (Pick Your Target):**\n"
                "   - Look at the three assignments and sort them: which one has the hard deadline first, and which one is the smallest/easiest? If they're all due at the same time, pick the *easiest* one first just to get points on the board and break the friction.\n\n"
                "2. **The 10-Minute 'Garbage First Draft' Sprint:**\n"
                "   - Do NOT try to finish the assignment right now. Set a timer on your phone for 10 minutes. Open the document and write 3 messy bullet points, open the questions, or draft the roughest possible start. Lowering the bar from 'perfect' to 'terrible' gets the engine running.\n\n"
                "3. **Single-Task Only:**\n"
                "   - Hide the tabs and rubrics for the other two assignments. Focusing on one single task reduces cognitive overwhelm immediately.\n\n"
                "What are the 3 assignments? Tell me what each one is, and we can pick the single best one to start on right now in 2 minutes."
            )

        # 2. Upcoming Exam Stress Advice
        if "exam_panic" in themes:
            sub = analysis["academic_subjects"][0] if analysis["academic_subjects"] else "your exam"
            return (
                f"When you're facing an exam in {sub} and running short on time, switch from 'completion mode' to 'triage mode':\n\n"
                "1. **Focus Exclusively on High-Yield Chapters:** Don't try to read everything cover-to-cover. Look at past quizzes, chapter summary boxes, and formula sheets. 80% of test questions usually come from 20% of core concepts.\n\n"
                "2. **Active Recall Over Re-Reading:** Spending 15 minutes testing yourself with practice questions or flashcards is 3x more effective than passively highlighting notes.\n\n"
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
                "1. **Match Their Energy (The Mirror Rule):** Stop being the only one initiating plans or checking in. Save your energy for people who show equal curiosity about your life.\n\n"
                "2. **Cultivate Low-Pressure 1-on-1 Micro-Bonds:** It's way easier to build a genuine connection with one person in a specific class, club, or hobby than trying to win over an entire group dynamic.\n\n"
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
                    "1. **Ice Water Shock:** Go to the sink and hold an ice cube or splash freezing cold water on your face for 15 seconds. This triggers the dive reflex to slow your physical heart rate without any breathing focus.\n\n"
                    "2. **Physical Sensory Dump:** Name 3 specific rough textures around you (your jeans, a desk edge, a wall) and press your hands firmly against them to pull attention into the room.\n\n"
                    "Do you have some cold water or an ice cube nearby you can grab?"
                )
            else:
                return (
                    "When your brain is spiraling, focus on quick physical grounding:\n\n"
                    "1. **Cold Physical Reset:** Splash freezing water on your face or hold an ice cube for 20 seconds. It immediately drops your heart rate.\n\n"
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

        # 1. Unanswered Messages / Texting Anxiety / Fear of Being Disliked (STRICT GROUNDING)
        if "unanswered_messages" in themes or any(w in lower for w in ["reply to my messages", "reply to my message", "text back", "wondering if i did something wrong"]):
            return (
                "Here is what is actually going on underneath that reaction:\n\n"
                "When someone doesn't reply right away, it creates an **information void**—your brain has no real-time data about what the other person is thinking or doing. "
                "Human brains hate uncertainty, so when there is a blank space, your mind instinctively rushes to fill in the missing information.\n\n"
                "If you're someone who cares deeply about your connections or already worries about how people perceive you, your brain's threat-detection system defaults to the worst-case scenario (*'Did I say something wrong? Are they mad at me?'*) as an overprotective defense mechanism. It tries to anticipate rejection so you won't be caught off guard.\n\n"
                "So that spike of anxiety isn't proof that you did something wrong—it's just an overprotective alarm going off in an information vacuum.\n\n"
                "Does this pattern usually happen only with certain close friends, or does it happen with almost anyone you text?"
            )

        # 2. Jealousy / Envy / Friendship Insecurity
        if "angry" in lower and ("friend" in lower or "other friend" in lower):
            return (
                "Let's untangle this without any judgment or self-blame. Feeling angry when a close friend talks about their other friends is super common, and it doesn't make you a bad person.\n\n"
                "Usually, that anger isn't about being mean—it's a protective shield around a deeper fear: the fear of being replaced, forgotten, or not being as important to them as they are to you. When they bond with someone else, your brain interprets it as a threat to your emotional safety.\n\n"
                "Does the feeling feel more like worrying they'll leave you behind, or feeling like you value the friendship more than they do?"
            )

        # 3. Procrastination / Avoidance
        if "assignments_procrastination" in themes or any(w in lower for w in ["putting them off", "procrastinating", "why do i put"]):
            return (
                "Here is why procrastination actually happens: it's almost never about laziness. It's an **emotional regulation** issue.\n\n"
                "When you look at three assignments and don't know where to start, your brain perceives the task as a threat—a threat of failure, of feeling stupid, or of spending hours feeling frustrated. To protect you from that discomfort, your brain seeks immediate relief (scrolling on your phone, doing literally anything else).\n\n"
                "The avoidance gives temporary relief, but then guilt and time pressure kick in, which increases the stress and makes the task feel even more threatening.\n\n"
                "When you think about starting on those assignments, what is the specific feeling that pops up first—boredom, fear of doing it badly, or just feeling overwhelmed by the sheer volume?"
            )

        # 4. Loneliness & Social Dynamics
        if "loneliness_exclusion" in themes:
            return (
                "Let's look at what's underneath this feeling of isolation. There is a huge difference between being physically alone and feeling lonely.\n\n"
                "Often, feeling lonely in a group happens when you realize you are constantly adapting to their humor and their topics, but nobody is making space for the real, unguarded version of you. You can be surrounded by 20 people and still feel invisible if you feel like you're playing a role just to be there.\n\n"
                "When you feel disconnected around people, does it feel like they're actively ignoring you, or like you just don't feel comfortable letting your guard down around them?"
            )

        # 5. Vitiligo / Physical Conditions
        if analysis["has_vitiligo"] or analysis["has_skin_condition"]:
            return (
                "Let's unpack why this takes such a heavy emotional toll. When you're dealing with visible changes in your appearance, you are navigating the psychological weight of hypervisibility.\n\n"
                "You have to manage your own feelings about your body while simultaneously anticipating how everyone around you might react. When people stare or give tone-deaf advice like 'looks don't matter,' it feels invalidating because they don't understand the constant micro-stress of having to explain yourself or feel scrutinized.\n\n"
                "Does the hardest part feel like managing your own worries about changes, or the exhaustion of having to deal with other people's reactions?"
            )

        # 6. Self-Worth & Critical Inner Voice
        if "self_worth" in themes:
            return (
                "Let's explore why that harsh inner voice is being so aggressive right now. When we feel like a 'failure' or a 'burden,' it's rarely because we actually did something unforgivable.\n\n"
                "Usually, it happens when we've been carrying chronic stress for weeks without any emotional recharge, and our brain starts blaming ourselves for feeling exhausted.\n\n"
                "If that critical voice sounded like someone's expectations, whose voice does it remind you of—your own, your family's, or people at school?"
            )

        # 7. General Reflection
        return (
            "Let's explore what is happening under the surface. Often when we feel deeply stuck or overwhelmed, our emotional reactions are signals that an important personal boundary or need is being pushed—like feeling safe, feeling heard, or needing rest.\n\n"
            "If you look at what has been draining you the most, what feels like the root cause behind this feeling?"
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
