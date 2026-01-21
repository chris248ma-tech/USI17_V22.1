"""
USI17 V22.2 Streamlit Web Interface - MULTI-DIRECTIONAL
Complete support for ANY of 17 languages as source → multiple targets
"""

import streamlit as st
import os
from v22_2_translator import USI17_V22_2_Translator  # ← UPDATED IMPORT
import tempfile

# ============================================================================
# PASSWORD PROTECTION
# ============================================================================
def check_password():
    """Password protection (CKD2026USI17)"""
    def password_entered():
        if st.session_state["password"] == "CKD2026USI17":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown('<div class="main-header">🔒 USI17 V22.2 Translation System</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">CKD Corporation - Authorized Access Only</div>', unsafe_allow_html=True)
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.info("💡 Contact chris248ma@gmail.com for access")
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown('<div class="main-header">🔒 USI17 V22.2 Translation System</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">CKD Corporation - Authorized Access Only</div>', unsafe_allow_html=True)
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("❌ Incorrect password")
        st.info("💡 Contact chris248ma@gmail.com for access")
        return False
    
    else:
        return True

if not check_password():
    st.stop()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.set_page_config(
    page_title="USI17 V22.2 - Multi-Directional Translation",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 16px;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Language definitions
LANGUAGES = {
    'ja': 'Japanese', 'en': 'English', 'de': 'German', 'fr': 'French',
    'es': 'Spanish', 'em': 'Spanish (MX)', 'pt': 'Portuguese', 
    'it': 'Italian', 'cz': 'Czech', 'pl': 'Polish', 'tk': 'Turkish',
    'vi': 'Vietnamese', 'th': 'Thai', 'id': 'Indonesian', 
    'ko': 'Korean', 'cn': 'Chinese (CN)', 'tw': 'Chinese (TW)'
}

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None
if 'source_lang' not in st.session_state:
    st.session_state.source_lang = 'ja'

# Header
st.markdown('<div class="main-header">🌐 USI17 V22.2 - Multi-Directional Translation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ANY of 17 languages → Multiple targets simultaneously</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    st.subheader("API Keys")
    gemini_key = st.text_input("Gemini API Key (Primary)", type="password")
    grok_key = st.text_input("Grok API Key (Backup)", type="password")
    claude_key = st.text_input("Claude API Key (Premium)", type="password")
    
    st.subheader("📂 V22.2 Master File")
    V22_2_file = st.file_uploader("Upload USI17_V22_2_MASTER.txt", type=['txt'],
                                   help="Required: 47,805-line system with 535 terms")
    
    st.subheader("💰 Budget Control")
    max_budget = st.number_input("Maximum Budget (¥)", min_value=1000, value=30000, step=1000)
    
    st.markdown("---")
    
    if st.button("🚀 Initialize Translator", use_container_width=True, type="primary"):
        if not grok_key:
            st.error("❌ Grok API key required!")
        elif not V22_2_file:
            st.error("❌ V22.2 Master file required!")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as tmp:
                tmp.write(V22_2_file.getvalue().decode('utf-8'))
                tmp_path = tmp.name
            
            try:
                st.session_state.translator = USI17_V22_2_Translator(
                    grok_api_key=grok_key,
                    gemini_api_key=gemini_key if gemini_key else None,
                    claude_api_key=claude_key if claude_key else None,
                    max_budget=max_budget,
                    V22_2_master_path=tmp_path
                )
                st.session_state.initialized = True
                st.success("✅ V22.2 system loaded! 535 terms, 276 agents active.")
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
    
    if st.session_state.initialized:
        st.markdown("---")
        st.header("📊 System Status")
        stats = st.session_state.translator.get_stats()
        
        st.metric("Total Cost", f"¥{stats['total_cost']:,.0f}")
        st.metric("Budget Used", f"{stats['budget_used_pct']:.1f}%")
        st.metric("Translations", stats['translations_completed'])
        st.metric("TM Hit Rate", f"{stats['tm_hit_rate']:.1f}%")

# Main content
if not st.session_state.initialized:
    st.warning("⚠️ Please initialize the translator first")
    st.info("""
    **Quick Start:**
    1. Enter Grok API key
    2. Upload USI17_V22_2_MASTER.txt (47,805 lines)
    3. Click "Initialize Translator"
    
    **V22.2 Improvements:**
    - 31 new Electric Motion terms (535 total, up from 509)
    - Fixed: ショックキラー = "shock absorber" (not "shock killer")
    - New terms: System Chart, Inline Mount, Parallel Mount, etc.
    """)
else:
    tab1, tab2, tab3 = st.tabs(["📝 Text Translation", "📁 File Translation", "📚 Help"])
    
    with tab1:
        st.markdown("### Multi-Directional Text Translation")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            source_lang = st.selectbox(
                "Source Language",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                key='source_lang_select'
            )
            
            if source_lang != st.session_state.source_lang:
                st.session_state.source_lang = source_lang
                st.rerun()
        
        with col2:
            st.info(f"📍 FROM: **{LANGUAGES[source_lang]}**")
        
        st.markdown("---")
        st.markdown("### Target Languages")
        
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
        
        with btn_col1:
            if st.button("✅ Select All", use_container_width=True):
                for code in LANGUAGES.keys():
                    if code != source_lang:
                        st.session_state[f'target_{code}'] = True
                st.rerun()
        
        with btn_col2:
            if st.button("❌ Deselect All", use_container_width=True):
                for code in LANGUAGES.keys():
                    st.session_state[f'target_{code}'] = False
                st.rerun()
        
        with btn_col3:
            english_first = st.checkbox("English First", value=True)
        
        cols = st.columns(4)
        
        for i, (code, name) in enumerate(LANGUAGES.items()):
            if code != source_lang:
                with cols[i % 4]:
                    if f'target_{code}' not in st.session_state:
                        st.session_state[f'target_{code}'] = True
                    
                    st.checkbox(name, value=st.session_state[f'target_{code}'], key=f'target_{code}')
        
        selected_targets = [code for code in LANGUAGES.keys() 
                           if code != source_lang and st.session_state.get(f'target_{code}', True)]
        st.info(f"📊 **{len(selected_targets)} target(s)** → 1 API call")
        
        st.markdown("---")
        
        source_text = st.text_area(
            f"Source Text ({LANGUAGES[source_lang]})",
            height=200,
            placeholder=f"Enter {LANGUAGES[source_lang]} text..."
        )
        
        translate_col1, translate_col2, translate_col3 = st.columns([2, 1, 2])
        
        with translate_col2:
            if st.button(f"🚀 TRANSLATE", 
                        use_container_width=True, type="primary",
                        disabled=not source_text or len(selected_targets) == 0):
                
                with st.spinner(f"Translating with V22.2..."):
                    try:
                        result = st.session_state.translator.translate(
                            source_text=source_text,
                            source_lang=source_lang,
                            target_langs=selected_targets,
                            input_format='text',
                            preserve_tags=True,
                            english_first=english_first
                        )
                        
                        st.session_state.translation_result = result
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Translation failed: {str(e)}")
        
        if st.session_state.translation_result:
            result = st.session_state.translation_result
            
            st.markdown("---")
            st.subheader("📊 Results")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Languages", len(result['targets']))
            with col2:
                st.metric("Model", result['model'])
            with col3:
                st.metric("Cost", f"¥{result['cost_jpy']:.2f}")
            with col4:
                st.metric("TM Hits", f"{result['tm_hits']}/{len(result['targets'])}")
            
            st.markdown("### Translations")
            
            for i, lang_code in enumerate(result['target_langs'], 1):
                with st.expander(f"{i}. {LANGUAGES[lang_code]}", expanded=(i <= 3)):
                    st.text_area(
                        LANGUAGES[lang_code],
                        value=result['targets'][lang_code],
                        height=100,
                        key=f'output_{lang_code}',
                        label_visibility='collapsed'
                    )
            
            st.markdown("---")
            st.subheader("💾 Download")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📄 With Header",
                    data=result['with_header'],
                    file_name="translation.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                st.download_button(
                    "📋 Data Only",
                    data=result['multi_language_tab'],
                    file_name="data.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col3:
                st.info("💡 Excel: Tab-delimited")
    
    with tab2:
        st.markdown("### RTF File Translation")
        st.info("RTF translation feature - upload files with TAGs preserved")
    
    with tab3:
        st.markdown("### 📚 USI17 V22.2 Documentation")
        
        st.markdown(f"""
        ## V22.2 Multi-Directional Translation System
        
        ### What's New in V22.2
        - **31 new Electric Motion terms** (535 total, up from 509)
        - **Fixed:** ショックキラー = "shock absorber" (was incorrectly "shock killer")
        - **New terminology:** System Chart, Inline Mount, Parallel Mount, Payload, etc.
        
        ### Key Innovation
        **Simultaneous Translation:** Source → [Target1 + Target2 + ...] in ONE API call
        
        Unlike competitors (Google, DeepL, Systran) who use multiple API calls
        
        ### Supported Languages ({len(LANGUAGES)})
        """ + ", ".join(LANGUAGES.values()) + """
        
        ### Features
        - 276 agents, 14 Laws
        - 535 LOCKED glossary terms
        - RTF/TAG preservation
        - Translation Memory (70% savings)
        - Prompt caching (90% discount)
        
        ### Cost Estimation
        - 1 page × 1 language: ¥50-100
        - 1 page × 16 languages: ¥200-500
        - 60 catalogs × 16 languages: ¥6,000-10,000 (with TM)
        """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
USI17 V22.2 Multi-Directional Translation | 535 Terms | 276 Agents | Built for CKD Corporation
</div>
""", unsafe_allow_html=True)