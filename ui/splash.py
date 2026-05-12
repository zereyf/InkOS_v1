"""
ui/splash.py — Terminal Latch Gateway
=======================================
v4.0: Tech-Noir Editorial Sync.
      - Synced with global typography and color palette.
      - Retained all live-ID and PIN logic.
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
/* Base overrides for splash */
.stApp { background-color: #0B0F19 !important; }
header[data-testid="stHeader"] { display: none !important; }

/* Boot header */
.splash-boot {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: #6B7280; letter-spacing: 0.15em; margin-bottom: 40px;
  line-height: 2; text-transform: uppercase;
}
.splash-boot .ok   { color: #D4AF37; } 
.splash-boot .warn { color: #F59E0B; }
.splash-boot .err  { color: #EF4444; }

/* Hero */
.splash-hero { text-align: center; margin-bottom: 30px; }
.splash-logo {
  font-family: 'Playfair Display', serif; font-size: 56px;
  color: #F8F9FA; letter-spacing: -1px; line-height: 1; margin-bottom: -5px;
}
.splash-ar {
  font-family: 'Amiri', serif; font-size: 28px;
  color: #D4AF37; display: block; margin-bottom: 12px;
}
.splash-divider {
  width: 40px; height: 1px; background: #D4AF37;
  margin: 16px auto; opacity: 0.5;
}
.splash-sub {
  font-family: 'JetBrains Mono', monospace; font-size: 10px;
  color: #9CA3AF; letter-spacing: 0.3em; text-transform: uppercase;
}

/* Status pill */
.splash-status {
  display: inline-flex; align-items: center; gap: 8px; justify-content: center;
  background: rgba(212, 175, 55, 0.05); border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 999px; padding: 6px 16px; width: 100%;
  font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 1px;
  color: #D4AF37; margin-bottom: 30px;
}
.splash-status .dot { font-size: 8px; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }

/* Step indicator */
.splash-step {
  font-family: 'Inter', sans-serif; font-size: 10px; color: #D4AF37;
  letter-spacing: 0.15em; margin-bottom: 12px; text-transform: uppercase;
}

/* ID state badges */
.id-badge {
  display: inline-flex; align-items: center; gap: 6px; border-radius: 999px;
  padding: 4px 14px; font-size: 11px; font-family: 'Inter', sans-serif; margin-top: 6px;
}
.id-badge.new      { background: rgba(212, 175, 55, 0.1); color: #D4AF37; border: 1px solid rgba(212, 175, 55, 0.3); }
.id-badge.existing { background: rgba(34, 197, 94, 0.1); color: #22C55E; border: 1px solid rgba(34, 197, 94, 0.3); }
.id-badge.invalid  { background: rgba(239, 68, 68, 0.1); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Description box */
.splash-desc {
  background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
  border-left: 2px solid #D4AF37; padding: 16px 20px; margin-bottom: 24px; border-radius: 0 8px 8px 0;
}
.splash-desc p { font-family: 'Inter', sans-serif; font-size: 13px; color: #9CA3AF; line-height: 1.6; margin: 0; }
.splash-desc .ar { font-family: 'Amiri', serif; font-size: 16px; color: #D4AF37; display: block; text-align: right; margin-top: 12px; }

/* Input overrides for Splash */
[data-testid="stTextInput"] input {
    background: #121826 !important; border: 1px solid rgba(255,255,255,0.1) !important;
    color: #F8F9FA !important; font-family: 'Inter', sans-serif !important; border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus { border-color: #D4AF37 !important; box-shadow: 0 0 0 1px #D4AF37 !important; }

/* Splash Button overrides */
button[kind="primary"] {
    background: #D4AF37 !important; color: #0B0F19 !important; font-family: 'Inter', sans-serif !important; 
    font-weight: 600 !important; border-radius: 8px !important; border: none !important; transition: all 0.2s ease !important;
}
button[kind="primary"]:hover { transform: scale(0.98) !important; background: #E8C84A !important; }
</style>
"""

_BOOT_LINES = [
    ('<span class="ok">[ OK ]</span>', "CIPHER ENGINE v2026 loaded"),
    ('<span class="ok">[ OK ]</span>', "Security sanitizer armed"),
    ('<span class="ok">[ OK ]</span>', "Forge & persona layers ready"),
    ('<span class="warn">[ ?? ]</span>', "Awaiting neural latch..."),
]

def _boot_sequence_html() -> str:
    lines = "".join(f"<div>{tag}&nbsp;&nbsp;{msg}</div>" for tag, msg in _BOOT_LINES)
    return f"<div class='splash-boot'>{lines}</div>"

def _hero_html() -> str:
    return """
    <div class='splash-hero'>
      <div class='splash-logo'>İnkOS</div>
      <span class='splash-ar'>حبر وفكرة</span>
      <div class='splash-divider'></div>
      <div class='splash-sub'>SECURE VAULT GATEWAY</div>
    </div>
    """

