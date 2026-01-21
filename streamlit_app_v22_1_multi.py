"""
USI17 V22.2 Streamlit Web Interface - MULTI-DIRECTIONAL
Complete support for ANY of 17 languages as source → multiple targets
"""

import streamlit as st
import os
from v22_1_translator import USI17_V22_2_Translator
import tempfile

# ============================================================================
# PASSWORD PROTECTION
# ============================================================================
def check_password():
    """
    Password protection for the application.
    
    To change password: Edit the line below with your desired password.
    Current password: CKD2026USI17
    """
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "CKD2026USI17":  # ← CHANGE PASSWORD HERE
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show password input
    if "password_correct" not in st.session_state:
        st.markdown('<div class="main-header">🔒 USI17 V22.2 Translation System</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">CKD Corporation - Authorized Access Only</div>', unsafe_allow_html=True)
        st.text_input(
            "Enter Password",
            type="password",
            on_change=password_entered,
            key="password",
            placeholder="Enter password to access system"
        )
        st.info("💡 Contact chris248ma@gmail.com for access credentials")
        return False
    
    # Password incorrect, show error
    elif not st.session_state["password_correct"]:
        st.markdown('<div class="main-header">🔒 USI17 V22.2 Translation System</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">CKD Corporation - Authorized Access Only</div>', unsafe_allow_html=True)
        st.text_input(
            "Enter Password",
            type="password",
            on_change=password_entered,
            key="password",
            placeholder="Enter password to access system"
        )
        st.error("❌ Incorrect password. Please try again.")
        st.info("💡 Contact chris248ma@gmail.com for access credentials")
        return False
    
    # Password correct
    else:
        return True

# Check password before loading the app
if not check_password():
    st.stop()  # Don't continue if password is wrong

# ============================================================================
# MAIN APPLICATION (only loads if password is correct)
# ============================================================================

