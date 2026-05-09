"""
ui/sidebar.py — Sidebar Command Deck
====================================
v13.3: Persistence Latch Patch.
       - Synchronized with config/personas.py legacy keys.
       - Hardened index resolution for browser refreshes.
"""

# ... (Previous imports remain the same) ...

def render_sidebar() -> SidebarConfig:
    with st.sidebar:
        # ... (Identity and Wordmark logic remains the same) ...

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── PERSONA SELECTOR (v2026.4 LATCH) ──────────────────────────────────
        st.markdown(f'<div class="vc-header" style="margin-top:20px; font-size:0.65rem;">[ {t("active_persona", fallback="ACTIVE_PERSONA").upper()} ]</div>', unsafe_allow_html=True)
        
        user_personas = _load_user_personas(st.session_state.get(K.USER_HASH, ''))

        # 1. BUILD THE MAP
        # We use a clean map to separate the UI Label from the Data
        options_map: dict = {'None': None}
        
        # Add Starter Personas [S]
        for name, p_data in STARTER_PERSONAS.items():
            if name != 'None':
                options_map[f'{name} [S]'] = p_data
                
        # Add Custom Personas [C]
        for p_data in user_personas:
            options_map[f"{p_data['name']} [C]"] = p_data
            
        options_list = list(options_map.keys())

        # 2. RECOVER ACTIVE STATE
        # Check URL first, then Session State
        url_p_name = st.query_params.get("p")
        current_active = st.session_state.get(K.ACTIVE_PERSONA)

        # 3. RESOLVE INDEX (The Persistence Latch)
        p_index = 0
        if url_p_name:
            # Match by searching for the name inside our labels
            for i, label in enumerate(options_list):
                if label.startswith(url_p_name):
                    p_index = i
                    break
        elif current_active:
            # If we have a dict in state, find which label points to it
            active_name = current_active.get('name')
            for i, label in enumerate(options_list):
                if label.startswith(active_name) or (url_p_name and label.startswith(url_p_name)):
                    p_index = i
                    break

        # 4. THE WIDGET
        selected_key = st.selectbox(
            'Persona Select', 
            options=options_list,
            index=p_index, 
            key='sb_persona_widget', # Unique key to avoid collisions
            label_visibility='collapsed',
        )
        
        # 5. SYNC STATE & URL
        active_p = options_map[selected_key]
        st.session_state[K.ACTIVE_PERSONA] = active_p

        if active_p:
            # Save the "Short Name" to the URL for clean rehydration
            st.query_params['p'] = active_p.get('name', '')
        else:
            if 'p' in st.query_params:
                del st.query_params['p']

        # ── UI FEEDBACK ──────────────────────────────────────────────────────
        if active_p:
            st.markdown(f"""
                <div style="background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.25); padding:8px; border-radius:3px; font-size:0.6rem; color:var(--gold);">
                    <strong>{active_p.get('name','')}</strong><br>
                    <span style="color:var(--text-muted); font-style:italic;">{active_p.get('role','')[:60]}...</span>
                </div>
            """, unsafe_allow_html=True)

        # ... (Options and Metrics remain the same) ...

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        islamic_mode     = islamic_mode,
        aesthetic_choice = aesthetic_choice,
        active_persona   = active_p,
        expert_mode      = expert_mode,
    )
