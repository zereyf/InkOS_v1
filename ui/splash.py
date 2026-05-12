"""
ui/splash.py — InkOS Official Login Gateway
=============================================
Matches the UX/UI Purpose Design Document.
- Centralized, non-scrollable, locked-width container.
- Integrated SVG Feather/Circuit Logo.
- Perfected side-by-side checkbox & link alignment.
"""
from __future__ import annotations
import time
import streamlit as st
from state import K
from vault.vault_engine import authenticate_terminal, check_id_availability
from vault.supabase_client import SUPABASE_MISSING

_SPLASH_CSS = """
<style>
/* ── BASE & NO-SCROLL LOCK ── */
.stApp { background-color: #1A202C !important; overflow-y: hidden !important; }
header[data-testid="stHeader"] { display: none !important; }

/* Lock the main container to center and prevent scrolling */
.main .block-container {
    max-width: 420px !important; 
    padding-top: 2rem !important;
    padding-bottom: 0rem !important;
    margin: 0 auto !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 100vh;
}

/* ── TOP RIGHT LANGUAGE TOGGLE ── */
.lang-toggle {
    position: absolute;
    top: 20px;
    right: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #A8A095;
    background: rgba(255, 255, 255, 0.03);
    padding: 6px 14px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    z-index: 100;
}
.lang-toggle span { cursor: pointer; transition: color 0.2s; }
.lang-toggle span:hover { color: #FFFFFF; }
.lang-toggle .active { color: #4299E1; font-weight: 600; }

/* ── BRAND LOGO AREA ── */
.splash-logo-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 30px;
}
.splash-logo-main {
    font-family: 'Playfair Display', serif;
    font-size: 38px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
    margin-top: 5px;
}
.splash-logo-sub {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #7A7A7A;
    letter-spacing: 0.5em;
    margin-top: 5px;
}

/* ── AUTH CARD TYPOGRAPHY ── */
.auth-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 22px;
    font-weight: 600;
    color: #FFFFFF;
    text-align: center;
    margin-bottom: 4px;
}
.auth-subtitle {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    color: #7A7A7A;
    text-align: center;
    margin-bottom: 24px;
}

/* ── INPUTS & LABELS ── */
.stTextInput label {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 13px !important;
    color: #F8F9FA !important;
    font-weight: 500 !important;
}

/* ── CHECKBOX & FORGOT PASSWORD ALIGNMENT ── */
[data-testid="stCheckbox"] {
    display: flex;
    align-items: center;
    height: 100%;
}
[data-testid="stCheckbox"] label { 
    font-size: 14px !important; 
    color: #F8F9FA !important; 
    font-family: 'Montserrat', sans-serif !important;
}
.forgot-pass {
    text-align: right;
    margin-top: 10px;
}
.forgot-pass a {
    font-family: 'Montserrat', sans-serif;
    font-size: 13px;
    color: #4299E1;
    text-decoration: underline;
    cursor: pointer;
}

/* ── SECONDARY BUTTON (SIGN UP) ── */
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    margin-top: 10px !important;
}
button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* ── FOOTER ── */
.security-footer {
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 11px;
    color: #7A7A7A;
    margin-top: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
</style>
"""

