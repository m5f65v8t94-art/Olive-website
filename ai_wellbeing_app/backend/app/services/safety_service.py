import re
from typing import Tuple, Optional, List, Dict
from app.utils.constants import (
    NON_CLINICAL_DISCLAIMER,
    CRISIS_RESOURCES,
    SAFETY_CRISIS_KEYWORDS,
    IMMEDIATE_DANGER_KEYWORDS,
    SUICIDE_SELF_HARM_KEYWORDS,
    SAFE_RIGHT_NOW_KEYWORDS,
    NOT_TELLING_KEYWORDS,
    DIAGNOSTIC_QUERIES
)
from app.schemas.safety import SafetyAssessment, CrisisResource

class SafetyService:
    @staticmethod
    def assess_message(message: str, history: Optional[List[Dict[str, str]]] = None) -> SafetyAssessment:
        """
        Analyzes user input with state-aware precision:
        1. Immediate Escalation: inability to keep safe tonight / imminent danger
        2. De-escalation: safe right now / reluctant to tell someone after prior crisis disclosure
        3. Initial Crisis: suicide thoughts / self-harm disclosure
        4. Diagnostic inquiry attempts
        """
        clean_text = message.lower().strip().replace("’", "'").replace("‘", "'")
        
        # Check history for past crisis indicators
        past_user_texts = []
        had_prior_crisis = False
        if history:
            for m in history:
                if m.get("role") == "user":
                    p_txt = m.get("content", "").lower().replace("’", "'").replace("‘", "'")
                    past_user_texts.append(p_txt)
                    if any(kw in p_txt for kw in SAFETY_CRISIS_KEYWORDS):
                        had_prior_crisis = True

        # =====================================================================
        # 1. Immediate Danger / Escalation
        # =====================================================================
        is_immediate_danger = False
        detected_trigger = None

        for kw in IMMEDIATE_DANGER_KEYWORDS:
            if kw in clean_text:
                is_immediate_danger = True
                detected_trigger = kw
                break

        if not is_immediate_danger:
            # Check combinations like "not sure" / "can't" + "keep myself safe" / "safe tonight"
            has_inability_marker = any(m in clean_text for m in [
                "not sure", "cant", "can't", "cannot", "unable", "don't know if", "dont know if", "don't think i can", "dont think i can"
            ])
            has_safety_marker = any(s in clean_text for s in [
                "keep myself safe", "stay safe", "promise to be safe", "safe tonight", "make it through", "trust myself"
            ])
            if has_inability_marker and has_safety_marker:
                is_immediate_danger = True
                detected_trigger = "inability to keep safe"

        if is_immediate_danger:
            resources = [CrisisResource(**r) for r in CRISIS_RESOURCES]
            support_msg = (
                "I hear how urgent and overwhelming things feel right now, and your safety is the absolute most important thing. Please do not stay alone.\n\n"
                "Please go to a parent, guardian, family member, or another trusted adult right now and let them know you need help staying safe.\n\n"
                "You can also reach out immediately for emergency human care:\n"
                "• Tele-MANAS: 14416 / 1800-89-14416 (24/7 toll-free mental health support)\n"
                "• Child Helpline: 1098 (24/7 for youth)\n"
                "• Meri Trustline: 6363 17 6363 (Call & WhatsApp)\n"
                "• Cyber Crime Helpline: 1930\n"
                "• Emergency: 112 (immediate assistance)\n\n"
                "Please connect with someone physically with you or call 112 right away. You do not have to handle this alone."
            )
            return SafetyAssessment(
                is_crisis=True,
                is_diagnostic_attempt=False,
                risk_level="imminent",
                trigger_detected=detected_trigger,
                safety_state="immediate_escalation",
                recommended_resources=resources,
                support_message=support_msg,
                non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
            )

        # =====================================================================
        # 2. De-escalation: "Safe right now" / "Support person present" / "Don't want to tell anyone"
        # =====================================================================
        # Check if user says a trusted person is with them now (Mom, Dad, Parents, etc.)
        has_support_person = any(kw in clean_text for kw in [
            "got my mom to stay with me", "got my dad to stay with me", "got my mom", "got my dad",
            "my mom is here with me", "my mom is with me", "my mom is here", "mom is here with me",
            "mom is with me now", "mom is here now", "my dad is here with me", "my dad is with me",
            "dad is here with me", "dad is with me now", "my parents are here", "parents are here with me",
            "with my mom now", "with my dad now", "with my parents now", "with my mom", "with my dad",
            "sitting with my mom", "sitting with my dad", "staying with my mom", "staying with my dad",
            "talked to my mom", "talked to my dad", "told my mom", "told my dad", "told my parents",
            "my counselor is with me", "my teacher is with me", "with my counselor", "with a trusted adult",
            "with someone right now", "my friend is with me", "not alone anymore", "someone is with me"
        ]) or bool(re.search(r'\b(?:got|have|having|is with|is here|staying with|sitting with)\b.*?\b(?:mom|dad|mother|father|parents|parent|counselor|teacher|friend|adult|someone)\b', clean_text)) or bool(re.search(r'\b(?:mom|dad|mother|father|parents|parent|counselor|teacher|friend|adult|someone)\b.*?\b(?:is here|is with me|is in the room|staying with me|stay with me|here with me)\b', clean_text))

        is_safe_right_now = any(kw in clean_text for kw in SAFE_RIGHT_NOW_KEYWORDS)
        is_not_telling = any(kw in clean_text for kw in NOT_TELLING_KEYWORDS)

        if has_support_person:
            # Let local_engine compose the contextual response with the user's specific topic & support person
            return SafetyAssessment(
                is_crisis=False,
                is_diagnostic_attempt=False,
                risk_level="low",
                trigger_detected="support_person_present",
                safety_state="support_person_present",
                recommended_resources=[],
                support_message=None,
                non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
            )

        if (had_prior_crisis or is_safe_right_now) and (is_safe_right_now or is_not_telling):
            support_msg = (
                "I'm really glad to hear that you are safe right now. Thank you for letting me know.\n\n"
                "I completely understand that opening up to a parent, teacher, or counselor can feel really hard or scary right now. You don't have to rush into anything before you feel ready, but having a trusted person in your life who knows what you're dealing with can make a huge difference.\n\n"
                "I'm right here with you. What has been on your mind lately?"
            )
            return SafetyAssessment(
                is_crisis=False,
                is_diagnostic_attempt=False,
                risk_level="medium",
                trigger_detected="safe_right_now",
                safety_state="safe_but_reluctant",
                recommended_resources=[CrisisResource(**r) for r in CRISIS_RESOURCES],
                support_message=support_msg,
                non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
            )

        # =====================================================================
        # 3. Initial / General Suicide or Self-Harm Disclosure
        # =====================================================================
        is_suicide_or_selfharm = False
        for kw in SUICIDE_SELF_HARM_KEYWORDS:
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, clean_text) or kw in clean_text:
                is_suicide_or_selfharm = True
                detected_trigger = kw
                break

        if is_suicide_or_selfharm:
            resources = [CrisisResource(**r) for r in CRISIS_RESOURCES]
            has_online_issue = any(w in clean_text for w in [
                "online", "cyber", "leaked", "blackmail", "photos", "chat", "insta", "instagram", "snap", "snapchat", "doxxed", "bullied online"
            ])
            
            support_msg = (
                "I hear how serious and painful things feel right now, and I want you to know that your life matters and you don't have to go through this alone.\n\n"
                "Because I care about your safety and I'm an AI—not a doctor, therapist, or replacement for real human support—I strongly encourage you to reach out to a trusted adult, such as a parent, guardian, teacher, school counselor, or another adult you feel safe with.\n\n"
                "Please connect with trained support services who can help you through this:\n"
                "• Tele-MANAS: 14416 / 1800-89-14416 (24/7, toll-free)\n"
                "• Child Helpline: 1098 (24/7 for youth)\n"
                "• Meri Trustline: 6363 17 6363 (Call & WhatsApp)\n"
                "• Cyber Crime Helpline: 1930\n"
                "• Emergency: 112 (if in immediate danger)\n\n"
                "Are you in a safe place right now?"
            )
            return SafetyAssessment(
                is_crisis=True,
                is_diagnostic_attempt=False,
                risk_level="high",
                trigger_detected=detected_trigger,
                safety_state="initial_disclosure",
                recommended_resources=resources,
                support_message=support_msg,
                non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
            )

        # =====================================================================
        # 4. Diagnostic Queries
        # =====================================================================
        is_diagnostic = False
        for diag_kw in DIAGNOSTIC_QUERIES:
            if diag_kw in clean_text:
                is_diagnostic = True
                break
        if "diagnose" in clean_text or "what condition do i have" in clean_text or "am i mentally ill" in clean_text:
            is_diagnostic = True

        if is_diagnostic:
            support_msg = (
                "I want to be transparent: as an AI, I am not a doctor, therapist, or clinical professional, "
                "so I cannot diagnose conditions or determine what might be going on medically.\n\n"
                "However, I am always here to listen and help you explore how you've been feeling day-to-day. "
                "If you would like, we can also work on a message together so you can discuss this with a doctor, counselor, or parent."
            )
            return SafetyAssessment(
                is_crisis=False,
                is_diagnostic_attempt=True,
                risk_level="low",
                trigger_detected="diagnostic_query",
                safety_state="diagnostic",
                recommended_resources=[],
                support_message=support_msg,
                non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
            )

        # =====================================================================
        # 5. Normal / Post-Crisis Conversation
        # =====================================================================
        return SafetyAssessment(
            is_crisis=False,
            is_diagnostic_attempt=False,
            risk_level="low",
            trigger_detected=None,
            safety_state="post_crisis_context" if had_prior_crisis else "normal",
            recommended_resources=[],
            support_message=None,
            non_clinical_disclaimer=NON_CLINICAL_DISCLAIMER
        )

safety_service = SafetyService()
