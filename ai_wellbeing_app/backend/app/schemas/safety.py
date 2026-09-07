from typing import Optional, List
from pydantic import BaseModel

class CrisisResource(BaseModel):
    name: str
    description: str
    phone: Optional[str] = None
    text: Optional[str] = None
    website: Optional[str] = None
    availability: str

class SafetyAssessment(BaseModel):
    is_crisis: bool = False
    is_diagnostic_attempt: bool = False
    risk_level: str = "low"  # low, medium, high, imminent
    trigger_detected: Optional[str] = None
    safety_state: Optional[str] = "normal"  # normal, initial_disclosure, safe_but_reluctant, immediate_escalation, diagnostic
    recommended_resources: List[CrisisResource] = []
    support_message: Optional[str] = None
    non_clinical_disclaimer: str
