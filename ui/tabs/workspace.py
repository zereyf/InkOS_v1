from __future__ import annotations

import re
from datetime import datetime, timezone

import streamlit as st

from engine.refiner import run_refinement_and_audit
from forge.intelligence import resolve_target_model
from forge.prompt_assembler import assemble_master_payload
from security.sanitizer import sanitize_input
from state import K

UTC = timezone.utc
AUDIENCE_OPTIONS = ["Students", "Professionals", "General"]

QUICK_EXAMPLES = [
    "Write an article about AI in education...",
    "اكتب مقالاً عن الذكاء الاصطناعي في التعليم...",
    "Write a marketing copy for a new productivity app.",
    "اكتب رسالة بريد إلكتروني احترافية لمتابعة عميل.",
]


def _tone_instruction(value: int) -> str:
    if value <= 33:
        return "Use a formal, professional tone"
    if value <= 66:
        return "Use a neutral, balanced tone"
    return "Use a casual, conversational tone"


def _length_instruction(value: int) -> str:
    if value <= 33:
        return "Keep response under 100 words, concise"
    if value <= 66:
        return "Aim for 100-250 words, medium length"
    return "Provide detailed response, 250+ words"


def _creativity_instruction(value: int) -> str:
    if value <= 33:
        return "Be conservative and logical"
    if value <= 66:
        return "Balance creativity with clarity"
    return "Be highly creative and imaginative"


def _audience_instruction(audience: str) -> str:
    mapping = {
        "Students": "Use simple, educational language",
        "Professionals": "Use technical, precise language",
        "General": "Use accessible, clear language",
    }
    return mapping.get(audience, mapping["General"])


def _is_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text or ""))


def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    refined_match = re.search(r"REFINED_PROMPT\s*:\s*(.+)", t, flags=re.I | re.S)
    if refined_match:
        t = refined_match.group(1)

    t = re.sub(r"\*\*\s*PART\s*\d+\s*:[^\n]*\**", "", t, flags=re.I)
    t = re.sub(r"(?:System\s*Prompt|PROMPT|OUTPUT|thinking)\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"A\.I\.Z\.E\.N\.[\s\S]*?(?=\n\n|$)", "", t, flags=re.I)
    for tag in ("quality-bar", "constraints", "role", "task", "edge-cases"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = re.sub(r"\{\s*\"score\"\s*:[\s\S]*?\}\s*$", "", t, flags=re.I)
    t = re.sub(r"REFINED_PROMPT\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _process_prompt(intent_val: str, cfg: dict, tone: int, length: int, creativity: int, audience: str) -> None:
    cleaned, violations = sanitize_input(intent_val)
    if violations:
        st.error("Blocked by security policy. Please remove malicious instruction patterns.")
        return

    control_block = "\n".join(
        [
            "[REFINEMENT CONTROLS]",
            _tone_instruction(tone),
            _length_instruction(length),
            _creativity_instruction(creativity),
            _audience_instruction(audience),
            "[/REFINEMENT CONTROLS]",
        ]
    )

    payload = assemble_master_payload(f"{cleaned}\n\n{control_block}", dict(cfg), {
        K.INK_DNA: str(st.session_state.get(K.INK_DNA) or ""),
        K.INTEL_DNA: str(st.session_state.get(K.INTEL_DNA) or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    })

    with st.spinner("Refining prompt..."):
        result, _audit, _ = run_refinement_and_audit(
            payload,
            resolve_target_model("auto", cleaned)[0],
            cfg.get("framework", "RACE"),
            cfg.get("source_lang", "English"),
            cfg.get("aesthetic_choice", "Default"),
            hikmah_style=str(cfg.get("hikmah_style") or "None"),
            skip_security=False,
        )

    clean = extract_clean_output(result)
    if _is_arabic(cleaned):
        clean = f"[Arabic]\n{clean}\n\n[English]\n{clean}"
    else:
        clean = f"[English]\n{clean}\n\n[Arabic]\n{clean}"

    st.session_state[K.LAST_RESULT] = clean
    st.session_state[K.LAST_INPUT] = cleaned
    history = st.session_state.get(K.HISTORY, [])
    history.append({"title": cleaned[:40], "input": cleaned, "output": clean, "time": datetime.now(UTC).isoformat()})
    st.session_state[K.HISTORY] = history[-50:]


def render_workspace(cfg: dict) -> None:
    st.subheader("InkOS Workspace | مساحة العمل")

    if "workspace_text" not in st.session_state:
        st.session_state["workspace_text"] = st.session_state.get(K.LAST_INPUT, "")

    top = st.columns([1, 1, 1, 1])
    for i, example in enumerate(QUICK_EXAMPLES):
        if top[i % 4].button(example, key=f"example_{i}"):
            st.session_state["workspace_text"] = example

    source = st.text_area(
        "1. Source Prompt / الموجه الأصلي",
        value=st.session_state["workspace_text"],
        height=220,
        placeholder="Write an article about AI in education...\nاكتب مقالاً عن الذكاء الاصطناعي...",
    )
    st.session_state["workspace_text"] = source
    st.caption(f"{len(source)} / 4000")

    left, center, right = st.columns(3)
    with left:
        tone = st.slider("Tone / النبرة", 0, 100, 50)
    with center:
        length = st.slider("Length / الطول", 0, 100, 50)
    with right:
        creativity = st.slider("Creativity / الإبداع", 0, 100, 50)

    audience = st.selectbox("Audience / الجمهور", AUDIENCE_OPTIONS)

    actions = st.columns(4)
    if actions[0].button("Clear / مسح", use_container_width=True):
        st.session_state["workspace_text"] = ""
        st.rerun()
    if actions[1].button("Reset to defaults / إعادة تعيين", use_container_width=True):
        st.rerun()

    if actions[2].button("⚡ Refine Prompt / تحسين الموجه", type="primary", use_container_width=True):
        if source.strip():
            _process_prompt(source, cfg, tone, length, creativity, audience)
            st.rerun()

    output = st.session_state.get(K.LAST_RESULT, "")
    if output:
        st.text_area("3. Refined Prompt ✨ / الموجه المحسّن", value=output, height=260)
        words = len(output.split())
        chars = len(output)
        minutes = max(1, round(words / 200))
        st.caption(f"📄 {words} words | Aa {chars} chars | ⏱ {minutes} min | ✨ Refined with InkOS")
