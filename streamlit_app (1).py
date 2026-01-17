"""
USI17 Emergency Translation Web UI
Multi-Model System: Grok → Gemini → Claude
Works on ANY computer via browser - NO installation needed!
"""

import streamlit as st
import io
import zipfile
from datetime import datetime
import time
from pathlib import Path

# PDF processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# Import our translator
from multi_model_translator import MultiModelTranslator

# Page config
st.set_page_config(
    page_title="USI17 Emergency Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight: bold;
}
.success-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
}
.warning-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #fff3cd;
    border: 1px solid #ffeeba;
}
.error-box {
    padding: 1rem;
    border-radius: 0.5rem;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = None
if 'results' not in st.session_state:
    st.session_state.results = []
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Title and header
st.title("🌐 USI17 V22.1 Emergency Translation System")
st.markdown("**60 Catalogs × 16 Languages in 1 Week** | Grok + Gemini + Claude Multi-Model System")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    st.subheader("🔑 API Keys")
    st.info("Enter at least ONE API key. Grok recommended for lowest cost.")
    
    grok_key = st.text_input(
        "Grok API Key (Cheapest - ¥6K)",
        type="password",
        help="Get at https://x.ai/api - Recommended!"
    )
    
    gemini_key = st.text_input(
        "Gemini API Key (Backup - ¥38K)",
        type="password",
        help="Get at https://ai.google.dev"
    )
    
    claude_key = st.text_input(
        "Claude API Key (Premium - ¥191K)",
        type="password",
        help="Get at https://console.anthropic.com"
    )
    
    st.markdown("---")
    
    st.subheader("💰 Budget Control")
    budget_limit = st.number_input(
        "Maximum Budget (¥)",
        min_value=5000,
        max_value=500000,
        value=30000,
        step=5000,
        help="Hard limit - system stops when reached"
    )
    
    st.markdown("---")
    
    # Initialize translator button
    if st.button("🚀 Initialize Translator", type="primary", use_container_width=True):
        if not (grok_key or gemini_key or claude_key):
            st.error("⚠️ Please enter at least ONE API key")
        else:
            with st.spinner("Initializing multi-model translator..."):
                try:
                    st.session_state.translator = MultiModelTranslator(
                        grok_api_key=grok_key if grok_key else None,
                        gemini_api_key=gemini_key if gemini_key else None,
                        claude_api_key=claude_key if claude_key else None,
                        max_budget_jpy=budget_limit
                    )
                    
                    models = st.session_state.translator.get_available_models()
                    st.success(f"✅ Translator ready!\n\nActive models: {', '.join(models)}")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # System status
    if st.session_state.translator:
        st.markdown("### 📊 System Status")
        
        costs = st.session_state.translator.cost_tracker.get_cost_jpy()
        budget_used = st.session_state.translator.cost_tracker.budget_used_percent()
        
        st.metric("Total Cost", f"¥{costs['total']:,.0f}")
        st.metric("Budget Used", f"{budget_used:.1f}%")
        st.metric("Translations", st.session_state.translator.stats['total_translations'])
        
        # TM hit rate
        tm_rate = st.session_state.translator.tm.get_hit_rate()
        st.metric("TM Hit Rate", f"{tm_rate:.1f}%")
    
    st.markdown("---")
    
    if st.button("🔄 Reset System", use_container_width=True):
        st.session_state.results = []
        st.session_state.translator = None
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload & Translate", "📊 Progress", "📥 Download", "📚 Help"])

with tab1:
    st.subheader("📁 Upload PDF Catalogs")
    
    # Check if translator is initialized
    if not st.session_state.translator:
        st.warning("⚠️ Please initialize the translator first (see sidebar)")
        st.stop()
    
    # File upload
    uploaded_files = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload up to 60 catalogs at once"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        with st.expander("📋 View File List"):
            for i, f in enumerate(uploaded_files, 1):
                st.text(f"{i}. {f.name}")
    
    st.markdown("---")
    st.subheader("🌍 Select Target Languages")
    
    # Initialize language selections in session state
    if 'lang_en' not in st.session_state:
        # Set defaults on first load
        defaults = ['lang_en', 'lang_de', 'lang_fr', 'lang_es', 'lang_pt', 'lang_it', 
                   'lang_cz', 'lang_pl', 'lang_tk', 'lang_vi', 'lang_th', 'lang_id',
                   'lang_ko', 'lang_cn', 'lang_tw', 'lang_mx']
        for key in defaults:
            st.session_state[key] = True
    
    # Quick selection buttons
    button_col1, button_col2, button_col3 = st.columns([1, 1, 3])
    
    with button_col1:
        if st.button("✅ Select All", use_container_width=True, key='btn_select_all'):
            st.session_state.lang_en = True
            st.session_state.lang_de = True
            st.session_state.lang_fr = True
            st.session_state.lang_es = True
            st.session_state.lang_pt = True
            st.session_state.lang_it = True
            st.session_state.lang_cz = True
            st.session_state.lang_pl = True
            st.session_state.lang_tk = True
            st.session_state.lang_vi = True
            st.session_state.lang_th = True
            st.session_state.lang_id = True
            st.session_state.lang_ko = True
            st.session_state.lang_cn = True
            st.session_state.lang_tw = True
            st.session_state.lang_mx = True
    
    with button_col2:
        if st.button("❌ Deselect All", use_container_width=True, key='btn_deselect_all'):
            st.session_state.lang_en = False
            st.session_state.lang_de = False
            st.session_state.lang_fr = False
            st.session_state.lang_es = False
            st.session_state.lang_pt = False
            st.session_state.lang_it = False
            st.session_state.lang_cz = False
            st.session_state.lang_pl = False
            st.session_state.lang_tk = False
            st.session_state.lang_vi = False
            st.session_state.lang_th = False
            st.session_state.lang_id = False
            st.session_state.lang_ko = False
            st.session_state.lang_cn = False
            st.session_state.lang_tw = False
            st.session_state.lang_mx = False
    
    col1, col2, col3, col4 = st.columns(4)
    
    lang_selections = {}
    
    with col1:
        lang_selections['EN'] = st.checkbox('English', key='lang_en')
        lang_selections['DE'] = st.checkbox('German', key='lang_de')
        lang_selections['FR'] = st.checkbox('French', key='lang_fr')
        lang_selections['ES'] = st.checkbox('Spanish', key='lang_es')
    
    with col2:
        lang_selections['PT'] = st.checkbox('Portuguese', key='lang_pt')
        lang_selections['IT'] = st.checkbox('Italian', key='lang_it')
        lang_selections['CZ'] = st.checkbox('Czech', key='lang_cz')
        lang_selections['PL'] = st.checkbox('Polish', key='lang_pl')
    
    with col3:
        lang_selections['TK'] = st.checkbox('Turkish', key='lang_tk')
        lang_selections['VI'] = st.checkbox('Vietnamese', key='lang_vi')
        lang_selections['TH'] = st.checkbox('Thai', key='lang_th')
        lang_selections['ID'] = st.checkbox('Indonesian', key='lang_id')
    
    with col4:
        lang_selections['KO'] = st.checkbox('Korean', key='lang_ko')
        lang_selections['CN'] = st.checkbox('Chinese (CN)', key='lang_cn')
        lang_selections['TW'] = st.checkbox('Chinese (TW)', key='lang_tw')
        lang_selections['MX'] = st.checkbox('Spanish (MX)', key='lang_mx')
    
    selected_langs = [code for code, selected in lang_selections.items() if selected]
    
    st.info(f"📊 {len(selected_langs)} languages selected × {len(uploaded_files) if uploaded_files else 0} files = {len(selected_langs) * (len(uploaded_files) if uploaded_files else 0)} translation jobs")
    
    st.markdown("---")
    
    # Start translation button
    if st.button("🚀 START TRANSLATION", type="primary", use_container_width=True, disabled=st.session_state.processing):
        if not uploaded_files:
            st.error("❌ Please upload at least one PDF file")
        elif not selected_langs:
            st.error("❌ Please select at least one target language")
        else:
            st.session_state.processing = True
            
            # Progress containers
            progress_container = st.container()
            
            with progress_container:
                st.markdown("### 📊 Translation Progress")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Metrics
                mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                completed_metric = mcol1.empty()
                speed_metric = mcol2.empty()
                cost_metric = mcol3.empty()
                model_metric = mcol4.empty()
                
                # Process files
                total_jobs = len(uploaded_files) * len(selected_langs)
                completed = 0
                start_time = time.time()
                
                for pdf_file in uploaded_files:
                    catalog_name = pdf_file.name.replace('.pdf', '')
                    
                    # Extract text from PDF
                    status_text.text(f"📄 Extracting text from {pdf_file.name}...")
                    
                    try:
                        if PDF_AVAILABLE:
                            with pdfplumber.open(pdf_file) as pdf:
                                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                        else:
                            text = f"[PDF extraction not available - placeholder text for {catalog_name}]"
                    except Exception as e:
                        st.error(f"❌ Error extracting {pdf_file.name}: {e}")
                        continue
                    
                    # Translate to each language
                    for lang in selected_langs:
                        status_text.text(f"🔄 Translating {catalog_name} → {lang}...")
                        
                        try:
                            result = st.session_state.translator.translate(text, lang)
                            
                            if result['success']:
                                # Store result
                                filename = f"{catalog_name}_{lang}.txt"
                                st.session_state.results.append({
                                    'filename': filename,
                                    'content': result['translation'],
                                    'catalog': catalog_name,
                                    'language': lang,
                                    'model': result['model_used'],
                                    'cost_jpy': result.get('cost_jpy', 0)
                                })
                                
                                completed += 1
                                
                                # Update progress
                                progress = completed / total_jobs
                                progress_bar.progress(progress)
                                
                                # Update metrics
                                elapsed = time.time() - start_time
                                rate = completed / (elapsed / 3600) if elapsed > 0 else 0
                                remaining = (total_jobs - completed) / rate if rate > 0 else 0
                                
                                completed_metric.metric("Completed", f"{completed}/{total_jobs}")
                                speed_metric.metric("Speed", f"{rate:.1f} jobs/hr")
                                
                                costs_jpy = st.session_state.translator.cost_tracker.get_cost_jpy()
                                cost_metric.metric("Cost", f"¥{costs_jpy['total']:,.0f}")
                                model_metric.metric("Model", result['model_used'])
                            
                            else:
                                st.error(f"❌ {catalog_name} → {lang} failed: {result.get('error', 'Unknown error')}")
                        
                        except Exception as e:
                            st.error(f"❌ Error translating {catalog_name} → {lang}: {e}")
                
                # Completion
                st.session_state.processing = False
                status_text.text("✅ Translation complete!")
                st.success(f"🎉 Successfully completed {completed} translations!")
                st.balloons()

with tab2:
    st.subheader("📊 Real-Time Statistics")
    
    if st.session_state.translator:
        translator = st.session_state.translator
        
        # Cost breakdown
        st.markdown("### 💰 Cost Breakdown")
        costs_jpy = translator.cost_tracker.get_cost_jpy()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Grok", f"¥{costs_jpy['grok']:,.0f}")
        col2.metric("Gemini", f"¥{costs_jpy['gemini']:,.0f}")
        col3.metric("Claude", f"¥{costs_jpy['claude']:,.0f}")
        col4.metric("Total", f"¥{costs_jpy['total']:,.0f}")
        
        # Budget status
        st.markdown("### 📈 Budget Status")
        budget_used_pct = translator.cost_tracker.budget_used_percent()
        
        st.progress(min(budget_used_pct / 100, 1.0))
        
        budget_remaining = translator.cost_tracker.budget_remaining_jpy()
        st.text(f"Used: ¥{costs_jpy['total']:,.0f} / ¥{translator.cost_tracker.max_budget_jpy:,} ({budget_used_pct:.1f}%)")
        st.text(f"Remaining: ¥{budget_remaining:,.0f}")
        
        # Usage stats
        st.markdown("### 📊 Translation Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Translations", translator.stats['total_translations'])
            st.metric("TM Hits (FREE)", translator.stats['tm_hits'])
            st.metric("Grok Used", translator.stats['grok_used'])
        
        with col2:
            st.metric("Gemini Used", translator.stats['gemini_used'])
            st.metric("Claude Used", translator.stats['claude_used'])
            tm_rate = translator.tm.get_hit_rate()
            st.metric("TM Hit Rate", f"{tm_rate:.1f}%")
    
    else:
        st.info("Initialize translator to see statistics")

with tab3:
    st.subheader("📥 Download Results")
    
    if st.session_state.results:
        st.success(f"✅ {len(st.session_state.results)} translations completed")
        
        # Download all as ZIP
        if st.button("📦 Download All as ZIP", type="primary", use_container_width=True):
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for result in st.session_state.results:
                    zip_file.writestr(result['filename'], result['content'])
            
            st.download_button(
                label="💾 Click to Download translations.zip",
                data=zip_buffer.getvalue(),
                file_name=f"usi17_translations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("### 📋 Individual Files")
        
        # Group by catalog
        catalogs = {}
        for result in st.session_state.results:
            if result['catalog'] not in catalogs:
                catalogs[result['catalog']] = []
            catalogs[result['catalog']].append(result)
        
        for catalog, results in catalogs.items():
            with st.expander(f"📄 {catalog} ({len(results)} languages)"):
                for result in results:
                    col1, col2, col3 = st.columns([4, 2, 1])
                    
                    with col1:
                        st.text(result['filename'])
                    with col2:
                        st.text(f"{result['model']}")
                    with col3:
                        st.download_button(
                            label="⬇️",
                            data=result['content'],
                            file_name=result['filename'],
                            mime="text/plain",
                            key=f"dl_{result['filename']}"
                        )
    
    else:
        st.info("No translations completed yet. Upload files and start translation in the Upload tab.")

with tab4:
    st.subheader("📚 Quick Help & Reference")
    
    st.markdown("""
    ### 🚀 Quick Start
    
    1. **Get API Key** (at least one):
       - Grok (recommended): https://x.ai/api
       - Gemini (backup): https://ai.google.dev
       - Claude (premium): https://console.anthropic.com
    
    2. **Initialize System**:
       - Enter API key(s) in sidebar
       - Click "Initialize Translator"
       - Wait for confirmation
    
    3. **Upload & Translate**:
       - Upload PDF files
       - Select target languages
       - Click "START TRANSLATION"
       - Monitor progress
    
    4. **Download Results**:
       - Go to Download tab
       - Download as ZIP or individual files
    
    ### 💰 Cost Estimates
    
    | Model | Cost (per 960 jobs) | Quality |
    |-------|---------------------|---------|
    | Grok 4.1 Fast | ¥6,000-10,000 | ⭐⭐⭐⭐⭐ |
    | Gemini 3 Flash | ¥35,000-40,000 | ⭐⭐⭐⭐⭐ |
    | Claude Sonnet 4.5 | ¥180,000-200,000 | ⭐⭐⭐⭐⭐ |
    
    ### 🆘 Troubleshooting
    
    **Problem**: "API key invalid"  
    **Solution**: Copy entire key, check billing enabled
    
    **Problem**: "All models failed"  
    **Solution**: Check internet, verify API credits
    
    **Problem**: "Budget limit reached"  
    **Solution**: Increase budget in sidebar
    
    **Problem**: "Too slow"  
    **Solution**: Use Grok (fastest model)
    
    ### ℹ️ System Info
    
    - **Glossary**: 509 technical terms enforced
    - **Languages**: 16 simultaneous translations
    - **Translation Memory**: 70% cost savings on reused content
    - **Budget Protection**: Hard limits prevent overspending
    - **Multi-Model**: Automatic failover for reliability
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 12px;'>"
    "USI17 V22.1 Emergency Translation System | "
    "Grok + Gemini + Claude Multi-Model | "
    "Built for CKD Corporation | "
    "Zero Installation Required"
    "</div>",
    unsafe_allow_html=True
)
