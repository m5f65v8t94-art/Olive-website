from typing import List, Dict, Optional

class ContinuityService:
    """
    Maintains non-identifying rolling context summaries for conversation continuity
    so returning users don't have to re-explain their circumstances.
    """

    @staticmethod
    def update_context_summary(existing_summary: Optional[str], recent_messages: List[Dict[str, str]]) -> str:
        """
        Creates/updates a concise topic summary from user statements.
        """
        user_statements = [m["content"] for m in recent_messages if m.get("role") == "user"]
        if not user_statements:
            return existing_summary or ""

        latest = user_statements[-1]
        summary_snippets = []
        if existing_summary:
            summary_snippets.append(existing_summary)

        # Extract themes accurately without misclassifying school social dynamics as academic stress
        lower_latest = latest.lower()
        if any(w in lower_latest for w in ["friend", "relationship", "left out", "alone", "lonely", "talking together", "part of it", "third wheel"]):
            summary_snippets.append("Discussing interpersonal relationships or feelings of isolation.")
        elif any(w in lower_latest for w in ["assignment", "homework", "exam", "test", "grade", "procrastinat", "studying"]):
            summary_snippets.append("Navigating academic workload and deadlines.")
        elif any(w in lower_latest for w in ["family", "parent", "dad", "mom", "home"]):
            summary_snippets.append("Navigating family and home dynamics.")
        elif any(w in lower_latest for w in ["overwhelm", "tired", "exhausted", "burnout", "rough day"]):
            summary_snippets.append("Experiencing mental exhaustion and needing unhurried space.")
        elif any(w in lower_latest for w in ["reply", "message", "text back", "wondering if i did something wrong"]):
            summary_snippets.append("Exploring uncertainty and overthinking around communication.")
        else:
            summary_snippets.append(f"Discussing: {latest[:60]}...")

        # Keep summary concise and deduplicated
        combined = " | ".join(dict.fromkeys(summary_snippets))
        return combined[-400:]

continuity_service = ContinuityService()
