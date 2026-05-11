"""
ui/splash.py — Terminal Latch Gateway
=======================================
v3.0: Premium identity-first login experience.
      - Auto-detects new vs returning user from ID
      - Single screen, zero cognitive load
      - Terminal OS aesthetic with Arabic soul
"""
from __future__ import annotations
import time
import streamlit as st
from state import K
from vault.vault_engine import authenticate_terminal, check_id_availability
from vault.supabase_client import SUPABASE_MISSING


# ── Inline styles scoped to splash only ──
_SPLASH_CSS = """
<style>
/* Boot header */
.splash-boot {
  font: 11px 'JetBrains Mono', monospace;
  color: #3f3f46;
  letter-spacing: .15em;
  margin-bottom: 40px;
  line-height: 2;
}
.splash-boot .ok   { color: #22c55e; }
.splash-boot .warn { color: #f59e0b; }
.splash-boot .err  { color: #ef4444; }

/* Hero */
.splash-hero {
  text-align: center;
  margin-bottom: 40px;
}
.splash-ar {
  font: 700 48px 'Noto Naskh Arabic', serif;
  color: #f1f1f3;
  line-height: 1.2;
  display: block;
  margin-bottom: 4px;
}
.splash-divider {
  width: 48px;
  height: 2px;
  background: #6366f1;
  margin: 12px auto;
  border-radius: 999px;
}
.splash-sub {
  font: 11px 'JetBrains Mono', monospace;
  color: #71717a;
  letter-spacing: .2em;
}

/* Status pill */
.splash-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #16161f;
  border: 1px solid #ffffff0f;
  border-radius: 999px;
  padding: 4px 14px;
  font: 11px 'JetBrains Mono', monospace;
  color: #71717a;
  margin-bottom: 32px;
}
.splash-status .dot { color: #22c55e; font-size: 8px; }
.splash-status.offline .dot { color: #ef4444; }

/* Step indicator */
.splash-step {
  font: 11px 'JetBrains Mono', monospace;
  color: #6366f1;
  letter-spacing: .1em;
  margin-bottom: 8px;
  text-transform: uppercase;
}

/* ID state badges */
.id-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 3px 12px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 6px;
}
.id-badge.new      { background: #6366f118; color: #6366f1; border: 1px solid #6366f133; }
.id-badge.existing { background: #22c55e18; color: #22c55e; border: 1px solid #22c55e33; }
.id-badge.invalid  { background: #ef444418; color: #ef4444; border: 1px solid #ef444433; }

/* Description box */
.splash-desc {
  background: #111118;
  border: 1px solid #ffffff0f;
  border-left: 2px solid #6366f1;
  border-radius: 0 10px 10px 0;
  padding: 14px 16px;
  margin-bottom: 24px;
}
.splash-desc p {
  font-size: 13px;
  color: #71717a;
  line-height: 1.7;
  margin: 0;
}
.splash-desc .ar {
  font-family: 'Noto Naskh Arabic', serif;
  font-size: 13px;
  color: #3f3f46;
  display: block;
  text-align: right;
  margin-top: 8px;
}

/* Offline banner */
.offline-banner {
  background: #f59e0b18;
  border: 1px solid #f59e0b33;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 13px;
  color: #f59e0b;
  margin-bottom: 20px;
  font-family: 'JetBrains Mono', monospace;
}
</style>
"""

# ── Boot sequence lines ──
_BOOT_LINES = [
    ('<span class="ok">[ OK ]</span>', "CIPHER ENGINE v12.0 loaded"),
    ('<span class="ok">[ OK ]</span>', "Security sanitizer armed"),
    ('<span class="ok">[ OK ]</span>', "Forge & persona layers ready"),
    ('<span class="warn">[ ?? ]</span>', "Awaiting terminal latch..."),
]


