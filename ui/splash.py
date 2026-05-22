"""
ui/splash.py — InkOS Official Login Gateway
=============================================
Phase 2 Security Hardening:

  SEC-1 FIXED: K.IS_ADMIN is now set from get_user_profile() immediately
               after a successful login. The username-string comparison
               ("AMEERINK") in admin.py is the old gate — this replaces it.
               Admin privileges come from the `is_admin` column in Supabase.
"""
from __future__ import annotations

import time
import streamlit as st

from state import K
from vault.vault_engine import authenticate_terminal, check_id_availability, get_user_profile
from vault.supabase_client import SUPABASE_MISSING

_SPLASH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, .stApp {
    background-color: #050505 !important; /* Deep obsidian void */
    background-image: radial-gradient(circle at 50% 0%, rgba(201, 168, 76, 0.05) 0%, transparent 50%);
    overflow: hidden !important; /* Enforce stable, non-scrollable view */
}
header[data-testid="stHeader"] { display: none !important; }

.main .block-container {
    max-width: 440px !important;
    padding: 0rem 2rem !important;
    margin: 0 auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    min-height: 100vh !important;
}

/* Language Toggle - Minimalist */
.lang-toggle {
    position: fixed;
    top: 24px;
    right: 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #5D6D7E;
    z-index: 99999;
}
.lang-toggle span { cursor: pointer; transition: color 0.2s; }
.lang-toggle span:hover { color: #C9A84C; }
.lang-toggle .active { color: #C9A84C; font-weight: 600; }

/* Logo & Branding */
.splash-logo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 40px;
}
.splash-logo-main {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: 0.2em;
    color: #FFFFFF;
    text-transform: uppercase;
    margin-top: 15px;
}
.splash-logo-sub {
    font-family: 'Cairo', sans-serif;
    font-size: 16px;
    color: #C9A84C; /* Gold accent */
    margin-top: 8px;
    opacity: 0.9;
}

/* Auth Headers */
.auth-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 16px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #FFFFFF;
    text-align: center;
    margin-bottom: 8px;
}
.auth-subtitle {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #5D6D7E;
    text-align: center;
    letter-spacing: 0.05em;
    margin-bottom: 30px;
}

/* Terminal-Style Inputs */
.stTextInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #7C9EBF !important;
}
.stTextInput > div > div > input {
    background-color: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    color: #FFFFFF !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 14px !important;
    border-radius: 4px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 8px rgba(201, 168, 76, 0.2) !important;
}

/* Checkbox */
[data-testid="stCheckbox"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    color: #5D6D7E !important;
}

/* Primary CTA Button (Centered, Horizontal, Larger) */
button[kind="primary"] {
    background: #C9A84C !important;
    color: #000000 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    border: none !important;
    margin-top: 20px !important;
    transition: all 0.3s ease !important;
}
button[kind="primary"]:hover {
    background: #E2D5BC !important;
    box-shadow: 0 0 15px rgba(201, 168, 76, 0.4) !important;
}

/* Secondary Toggle Button */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px dashed rgba(255, 255, 255, 0.15) !important;
    color: #7C9EBF !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    margin-top: 15px !important;
}
button[kind="secondary"]:hover {
    border-color: rgba(124, 158, 191, 0.5) !important;
    color: #FFFFFF !important;
}

