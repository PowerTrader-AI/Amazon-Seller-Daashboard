def generate_ai_summary(score: int, breakdown: str) -> str:
    # Placeholder for enterprise AI layer. Replace with internal LLM later.
    if score >= 85:
        verdict = "Strong Buy"
    elif score >= 70:
        verdict = "Buy"
    elif score >= 55:
        verdict = "Watch"
    else:
        verdict = "Avoid"

    return f"Verdict: {verdict}. Factors: {breakdown}."
