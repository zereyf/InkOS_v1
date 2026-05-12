"""
ui/splash.py — InkOS Official Login Gateway
=============================================
Matches the UX/UI Purpose Design Document (Section 6).
- Centralized login container (#2D3748)
- Blue accent primary buttons (#4299E1)
- Seamlessly integrates with existing vault_engine logic.
"""
from __future__ import annotations
import time
import streamlit as st
from state import K
from vault.vault_engine import authenticate_terminal, check_id_availability
from vault.supabase_client import SUPABASE_MISSING

# ── Inline styles scoped to match the PDF Mockup ──
_SPLASH_CSS = """
<style>
/* Base overrides for splash */
.stApp { background-color: #1A202C !important; }
header[data-testid="stHeader"] { display: none !important; }

/* Top Right Language Toggle */
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
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    z-index: 100;
}
.lang-toggle span { cursor: pointer; transition: color 0.2s; }
.lang-toggle span:hover { color: #FFFFFF; }
.lang-toggle .active { color: #4299E1; font-weight: 600; }

/* Brand Logo Area */
.splash-logo-container {
    text-align: center;
    margin-bottom: 30px;
    margin-top: 40px;
}
.splash-logo-main {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.splash-logo-sub {
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    color: #7A7A7A;
    letter-spacing: 0.4em;
    margin-top: 5px;
}

/* Auth Card Typography */
.auth-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 20px;
    font-weight: 600;
    color: #FFFFFF;
    text-align: center;
    margin-bottom: 4px;
}
.auth-subtitle {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #7A7A7A;
    text-align: center;
    margin-bottom: 24px;
}

/* Links & Utilities */
.auth-link {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #4299E1;
    text-align: right;
    cursor: pointer;
    text-decoration: none;
    display: block;
    margin-top: -10px;
    margin-bottom: 15px;
    transition: color 0.2s;
}
.auth-link:hover { color: #5BA3E8; }

.auth-switch {
    font-family: 'Montserrat', sans-serif;
    font-size: 12px;
    color: #7A7A7A;
    text-align: center;
    margin-top: 20px;
}
.auth-switch a {
    color: #4299E1;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
}

/* Custom Checkbox Alignment */
[data-testid="stCheckbox"] label { font-size: 12px !important; color: #7A7A7A !important; }

/* Security Footer */
.security-footer {
    text-align: center;
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    color: #7A7A7A;
    margin-top: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
</style>
"""

def render_splash_screen() -> None:
    st.markdown(_SPLASH_CSS, unsafe_allow_html=True)
    
    # Language Toggle (Visual match to PDF)
    st.markdown("""
        <div class="lang-toggle">
            <span>🌐</span>
            <span class="active">English</span> | <span>العربية</span>
        </div>
    """, unsafe_allow_html=True)

    # State management for Login vs Sign Up toggle
    if "auth_mode" not in st.session_state:
        st.session_state["auth_mode"] = "login"
    
    is_login = st.session_state["auth_mode"] == "login"

    _, center_col, _ = st.columns([1, 1.2, 1])
    
    with center_col:
        # AmeerInk Logo
        st.markdown("""
            <div class="splash-logo-container">
                <div style="font-size: 50px; color: #4299E1; margin-bottom: -15px;">A</div>
                <div class="splash-logo-main">AmeerInk</div>
                <div class="splash-logo-sub">I N K O S</div>
            </div>
        """, unsafe_allow_html=True)

        # ── Offline / guest mode ──
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

        # ── Auth Card (Matches Document exactly) ──
        with st.container(border=True):
            if is_login:
                st.markdown('<div class="auth-title">Welcome back</div>', unsafe_allow_html=True)
                st.markdown('<div class="auth-subtitle">Please login to your InkOS account</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="auth-title">Create an Account</div>', unsafe_allow_html=True)
                st.markdown('<div class="auth-subtitle">Register to secure your InkOS vault</div>', unsafe_allow_html=True)

            with st.form("auth_form", border=False):
                # Using Streamlit native inputs but they inherit our beautiful CSS from styles.py
                uid = st.text_input("Username/Email", placeholder="Enter your username or email")
                pin = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if is_login:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.checkbox("Remember me", value=True)
                    with c2:
                        st.markdown('<a class="auth-link">Forgot Password?</a>', unsafe_allow_html=True)
                else:
                    pin_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
                
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

        # ── Bottom Toggle ──
        if is_login:
            if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
                st.session_state["auth_mode"] = "signup"
                st.rerun()
        else:
            if st.button("Already have an account? Login", type="secondary", use_container_width=True):
                st.session_state["auth_mode"] = "login"
                st.rerun()

        # ── Footer ──
        st.markdown("""
            <div class="security-footer">
                🛡️ Your data is protected by enterprise-grade security
            </div>
        """, unsafe_allow_html=True)