.security-footer {
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.2);
    margin-top: 40px;
}
</style>
"""


def _set_logged_in(uid: str) -> None:
    """
    SEC-1: After successful auth, pull admin status from the DB and store it
    in session state. Never derive admin status from the username.
    """
    st.session_state[K.USER_HASH] = uid
    profile = get_user_profile(uid)
    st.session_state[K.IS_ADMIN] = profile.get("is_admin", False)


def render_splash_screen() -> None:
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)

    st.markdown("""
        <div class="lang-toggle">
            <span>🌐</span>
            <span class="active">English</span> | <span>العربية</span>
        </div>
    """, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"

    is_login = st.session_state["auth_mode"] == "login"

    # Logo
    st.markdown("""
        <div class="splash-logo-container">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"
                 style="width: 65px; height: 65px; fill: #4299E1;">
                <path d="M539.3 64.1C549.2 63.3 558.9 67.1 565.9 74.1C572.9 81.1 576.7 90.8
                575.9 100.7C571.9 150 558.5 226.9 529.6 300.4C527.8 304.9 524.1 308.3 519.4
                309.7L438.5 334C434.6 335.2 432 338.7 432 342.8C432 347.9 436.1 352 441.2
                352L479.8 352C491.8 352 499.5 364.8 493.3 375.1C489.3 381.8 485 388.3 480.6
                394.7C478.6 397.6 475.6 399.7 472.2 400.8L374.5 430C370.6 431.2 368 434.7
                368 438.8C368 443.9 372.1 448 377.2 448L393.2 448C407.8 448 414.2 465.4 402
                473.4C334 518.4 264.3 516.7 219.6 504.7C206.9 501.3 195.6 494.8 185.2
                486.8L112 560C103.2 568.8 88.8 568.8 80 560C71.2 551.2 71.2 536.8 80
                528L160 448L160.5 448.5C161.2 447.2 162.1 446 163.2 444.9L320 288C328.8
                279.2 328.8 264.8 320 256C311.2 247.2 296.8 247.2 288 256L153.7 390.2C144.8
                399.1 129.7 394.6 128.7 382C124.4 328.8 138 258.9 201.3 195.6C292.4 104.5
                455.5 70.9 539.2 64.1z"/>
            </svg>
            <div class="splash-logo-main">AmeerInk</div>
            <div class="splash-logo-sub">I N K O S</div>
        </div>
    """, unsafe_allow_html=True)

    if SUPABASE_MISSING:
        st.markdown("""
        <div style='background:rgba(229,62,62,0.1); border:1px solid rgba(229,62,62,0.2);
             padding:16px; border-radius:8px; text-align:center; color:#E53E3E;
             font-family:Montserrat,sans-serif; font-size:12px; margin-bottom:20px;'>
          ⚠ Vault connection unavailable. Enterprise database offline.<br>
          Operating in Guest Mode.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Continue as Guest", use_container_width=True, type="primary"):
            st.session_state[K.USER_HASH] = f"GUEST_{int(time.time())}"
            st.session_state[K.IS_ADMIN]  = False
            st.rerun()
        return

    with st.container(border=True):
        if is_login:
            st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Please login to your InkOS account</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="auth-title">Create an Account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Register to secure your InkOS vault</div>',
                        unsafe_allow_html=True)

        with st.form("auth_form", border=False):
            uid = st.text_input("Username / Email",
                                placeholder="Enter your username or email")
            pin = st.text_input("Password", type="password",
                                placeholder="Enter your password")

            if is_login:
                st.checkbox("Remember me", value=True)
            else:
                pin_confirm = st.text_input("Confirm Password", type="password",
                                            placeholder="Re-enter your password")

            btn_label = "Login" if is_login else "Sign Up"
            submit    = st.form_submit_button(btn_label, type="primary",
                                              use_container_width=True)

            if submit:
                uid_clean = (uid or "").strip()
                pin_clean = (pin or "").strip()

                if len(uid_clean) < 3 or len(pin_clean) < 4:
                    st.error("Invalid credentials format.")
                else:
                    available, _ = check_id_availability(uid_clean)

                    if is_login:
                        if available:
                            st.error("Account not found. Please Sign Up.")
                        else:
                            with st.spinner("Authenticating..."):
                                success, err = authenticate_terminal(
                                    uid_clean, pin_clean, is_new=False
                                )
                            if success:
                                # SEC-1: admin flag comes from DB, not username
                                _set_logged_in(uid_clean)
                                st.rerun()
                            else:
                                st.error(err or "Authentication failed.")
                    else:
                        if not available:
                            st.error("Username already exists. Please Login.")
                        elif pin_clean != (pin_confirm or "").strip():
                            st.error("Passwords do not match.")
                        else:
                            with st.spinner("Creating secure vault..."):
                                success, err = authenticate_terminal(
                                    uid_clean, pin_clean, is_new=True
                                )
                            if success:
                                _set_logged_in(uid_clean)
                                st.rerun()
                            else:
                                st.error(f"Registration failed: {err}")

    if is_login:
        if st.button("Don't have an account? Sign Up",
                     type="secondary", use_container_width=True):
            st.session_state["auth_mode"] = "signup"
            st.rerun()
    else:
        if st.button("Already have an account? Login",
                     type="secondary", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.rerun()

    st.markdown("""
        <div class="security-footer">
            🛡️ Your data is protected by enterprise-grade security
        </div>
    """, unsafe_allow_html=True)