def _boot_sequence_html() -> str:
    lines = "".join(
        f"<div>{tag}&nbsp;&nbsp;{msg}</div>"
        for tag, msg in _BOOT_LINES
    )
    return f"<div class='splash-boot'>{lines}</div>"


def _hero_html() -> str:
    return """
    <div class='splash-hero'>
      <span class='splash-ar'>حبر وفكرة</span>
      <div class='splash-divider'></div>
      <div class='splash-sub'>INKOS  //  TERMINAL LATCH  //  v2026</div>
    </div>
    """


def _status_pill() -> str:
    if SUPABASE_MISSING:
        return "<div class='splash-status offline'><span class='dot'>●</span> VAULT OFFLINE — Guest mode only</div>"
    return "<div class='splash-status'><span class='dot'>●</span> NEURAL UPLINK ACTIVE</div>"


def render_splash_screen() -> None:
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)
    st.markdown(_SPLASH_CSS + _boot_sequence_html() + _hero_html(), unsafe_allow_html=True)
    st.markdown(_status_pill(), unsafe_allow_html=True)

    # ── Offline / guest mode ──
    if SUPABASE_MISSING:
        st.markdown("""
        <div class='offline-banner'>
          ⚠ Vault connection unavailable.<br>
          You can still use InkOS in guest mode with limited features.
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button(
                "⚡  Enter as Guest",
                use_container_width=True,
                type="primary",
                key="guest_enter",
            ):
                st.session_state[K.USER_HASH] = f"GUEST_{int(time.time())}"
                st.rerun()
        return

    # ── Step 1: ID entry ──
    latch_phase = st.session_state.get("latch_phase", "id")

    if latch_phase == "id":
        _render_id_phase()
    elif latch_phase == "pin":
        _render_pin_phase()
    elif latch_phase == "success":
        _render_success_phase()


# ────────────────────────────────────────────────────────────
# PHASE 1 — ID ENTRY
# ────────────────────────────────────────────────────────────

def _render_id_phase() -> None:
    st.markdown("""
    <div class='splash-desc'>
      <p>
        InkOS is a specialized Prompt Engineering OS — it refines raw ideas
        into production-grade prompts using an 8B Reflex Engine, CIPHER identity
        layers, and a Maqasid ethical framework.
      </p>
      <span class='ar'>أدخل معرّفك للبدء</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='splash-step'>STEP 1 OF 2  —  IDENTITY</div>",
                unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 4, 1])
    with col_b:
        uid = st.text_input(
            "Your ID",
            placeholder="Enter your identifier  (e.g. Ameer)",
            label_visibility="collapsed",
            key="latch_uid_input",
            max_chars=64,
        )

        # Live ID check
        if uid and uid.strip():
            uid_clean = uid.strip()
            available, msg = check_id_availability(uid_clean)

            if len(uid_clean) < 3:
                st.markdown(
                    "<div class='id-badge invalid'>⚠ Too short — min 3 characters</div>",
                    unsafe_allow_html=True,
                )
            elif available:
                st.markdown(
                    f"<div class='id-badge new'>✦ New identity — '{uid_clean}' will be created</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='id-badge existing'>✓ Welcome back, {uid_clean}</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        proceed = st.button(
            "Continue  →",
            use_container_width=True,
            type="primary",
            key="latch_proceed",
        )

        if proceed:
            uid_clean = (uid or "").strip()
            if len(uid_clean) < 3:
                st.error("ID must be at least 3 characters.")
                return

            # Check validity
            available, _ = check_id_availability(uid_clean)
            st.session_state["latch_uid"]    = uid_clean
            st.session_state["latch_is_new"] = available
            st.session_state["latch_phase"]  = "pin"
            st.rerun()

        st.markdown("""
        <div style='text-align:center;margin-top:16px;
                    font-size:11px;color:#3f3f46;font-family:monospace;'>
          Your ID is your identity — choose something memorable.
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────
# PHASE 2 — PIN ENTRY
# ────────────────────────────────────────────────────────────

def _render_pin_phase() -> None:
    uid    = st.session_state.get("latch_uid", "")
    is_new = st.session_state.get("latch_is_new", True)

    action_label = "REGISTRATION" if is_new else "AUTHENTICATION"
    action_verb  = "Create a PIN" if is_new else "Enter your PIN"
    action_hint  = "Choose a secure PIN (min 4 chars)" if is_new else f"Welcome back, {uid}"

    st.markdown(f"""
    <div style='background:#16161f;border:1px solid #ffffff0f;
                border-radius:12px;padding:16px 20px;margin-bottom:20px;'>
      <div style='font-size:11px;font-family:monospace;color:#6366f1;
                  letter-spacing:.1em;margin-bottom:8px;'>{action_label}</div>
      <div style='font-size:22px;font-weight:700;color:#f1f1f3;
                  margin-bottom:2px;'>{uid}</div>
      <div style='font-size:12px;color:#71717a;'>{action_hint}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='splash-step'>STEP 2 OF 2  —  {action_verb.upper()}</div>",
                unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1, 4, 1])
    with col_b:
        pin = st.text_input(
            "PIN",
            placeholder="Enter PIN...",
            type="password",
            label_visibility="collapsed",
            key="latch_pin_input",
            max_chars=128,
        )

        if is_new:
            pin_confirm = st.text_input(
                "Confirm PIN",
                placeholder="Confirm PIN...",
                type="password",
                label_visibility="collapsed",
                key="latch_pin_confirm",
                max_chars=128,
            )
        else:
            pin_confirm = pin

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        col_back, col_go = st.columns([1, 2])
        with col_back:
            if st.button("← Back", key="latch_back", use_container_width=True):
                st.session_state["latch_phase"] = "id"
                st.rerun()

        with col_go:
            btn_label = "⚡ Create Identity" if is_new else "⚡ Initiate Latch"
            submit = st.button(
                btn_label,
                use_container_width=True,
                type="primary",
                key="latch_submit",
            )

        if submit:
            pin_val = (pin or "").strip()

            if len(pin_val) < 4:
                st.error("PIN must be at least 4 characters.")
                return

            if is_new and pin_val != (pin_confirm or "").strip():
                st.error("PINs do not match.")
                return

            with st.spinner("Authenticating..."):
                success, err = authenticate_terminal(uid, pin_val, is_new)

            if success:
                st.session_state[K.USER_HASH]   = uid
                st.session_state["latch_phase"] = "success"
                st.rerun()
            else:
                st.error(f"⚠ {err or 'Authentication failed.'}")