def _status_pill() -> str:
    if SUPABASE_MISSING:
        return "<div class='splash-status' style='color:#EF4444; border-color:rgba(239,68,68,0.2);'><span class='dot' style='color:#EF4444;'>●</span> VAULT OFFLINE — GUEST MODE</div>"
    return "<div class='splash-status'><span class='dot'>●</span> NEURAL UPLINK SECURED</div>"

def render_splash_screen() -> None:
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)
    
    # Push content down to center it vertically
    for _ in range(2): st.write("")

    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        st.markdown(_boot_sequence_html() + _hero_html(), unsafe_allow_html=True)
        st.markdown(_status_pill(), unsafe_allow_html=True)

        # ── Offline / guest mode ──
        if SUPABASE_MISSING:
            st.markdown("""
            <div style='background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); padding:16px; border-radius:8px; text-align:center; color:#EF4444; font-family:Inter, sans-serif; font-size:13px; margin-bottom:20px;'>
              ⚠ Vault connection unavailable.<br>
              You can still use InkOS in guest mode with limited features.
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ Enter as Guest", use_container_width=True, type="primary", key="guest_enter"):
                st.session_state[K.USER_HASH] = f"GUEST_{int(time.time())}"
                st.rerun()
            return

        # ── Routing ──
        latch_phase = st.session_state.get("latch_phase", "id")

        with st.container(border=True): # Gives the entire auth block a subtle border
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

    st.markdown("<div class='splash-step'>STEP 1 OF 2  —  IDENTITY</div>", unsafe_allow_html=True)

    uid = st.text_input(
        "Your ID",
        placeholder="Enter your identifier (e.g. Ameer)",
        label_visibility="collapsed",
        key="latch_uid_input",
        max_chars=64,
    )

    # Live ID check
    if uid and uid.strip():
        uid_clean = uid.strip()
        available, msg = check_id_availability(uid_clean)

        if len(uid_clean) < 3:
            st.markdown("<div class='id-badge invalid'>⚠ Too short — min 3 characters</div>", unsafe_allow_html=True)
        elif available:
            st.markdown(f"<div class='id-badge new'>✦ New identity — '{uid_clean}' will be created</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='id-badge existing'>✓ Welcome back, {uid_clean}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    proceed = st.button("Continue  →", use_container_width=True, type="primary", key="latch_proceed")

    if proceed:
        uid_clean = (uid or "").strip()
        if len(uid_clean) < 3:
            st.error("ID must be at least 3 characters.")
            return

        available, _ = check_id_availability(uid_clean)
        st.session_state["latch_uid"]    = uid_clean
        st.session_state["latch_is_new"] = available
        st.session_state["latch_phase"]  = "pin"
        st.rerun()

    st.markdown("""
    <div style='text-align:center; margin-top:16px; font-size:11px; color:#6B7280; font-family:JetBrains Mono, monospace;'>
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
    <div style='background:#121826; border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:16px 20px; margin-bottom:20px;'>
      <div style='font-size:10px; font-family:JetBrains Mono, monospace; color:#D4AF37; letter-spacing:.1em; margin-bottom:8px;'>{action_label}</div>
      <div style='font-size:22px; font-weight:700; color:#F8F9FA; margin-bottom:2px; font-family:Playfair Display, serif;'>{uid}</div>
      <div style='font-size:12px; color:#9CA3AF; font-family:Inter, sans-serif;'>{action_hint}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div class='splash-step'>STEP 2 OF 2  —  {action_verb.upper()}</div>", unsafe_allow_html=True)

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
        submit = st.button(btn_label, use_container_width=True, type="primary", key="latch_submit")

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
    <div style='text-align:center; padding:40px 24px;'>
      <div style='font-size:48px; margin-bottom:16px; color:#D4AF37;'>⚡</div>
      <div style='font-family:Playfair Display, serif; font-size:28px; font-weight:700; color:#F8F9FA; margin-bottom:8px;'>Identity Latched</div>
      <div style='font-family:Inter, sans-serif; font-size:14px; color:#9CA3AF; margin-bottom:4px;'>
        Welcome, {uid}
      </div>
      <div style='font-family:Amiri, serif; font-size:18px; color:#D4AF37;'>
        أهلاً بك في النظام
      </div>
      <div style='margin-top:30px;'>
        <div style='display:inline-flex; align-items:center; gap:8px; background:rgba(34, 197, 94, 0.1);
                    border:1px solid rgba(34, 197, 94, 0.3); border-radius:999px;
                    padding:6px 16px; font-size:10px; color:#22C55E; font-family:JetBrains Mono, monospace;'>
          <span class="dot" style="font-size:8px;">●</span> UPLINK ESTABLISHED
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(1.2)
    for key in ("latch_phase", "latch_uid", "latch_is_new"):
        st.session_state.pop(key, None)
    st.rerun()