def render_splash_screen() -> None:
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)
    
    # Language Toggle (Top Right Fixed)
    st.markdown("""
        <div class="lang-toggle">
            <span>🌐</span>
            <span class="active">English</span> | <span>العربية</span>
        </div>
    """, unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    
    is_login = st.session_state["auth_mode"] == "login"

    # SVG Logo Integration
    st.markdown("""
        <div class="splash-logo-container">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" style="width: 65px; height: 65px; fill: #4299E1;">
                <path d="M539.3 64.1C549.2 63.3 558.9 67.1 565.9 74.1C572.9 81.1 576.7 90.8 575.9 100.7C571.9 150 558.5 226.9 529.6 300.4C527.8 304.9 524.1 308.3 519.4 309.7L438.5 334C434.6 335.2 432 338.7 432 342.8C432 347.9 436.1 352 441.2 352L479.8 352C491.8 352 499.5 364.8 493.3 375.1C489.3 381.8 485 388.3 480.6 394.7C478.6 397.6 475.6 399.7 472.2 400.8L374.5 430C370.6 431.2 368 434.7 368 438.8C368 443.9 372.1 448 377.2 448L393.2 448C407.8 448 414.2 465.4 402 473.4C334 518.4 264.3 516.7 219.6 504.7C206.9 501.3 195.6 494.8 185.2 486.8L112 560C103.2 568.8 88.8 568.8 80 560C71.2 551.2 71.2 536.8 80 528L160 448L160.5 448.5C161.2 447.2 162.1 446 163.2 444.9L320 288C328.8 279.2 328.8 264.8 320 256C311.2 247.2 296.8 247.2 288 256L153.7 390.2C144.8 399.1 129.7 394.6 128.7 382C124.4 328.8 138 258.9 201.3 195.6C292.4 104.5 455.5 70.9 539.2 64.1z"/>
            </svg>
            <div class="splash-logo-main">AmeerInk</div>
            <div class="splash-logo-sub">I N K O S</div>
        </div>
    """, unsafe_allow_html=True)

    if SUPABASE_MISSING:
        st.markdown("""
        <div style='background:rgba(229,62,62,0.1); border:1px solid rgba(229,62,62,0.2); padding:16px; border-radius:8px; text-align:center; color:#E53E3E; font-family:Montserrat, sans-serif; font-size:12px; margin-bottom:20px;'>
          ⚠ Vault connection unavailable. Enterprise database offline.<br>
          Operating in Guest Mode.
        </div>
        """, unsafe_allow_html=True)

        if st.button("Continue as Guest", use_container_width=True, type="primary"):
            st.session_state[K.USER_HASH] = f"GUEST_{int(time.time())}"
            st.rerun()
        return

    # ── Main Authentication Box ──
    with st.container(border=True):
        if is_login:
            st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Please login to your InkOS account</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="auth-title">Create an Account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Register to secure your InkOS vault</div>', unsafe_allow_html=True)

        with st.form("auth_form", border=False):
            uid = st.text_input("Username/Email", placeholder="Enter your username or email")
            pin = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if is_login:
                # Perfect alignment for Checkbox and Forgot Password
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.checkbox("Remember me", value=True)
                with c2:
                    st.markdown('<div class="forgot-pass"><a>Forgot Password?</a></div>', unsafe_allow_html=True)
            else:
                pin_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            
            st.write("") # Micro-spacing before button
            btn_label = "Login" if is_login else "Sign Up"
            submit = st.form_submit_button(btn_label, type="primary", use_container_width=True)

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
                                success, err = authenticate_terminal(uid_clean, pin_clean, is_new=False)
                                if success:
                                    st.session_state[K.USER_HASH] = uid_clean
                                    st.rerun()
                                else:
                                    st.error("Incorrect password.")
                    else:
                        if not available:
                            st.error("Username already exists. Please Login.")
                        elif pin_clean != (pin_confirm or "").strip():
                            st.error("Passwords do not match.")
                        else:
                            with st.spinner("Creating secure vault..."):
                                success, err = authenticate_terminal(uid_clean, pin_clean, is_new=True)
                                if success:
                                    st.session_state[K.USER_HASH] = uid_clean
                                    st.rerun()
                                else:
                                    st.error(f"Registration failed: {err}")

    # ── Secondary Detached Action Button ──
    if is_login:
        if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
            st.session_state["auth_mode"] = "signup"
            st.rerun()
    else:
        if st.button("Already have an account? Login", type="secondary", use_container_width=True):
            st.session_state["auth_mode"] = "login"
            st.rerun()

    # ── Security Footer ──
    st.markdown("""
        <div class="security-footer">
            🛡️ Your data is protected by enterprise-grade security
        </div>
    """, unsafe_allow_html=True)