# ────────────────────────────────────────────────────────────
# PHASE 3 — SUCCESS
# ────────────────────────────────────────────────────────────

def _render_success_phase() -> None:
    uid = st.session_state.get("latch_uid", "")

    st.markdown(f"""
    <div style='text-align:center;padding:40px 24px;'>
      <div style='font-size:48px;margin-bottom:16px;'>⚡</div>
      <div style='font-size:22px;font-weight:700;color:#f1f1f3;
                  margin-bottom:8px;'>Identity Latched</div>
      <div style='font-size:14px;color:#71717a;margin-bottom:4px;'>
        Welcome, {uid}
      </div>
      <div style='font-size:13px;color:#3f3f46;
                  font-family:Noto Naskh Arabic,serif;'>
        أهلاً بك في النظام
      </div>
      <div style='margin-top:24px;'>
        <div style='display:inline-block;background:#22c55e18;
                    border:1px solid #22c55e33;border-radius:999px;
                    padding:4px 16px;font-size:12px;color:#22c55e;
                    font-family:monospace;'>
          ● NEURAL UPLINK SECURED
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Auto-advance after brief pause
    time.sleep(1.2)
    # Clean up latch state
    for key in ("latch_phase", "latch_uid", "latch_is_new"):
        st.session_state.pop(key, None)
    st.rerun()
