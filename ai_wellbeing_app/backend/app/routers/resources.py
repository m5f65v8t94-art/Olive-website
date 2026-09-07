from fastapi import APIRouter
from typing import List, Dict, Any
from app.utils.constants import CRISIS_RESOURCES, NON_CLINICAL_DISCLAIMER, GET_HELP_PRIVATELY_GUIDANCE, STUDY_NOTES_SUBJECTS
from app.schemas.safety import CrisisResource, SafetyAssessment
from app.services.safety_service import safety_service

router = APIRouter(prefix="/api/resources", tags=["Wellbeing & Crisis Resources"])

WELLBEING_COPING_TOOLS = [
    {
        "id": "box_breathing",
        "category": "Breathing",
        "title": "Box Breathing (4-4-4-4)",
        "description": "Slow, balanced breathing technique used to down-regulate the nervous system and calm anxiety.",
        "duration": "2 mins",
        "steps": [
            "Inhale slowly through the nose for 4 seconds.",
            "Hold your lungs full gently for 4 seconds.",
            "Exhale smoothly through the mouth for 4 seconds.",
            "Hold your lungs empty gently for 4 seconds.",
            "Repeat for 4 to 6 cycles."
        ]
    },
    {
        "id": "relaxing_breath_478",
        "category": "Breathing",
        "title": "4-7-8 Relaxing Breath",
        "description": "Natural tranquilizer for the nervous system, helpful for sleep and acute stress.",
        "duration": "3 mins",
        "steps": [
            "Inhale quietly through the nose for 4 seconds.",
            "Hold your breath gently for 7 seconds.",
            "Exhale completely through your mouth making a soft whoosh sound for 8 seconds.",
            "Repeat this cycle 4 times."
        ]
    },
    {
        "id": "coherent_breathing",
        "category": "Breathing",
        "title": "5-5 Coherent Breathing",
        "description": "Equalized 5-second rhythmic breathing to optimize heart-rate variability and mental focus.",
        "duration": "3 mins",
        "steps": [
            "Inhale gently through your nose for 5 seconds.",
            "Exhale smoothly without pausing for 5 seconds.",
            "Maintain an effortless, wave-like rhythm for 15 breaths."
        ]
    },
    {
        "id": "sensory_grounding",
        "category": "Grounding",
        "title": "5-4-3-2-1 Sensory Grounding",
        "description": "Anchors attention back into your physical surroundings when spiraling or dissociating.",
        "duration": "3 mins",
        "steps": [
            "Name 5 things you can SEE around the room.",
            "Name 4 things you can physically TOUCH or feel (e.g. fabric, table).",
            "Name 3 things you can HEAR right now.",
            "Name 2 things you can SMELL or enjoy the scent of.",
            "Name 1 thing you like, appreciate, or find comforting."
        ]
    },
    {
        "id": "body_scan",
        "category": "Mindfulness",
        "title": "Progressive Body Scan & Release",
        "description": "Releases physical muscle tension stored in your shoulders, jaw, and stomach.",
        "duration": "4 mins",
        "steps": [
            "Soften your forehead and unclench your teeth and jaw.",
            "Drop your shoulders down away from your ears.",
            "Loosen your hands, fingers, and belly.",
            "Feel the steady support of the chair or floor underneath you."
        ]
    },
    {
        "id": "thought_defusion",
        "category": "Short Reflection",
        "title": "Leaves on a Stream (Thought Defusion)",
        "description": "Visualize your anxious or sticky thoughts drifting by without having to fight them.",
        "duration": "3 mins",
        "steps": [
            "Picture a gentle stream flowing under a canopy of trees.",
            "Whenever a worrying thought arises, place it onto an autumn leaf.",
            "Watch the leaf drift along the water, around the bend, and out of sight.",
            "You don't need to push it or stop it—just let it float away naturally."
        ]
    },
    {
        "id": "tactile_reset",
        "category": "Quick Reset",
        "title": "Bilateral Alternate Fingertip Tapping",
        "description": "Gentle sensory rhythm to ground your attention and interrupt frantic overthinking.",
        "duration": "2 mins",
        "steps": [
            "Rest your hands gently on your lap or desk.",
            "Slowly tap your left index finger, then your right index finger.",
            "Continue alternating at a calm, steady rhythm like a ticking clock.",
            "Take 5 slow breaths while focusing solely on the sensation of your fingertips."
        ]
    }
]

@router.get("", response_model=Dict[str, Any])
async def get_all_resources():
    """Returns crisis hotlines, private help directory, coping tools, and disclaimers."""
    return {
        "disclaimer": NON_CLINICAL_DISCLAIMER,
        "get_help_privately": GET_HELP_PRIVATELY_GUIDANCE,
        "crisis_resources": [CrisisResource(**r) for r in CRISIS_RESOURCES],
        "coping_tools": WELLBEING_COPING_TOOLS,
        "study_notes": STUDY_NOTES_SUBJECTS
    }

@router.get("/study-notes", response_model=List[Dict[str, Any]])
async def get_study_notes():
    """Returns realistic study notes subjects for Quick Privacy Hide."""
    return STUDY_NOTES_SUBJECTS

@router.get("/coping-tools", response_model=List[Dict[str, Any]])
async def get_coping_tools():
    """Returns optional categorized calming and grounding exercises."""
    return WELLBEING_COPING_TOOLS

@router.get("/private-help", response_model=Dict[str, Any])
async def get_private_help_directory():
    """Returns the dedicated Get Help Privately directory with Tele-MANAS, Child Helpline, Meri Trustline, Cyber Crime, and 112."""
    return GET_HELP_PRIVATELY_GUIDANCE

@router.post("/safety-check", response_model=SafetyAssessment)
async def check_message_safety(payload: Dict[str, str]):
    """Evaluate text for crisis risk or diagnostic query."""
    text = payload.get("text", "")
    return safety_service.assess_message(text)