# Page config
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
    .stTextArea textarea {
        font-size: 14px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Language definitions (17 languages)
LANGUAGES = {
    'ja': 'Japanese',
    'en': 'English',
    'de': 'German',
    'fr': 'French',
    'es': 'Spanish',
    'em': 'Spanish (MX)',
    'pt': 'Portuguese',
    'it': 'Italian',
    'cz': 'Czech',
    'pl': 'Polish',
    'tk': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'ko': 'Korean',
    'cn': 'Chinese (CN)',
    'tw': 'Chinese (TW)'
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
st.markdown('<div class="sub-header">ANY of 17 languages → Multiple target languages simultaneously</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    st.subheader("API Keys")
    gemini_key = st.text_input("Gemini API Key (Primary)", type="password",
                                help="Optional backup")
    grok_key = st.text_input("Grok API Key (Backup)", type="password", 
                              help="Required: Grok 4 Fast with 2M context")
    claude_key = st.text_input("Claude API Key (Premium)", type="password",
                                help="Optional premium backup")
    
    st.subheader("📂 V22.2 Master File")
    V22_2_file = st.file_uploader("Upload USI17_V22_2_MASTER.txt", type=['txt'],
                                   help="Required: 47,000-line complete system")
    
    st.subheader("💰 Budget Control")
    max_budget = st.number_input("Maximum Budget (¥)", min_value=1000, value=30000, step=1000)
    
    st.markdown("---")
    
    # Initialize button
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
                st.success("✅ V22.2 system loaded! All 276 agents active.")
            except Exception as e:
                st.error(f"❌ Initialization failed: {str(e)}")
    
    # System status
    if st.session_state.initialized:
        st.markdown("---")
        st.header("📊 System Status")
        stats = st.session_state.translator.get_stats()
        
        st.metric("Total Cost", f"¥{stats['total_cost']:,.0f}")
        st.metric("Budget Used", f"{stats['budget_used_pct']:.1f}%")
        st.metric("Translations", stats['translations_completed'])
        st.metric("TM Hit Rate", f"{stats['tm_hit_rate']:.1f}%")

# Main content area
if not st.session_state.initialized:
    st.warning("⚠️ Please initialize the translator first using the sidebar.")
    st.info("""
    **Quick Start:**
    1. Enter Grok API key (get at https://x.ai/api)
    2. Upload USI17_V22_2_MASTER.txt (47,000 lines)
    3. Click "Initialize Translator"
    
    **System Capabilities:**
    - ANY of 17 languages as source
    - Multiple target languages simultaneously (1-16)
    - 276 agents, 14 Laws, 509 glossary terms
    - RTF/TAG preservation
    - English priority option
    """)
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📝 Text Translation", "📁 File Translation", "📚 Help"])
    
    with tab1:
        st.markdown("### Multi-Directional Text Translation")
        
        # Source language selection
        col1, col2 = st.columns([1, 2])
        
        with col1:
            source_lang = st.selectbox(
                "Source Language (Select 1)",
                options=list(LANGUAGES.keys()),
                format_func=lambda x: LANGUAGES[x],
                key='source_lang_select'
            )
            
            # Update source lang in session state
            if source_lang != st.session_state.source_lang:
                st.session_state.source_lang = source_lang
                # Reset target selections to exclude new source
                for code in LANGUAGES.keys():
                    if code != source_lang:
                        st.session_state[f'target_{code}'] = True
                    else:
                        st.session_state[f'target_{code}'] = False
                st.rerun()
        
        with col2:
            st.info(f"📍 Translating FROM: **{LANGUAGES[source_lang]}**")
        
        st.markdown("---")
        
        # Target language selection
        st.markdown("### Target Languages (Select 1-16)")
        st.markdown(f"*{LANGUAGES[source_lang]} is automatically excluded*")
        
        # Select All / Deselect All buttons
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 3])
        
        with btn_col1:
            if st.button("✅ Select All", use_container_width=True):
                for code in LANGUAGES.keys():
                    if code != source_lang:
                        st.session_state[f'target_{code}'] = True
                st.rerun()
        
        with btn_col2:
            if st.button("❌ Deselect All", use_container_width=True):
                for code in LANGUAGES.keys():
                    if code != source_lang:
                        st.session_state[f'target_{code}'] = False
                st.rerun()
        
        with btn_col3:
            english_first = st.checkbox("English First", value=True,
                                       help="Put English as first target language (when selected)")
        
        # Language checkboxes in 4 columns
        cols = st.columns(4)
        
        for i, (code, name) in enumerate(LANGUAGES.items()):
            if code != source_lang:  # Exclude source language
                with cols[i % 4]:
                    # Initialize default value if not set
                    if f'target_{code}' not in st.session_state:
                        st.session_state[f'target_{code}'] = True
                    
                    st.checkbox(
                        name,
                        value=st.session_state[f'target_{code}'],
                        key=f'target_{code}'
                    )
        
        # Show selected count
        selected_targets = [code for code in LANGUAGES.keys() 
                           if code != source_lang and st.session_state.get(f'target_{code}', True)]
        st.info(f"📊 **{len(selected_targets)} target language(s) selected** → 1 API call")
        
        st.markdown("---")
        
        # Text input
        source_text = st.text_area(
            f"Source Text ({LANGUAGES[source_lang]})",
            height=200,
            placeholder=f"Enter {LANGUAGES[source_lang]} text here..."
        )
        
        # Translate button
        translate_col1, translate_col2, translate_col3 = st.columns([2, 1, 2])
        
        with translate_col2:
            if st.button(f"🚀 TRANSLATE TO {len(selected_targets)} LANGUAGES", 
                        use_container_width=True, type="primary",
                        disabled=not source_text or len(selected_targets) == 0):
                
                if not source_text:
                    st.error("❌ Please enter source text")
                elif len(selected_targets) == 0:
                    st.error("❌ Please select at least one target language")
                else:
                    with st.spinner(f"Translating to {len(selected_targets)} languages with V22.2..."):
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
        
        # Display results
        if st.session_state.translation_result:
            result = st.session_state.translation_result
            
            st.markdown("---")
            st.subheader("📊 Translation Results")
            
            # Metrics
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Languages", len(result['targets']))
            with metric_col2:
                st.metric("Model", result['model'])
            with metric_col3:
                st.metric("Cost", f"¥{result['cost_jpy']:.2f}")
            with metric_col4:
                st.metric("TM Hits", f"{result['tm_hits']}/{len(result['targets'])}")
            
            # Show translations
            st.markdown("### Translations")
            
            for i, lang_code in enumerate(result['target_langs'], 1):
                with st.expander(f"{i}. {LANGUAGES[lang_code]}", expanded=(i <= 3)):
                    st.text_area(
                        f"{LANGUAGES[lang_code]} Translation",
                        value=result['targets'][lang_code],
                        height=100,
                        key=f'output_{lang_code}',
                        label_visibility='collapsed'
                    )
            
            # Download options
            st.markdown("---")
            st.subheader("💾 Download Options")
            
            download_col1, download_col2, download_col3 = st.columns(3)
            
            with download_col1:
                st.download_button(
                    label="📄 Download TAB-delimited (with header)",
                    data=result['with_header'],
                    file_name="translation_multi_language.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with download_col2:
                st.download_button(
                    label="📋 Download TAB-delimited (data only)",
                    data=result['multi_language_tab'],
                    file_name="translation_data.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with download_col3:
                # Excel preview info
                st.info("💡 Open in Excel\nFile → Tab-delimited → Perfect columns")
            
            # Show preview of TAB format
            with st.expander("📋 Preview TAB-Delimited Format"):
                st.text(result['with_header'])
                st.caption("This format opens perfectly in Excel with proper columns")
    
    with tab2:
        st.markdown("### File Translation (RTF with TAG Preservation)")
        st.markdown("Upload RTF files with InDesign/memoQ/Wordfast TAGs for translation")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload RTF Files",
            type=['rtf', 'txt'],
            accept_multiple_files=True,
            help="Upload one or more RTF files with TAGs"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            
            # Show file details
            with st.expander("📁 Uploaded Files", expanded=True):
                for file in uploaded_files:
                    st.text(f"• {file.name} ({file.size:,} bytes)")
            
            # Source language
            col1, col2 = st.columns(2)
            
            with col1:
                file_source_lang = st.selectbox(
                    "Source Language",
                    options=list(LANGUAGES.keys()),
                    format_func=lambda x: LANGUAGES[x],
                    key='file_source_lang'
                )
            
            with col2:
                st.info(f"📍 Source: **{LANGUAGES[file_source_lang]}**")
            
            st.markdown("---")
            
            # Target languages
            st.markdown("### Target Languages")
            st.markdown(f"*{LANGUAGES[file_source_lang]} automatically excluded*")
            
            # Select All / Deselect All
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            
            with btn_col1:
                if st.button("✅ Select All (Files)", use_container_width=True, key='file_select_all'):
                    for code in LANGUAGES.keys():
                        if code != file_source_lang:
                            st.session_state[f'file_target_{code}'] = True
                    st.rerun()
            
            with btn_col2:
                if st.button("❌ Deselect All (Files)", use_container_width=True, key='file_deselect_all'):
                    for code in LANGUAGES.keys():
                        st.session_state[f'file_target_{code}'] = False
                    st.rerun()
            
            with btn_col3:
                file_english_first = st.checkbox(
                    "English First (Files)", 
                    value=True,
                    key='file_english_first',
                    help="Put English as first target language"
                )
            
            # Language checkboxes
            cols = st.columns(4)
            
            for i, (code, name) in enumerate(LANGUAGES.items()):
                if code != file_source_lang:
                    with cols[i % 4]:
                        # Initialize default value if not set
                        if f'file_target_{code}' not in st.session_state:
                            st.session_state[f'file_target_{code}'] = True
                        
                        st.checkbox(
                            name,
                            value=st.session_state[f'file_target_{code}'],
                            key=f'file_target_{code}'
                        )
            
            selected_file_targets = [code for code in LANGUAGES.keys() 
                                    if code != file_source_lang and st.session_state.get(f'file_target_{code}', True)]
            
            st.info(f"📊 **{len(selected_file_targets)} target language(s)** × **{len(uploaded_files)} file(s)** = **{len(selected_file_targets) * len(uploaded_files)} translations**")
            
            st.markdown("---")
            
            # Translate button
            if st.button(
                f"🚀 TRANSLATE {len(uploaded_files)} FILES TO {len(selected_file_targets)} LANGUAGES",
                type="primary",
                use_container_width=True,
                disabled=len(selected_file_targets) == 0
            ):
                if len(selected_file_targets) == 0:
                    st.error("❌ Please select at least one target language")
                else:
                    # Process files
                    results = []
                    total_cost = 0.0
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for file_idx, file in enumerate(uploaded_files):
                        status_text.text(f"Processing {file.name} ({file_idx + 1}/{len(uploaded_files)})...")
                        
                        try:
                            # Read RTF content
                            rtf_content = file.read().decode('utf-8', errors='ignore')
                            
                            # Translate
                            result = st.session_state.translator.translate_rtf_file(
                                rtf_content=rtf_content,
                                source_lang=file_source_lang,
                                target_langs=selected_file_targets,
                                english_first=file_english_first
                            )
                            
                            results.append({
                                'filename': file.name,
                                'result': result
                            })
                            
                            total_cost += result['cost_jpy']
                            
                        except Exception as e:
                            st.error(f"❌ Failed to process {file.name}: {str(e)}")
                        
                        progress_bar.progress((file_idx + 1) / len(uploaded_files))
                    
                    status_text.text("✅ All files processed!")
                    st.success(f"🎉 Translated {len(results)} files to {len(selected_file_targets)} languages!")
                    
                    # Show results
                    st.markdown("---")
                    st.subheader("📊 Translation Results")
                    
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.metric("Files Processed", len(results))
                    with metric_col2:
                        st.metric("Languages", len(selected_file_targets))
                    with metric_col3:
                        st.metric("Total Cost", f"¥{total_cost:.2f}")
                    with metric_col4:
                        total_tags = sum(r['result']['tag_count'] for r in results)
                        st.metric("TAGs Preserved", total_tags)
                    
                    # Download section
                    st.markdown("---")
                    st.subheader("💾 Download Translations")
                    
                    for file_result in results:
                        filename = file_result['filename']
                        result = file_result['result']
                        
                        with st.expander(f"📄 {filename}", expanded=True):
                            st.text(f"TAGs detected: {result['tag_count']}")
                            st.text(f"LAW_13 status: {'✅ PASSED' if result['law_13_passed'] else '❌ FAILED'}")
                            st.text(f"Cost: ¥{result['cost_jpy']:.2f}")
                            
                            # Download buttons for each language
                            download_cols = st.columns(min(4, len(selected_file_targets)))
                            
                            for idx, target_lang in enumerate(selected_file_targets):
                                with download_cols[idx % 4]:
                                    bilingual_content = result['bilingual_outputs'][target_lang]
                                    output_filename = f"{filename.replace('.rtf', '')}_{target_lang.upper()}.txt"
                                    
                                    st.download_button(
                                        label=f"⬇️ {LANGUAGES[target_lang]}",
                                        data=bilingual_content,
                                        file_name=output_filename,
                                        mime="text/plain",
                                        use_container_width=True,
                                        key=f'download_{filename}_{target_lang}'
                                    )
        else:
            st.info("""
            **📋 RTF File Translation Features:**
            - Upload RTF files with InDesign/memoQ/Wordfast TAGs
            - TAGs automatically detected and preserved
            - Multi-file batch processing
            - LAW_13 enforcement (RTF structure validation)
            - Bilingual output with TAGs intact
            - Compatible with all major CAT tools
            
            **Supported TAG Formats:**
            - InDesign: `<tag>`, `</tag>`
            - memoQ: `[uf ufcatid="..."}`, `{uf]`
            - Wordfast: `{1}`, `{2}`, etc.
            - Trados: `<g1>`, `<x1/>`, etc.
            
            **Upload RTF files to begin!**
            """)
    
    with tab3:
        st.markdown("### 📚 Help & Documentation")
        
        st.markdown(f"""
        ## USI17 V22.2 Multi-Directional Translation System
        
        ### Key Innovation
        **Unlike competitors** (Google Translate, DeepL, Systran):
        - They translate: Source → Target1, Source → Target2, Source → Target3 (multiple API calls)
        - **USI17 translates**: Source → [Target1 + Target2 + Target3 + ...] (ONE API call!)
        
        ### Supported Languages ({len(LANGUAGES)})
        """ + ", ".join([f"{LANGUAGES[code]}" for code in LANGUAGES.keys()]) + """
        
        ### Any Direction
        - **Source**: Select ANY of 17 languages
        - **Targets**: Select 1-16 languages (excluding source)
        - **English Priority**: Automatically puts English first in output (optional)
        
        ### Example Workflows
        
        **Workflow 1: Japanese → 16 languages**
        - Source: Japanese
        - Targets: All 16 others
        - Output: 17 columns (JA + 16 translations)
        - Cost: ~¥200 per page
        
        **Workflow 2: English → Asian languages**
        - Source: English
        - Targets: Japanese, Korean, Chinese (CN), Chinese (TW), Thai, Vietnamese
        - Output: 7 columns (EN + 6 translations)
        - Cost: ~¥100 per page
        
        **Workflow 3: German → English + French**
        - Source: German
        - Targets: English, French
        - Output: 3 columns (DE + EN + FR)
        - Cost: ~¥50 per page
        
        ### Critical Features
        - **276 Agents**: Complete V22.2 architecture
        - **14 Laws**: Including SI unit spacing (50mm → 50 mm in English)
        - **535 Glossary Terms**: LOCKED translations (ショックキラー = "shock absorber" NEVER "shock killer")
        - **TAG Preservation**: Maintains InDesign, memoQ, Wordfast formatting
        - **Translation Memory**: 70% cost savings on repeated content
        
        ### Cost Estimation
        - Single page × 1 language: ¥50-100
        - Single page × 16 languages: ¥200-500
        - 60 catalogs × 16 languages: ¥6,000-10,000 (with TM reuse)
        
        ### Support
        System built with CSV Protocol - Zero truncation, all 47,000 lines loaded.
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
USI17 V22.2 Multi-Directional Translation | 17 Languages × 16 Targets = 272 Translation Directions | 
Grok 4 Fast (2M Context) | Built for CKD Corporation
</div>
""", unsafe_allow_html=True)
