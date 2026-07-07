"""
Plain-language narrative generation for each dashboard view.

If an Anthropic API key is available (via st.secrets["ANTHROPIC_API_KEY"] or
the ANTHROPIC_API_KEY environment variable), narratives are generated live by
Claude from the filtered summary statistics. If no key is configured, the
module falls back to a rule-based narrative built from the same statistics,
so every page remains fully functional without any external dependency.
"""

import os
import streamlit as st

MODEL_NAME = "claude-sonnet-5"


def _get_api_key():
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def _call_claude(system_prompt: str, user_prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=_get_api_key())
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def generate_narrative(audience: str, stats: dict, fallback_text: str, use_ai: bool = False) -> str:
    """
    audience: one of "dean", "faculty_manager", "lecturer", "student"
    stats: dictionary of summary statistics to ground the narrative
    fallback_text: rule-based narrative to show if AI is unavailable or disabled
    use_ai: whether the user has opted in to live AI generation
    """
    if not use_ai or not _get_api_key():
        return fallback_text

    audience_briefs = {
        "dean": (
            "You are briefing a Dean and Deputy Deans on faculty-wide student "
            "progression. Write three short paragraphs: overall picture, the "
            "main equity or programme concern, and one clear strategic "
            "recommendation. Use formal British English, no bullet points, "
            "no filler phrases."
        ),
        "faculty_manager": (
            "You are briefing a Faculty Manager responsible for operational "
            "oversight of modules and assessments. Write two short paragraphs "
            "covering which modules or monitoring points need attention and "
            "what operational action to take this week. Formal British "
            "English, no filler phrases."
        ),
        "lecturer": (
            "You are briefing a module lecturer. Write two short paragraphs "
            "naming the pattern of non-submission or failure in this module "
            "and which students need contact first. Formal British English, "
            "practical and direct."
        ),
        "student": (
            "You are writing directly to a student about their own progress. "
            "Write two short paragraphs in a warm, encouraging, non-alarming "
            "tone that explains where they stand compared with their class "
            "and programme, and one concrete next step. Do not use clinical "
            "or diagnostic language."
        ),
    }

    system_prompt = audience_briefs.get(audience, audience_briefs["faculty_manager"])
    user_prompt = "Here are the current filtered summary statistics:\n\n" + "\n".join(
        f"{k}: {v}" for k, v in stats.items()
    )

    try:
        return _call_claude(system_prompt, user_prompt)
    except Exception as exc:
        return fallback_text + f"\n\n_(AI narrative unavailable: {exc})_"


def ai_toggle(key: str) -> bool:
    """Render the AI narrative opt-in toggle and return its state."""
    has_key = bool(_get_api_key())
    label = "Generate narrative with Claude" if has_key else "Generate narrative with Claude (no API key configured)"
    return st.toggle(label, value=False, disabled=not has_key, key=key)
