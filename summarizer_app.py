import streamlit as st
from summarizer_engine import summarize_text_ollama
import re # For word count

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced AI Text Summarizer | Ollama",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
DEFAULT_MODEL = "llama3.2:latest"
INITIAL_CUSTOM_PROMPT = "" # e.g., "Extract key entities from the following text"

# --- Session State Initialization ---
def init_session_state():
    defaults = {
        'selected_model': DEFAULT_MODEL,
        'custom_prompt_template': INITIAL_CUSTOM_PROMPT,
        'generated_summary': "",
        'input_text': "",
        'file_uploader_key': 0, # To allow re-uploading the same file
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# --- Helper Functions ---
def get_text_stats(text):
    word_count = len(re.findall(r'\w+', text))
    return f"Words: {word_count}"

def handle_file_upload():
    uploaded_file_obj = st.session_state.get(f"file_uploader_{st.session_state.file_uploader_key}")
    if uploaded_file_obj is not None:
        try:
            content = uploaded_file_obj.read().decode('utf-8')
            st.session_state.input_text = content
            st.toast(f"Successfully loaded '{uploaded_file_obj.name}'!", icon="📄")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.session_state.input_text = ""
        finally:
            # Increment key to allow re-uploading the same file after clearing
            st.session_state.file_uploader_key += 1 

# --- Sidebar UI ---
with st.sidebar:
    # st.image("https://ollama.com/public/ollama.png", width=100, use_column_width=False)
    st.image("https://ollama.com/public/ollama.png", width=100)

    st.title("⚙️ Summarizer Controls")
    st.divider()

    # Custom Prompt directly in sidebar
    with st.expander("Custom Prompt Instruction (Optional)", expanded=False):
            st.session_state.custom_prompt_template = st.text_area(
                "Your Custom Instruction (e.g., 'Extract key entities'):",
                height=100,
                value=st.session_state.custom_prompt_template,
                placeholder="Default internal prompt will be used if empty.",
                help="Enter your specific instruction. The app will automatically append the input text to it. Do NOT include '{text_to_summarize}'."
            )
            
            apply_col, reset_col = st.columns(2)
            with apply_col:
                if st.button("✅ Apply Prompt", key="apply_custom_prompt_btn", help="Confirms the custom instruction.", use_container_width=True):
                    st.toast("Custom instruction noted and ready!", icon="👍")
                    # No rerun needed, session state is already updated by text_area
            with reset_col:
                if st.button("🔄 Reset Instruction", key="reset_custom_prompt_instr_btn", help="Clears the custom instruction field.", use_container_width=True):
                    st.session_state.custom_prompt_template = INITIAL_CUSTOM_PROMPT
                    st.toast("Custom instruction cleared!", icon="🔄")
                    st.rerun()
    
    # Generate Summary button in sidebar
    summarize_button_sidebar = st.button(
        "🚀 Generate Summary", 
        use_container_width=True, 
        type="primary", 
        key="summarize_button_sidebar",
        help="Click to process the text and generate a summary."
    )
    st.markdown("<hr style='margin-top: 1em; margin-bottom: 1em;'>", unsafe_allow_html=True)
    st.caption("© 2024 Cascade AI Solutions") # Branding

# --- Main Application Area ---
st.title("✨ Advanced AI Text Summarizer")
st.markdown("Condense large texts into insightful summaries with LLMs.")

# --- Input and Output Columns with Containers ---
col1, col2 = st.columns(2, gap="large")

with col1:
    with st.container(border=True):
        st.header("📜 Input Your Text")
        st.session_state.input_text = st.text_area(
            "Paste Text Here (or use file uploader below):",
            value=st.session_state.input_text,
            height=250, # Reduced height
            key="main_input_text_area",
            help="The text you want to summarize."
        )
        # Display char/word count for input text
        st.caption(get_text_stats(st.session_state.input_text))

        # File uploader and clear button in a row
        upload_col, clear_col = st.columns([3,2])
        with upload_col:
            st.file_uploader(
                "📂 Upload .txt File",
                type=['txt'],
                key=f"file_uploader_{st.session_state.file_uploader_key}", # Dynamic key for re-upload
                on_change=handle_file_upload,
                help="Upload a plain text file for summarization."
            )
        with clear_col:
            if st.button("🗑️ Clear Input", use_container_width=True, help="Clears the input text area and uploaded file."):
                st.session_state.input_text = ""
                st.session_state.file_uploader_key += 1 # To allow re-uploading the same file
                st.toast("Input text cleared!", icon="✨")
                st.rerun()

with col2:
    with st.container(border=True):
        st.header("💡 Generated Summary")
        st.session_state.generated_summary = st.text_area(
            "Editable Summary Output:",
            value=st.session_state.generated_summary,
            height=250, # Reduced height
            key="summary_edit_text_area",
            help="The AI-generated summary will appear here. You can edit it as needed."
        )
        # Display char/word count for summary text
        st.caption(get_text_stats(st.session_state.generated_summary))

        # Download button for summary
        st.download_button(
            label="💾 Download Summary", # Made label slightly more descriptive
            data=st.session_state.generated_summary,
            file_name="summary.txt",
            mime="text/plain",
            use_container_width=True, # This will make it span the width of its container
            disabled=not st.session_state.generated_summary,
            help="Download the summary as a .txt file."
        )

# --- Summarization Logic ---
# The button state is checked using its key from the sidebar
if st.session_state.get('summarize_button_sidebar'):
    final_input_text = st.session_state.input_text # Simplified, as file upload now updates input_text directly

    if not final_input_text.strip():
        st.session_state.generated_summary = ""
        st.sidebar.warning("⚠️ Please input or upload text to summarize.") # Display warning in sidebar
    else:
        with st.spinner(f"⏳ Summarizing with {DEFAULT_MODEL}..."):
            user_instruction = st.session_state.custom_prompt_template.strip()
            final_prompt_for_ollama = None
            if user_instruction:
                # Combine user's instruction with the input text
                # Adding a clear separator like a newline or specific instruction phrasing
                final_prompt_for_ollama = f"{user_instruction}\n\nText to process:\n{final_input_text}"
            
            summary_result = summarize_text_ollama(
                final_input_text, # Still pass original text for potential non-custom-prompt use in engine or for context
                model_name=DEFAULT_MODEL, # Use the fixed DEFAULT_MODEL directly
                custom_prompt=final_prompt_for_ollama # This is now the fully formed prompt or None
            )

            if summary_result.startswith("Error:") or \
               summary_result.startswith("Ollama API Error:") or \
               summary_result.startswith("An unexpected error occurred:"):
                st.error(f"❌ {summary_result}")
                st.session_state.generated_summary = "" 

            else:
                st.session_state.generated_summary = summary_result
                st.toast("Summary generated successfully!", icon="🎉")
                st.rerun() # Update summary text_area and counts

# --- Footer ---
st.divider()
st.caption("✨ Happy Summarizing! ✨")
