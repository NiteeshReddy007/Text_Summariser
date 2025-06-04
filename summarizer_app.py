import streamlit as st
from summarizer_engine import summarize_text_ollama

st.set_page_config(page_title="Ollama Text Summarizer", layout="wide")

st.title("📝 Ollama-Powered Text Summarizer")
st.markdown("Summarize your text using local Ollama models.")

# Available Ollama models (user should have these pulled)
# You can customize this list
DEFAULT_MODELS = ["llama3.2:latest","llama3", "mistral", "phi3", "gemma:2b"]

# Initialize session state for model list if it doesn't exist
if 'available_models' not in st.session_state:
    st.session_state.available_models = DEFAULT_MODELS

with st.sidebar:
    st.header("⚙️ Configuration")
    
    selected_model = st.selectbox(
        "Choose Ollama Model:",
        options=st.session_state.available_models,
        index=0, # Default to the first model in the list
        help="Ensure the selected model is pulled in Ollama (e.g., `ollama pull llama3`)"
    )

    st.markdown("---_Or add a new model name below_---")
    new_model_name = st.text_input("Enter new model name (and press Enter):", key="new_model_input")
    if new_model_name and new_model_name not in st.session_state.available_models:
        st.session_state.available_models.append(new_model_name)
        st.experimental_rerun() # Rerun to update the selectbox

    custom_prompt_template = st.text_area(
        "Custom Prompt Template (Optional):",
        height=100,
        placeholder="e.g., 'Provide a very short summary of: {text_to_summarize}'\nLeave empty to use the default prompt.",
        help="If you use a custom prompt, ensure it includes '{text_to_summarize}' as a placeholder for the input text."
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Input Text")
    input_text = st.text_area("Paste your text here:", height=300, key="input_text_area")
    
    uploaded_file = st.file_uploader("Or upload a .txt file", type=['txt'])
    if uploaded_file is not None:
        try:
            input_text = uploaded_file.read().decode('utf-8')
            # Display the uploaded text in the text_area for consistency and potential editing
            st.text_area("File Content (editable if needed before summarizing):", value=input_text, height=300, key="file_content_display")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            input_text = "" # Clear input text on error

summarize_button = st.button("✨ Summarize Text", use_container_width=True, type="primary")

with col2:
    st.subheader("💡 Summary")
    summary_placeholder = st.empty() # Used to display summary or messages

if summarize_button:
    # Prioritize edited file content if available, otherwise use the main text area content
    if uploaded_file and 'file_content_display' in st.session_state:
        final_input_text = st.session_state.file_content_display
    else:
        final_input_text = input_text

    if not final_input_text.strip():
        summary_placeholder.warning("Please enter or upload some text to summarize.")
    else:
        with st.spinner(f"Summarizing using {selected_model}..."): 
            prompt_to_use = custom_prompt_template if custom_prompt_template.strip() else None
            summary = summarize_text_ollama(final_input_text, model_name=selected_model, custom_prompt=prompt_to_use)
            if summary.startswith("Error:") or summary.startswith("Ollama API Error:") or summary.startswith("An unexpected error occurred:"):
                summary_placeholder.error(summary)
            elif summary == "Input text is empty.":
                 summary_placeholder.warning(summary)
            else:
                summary_placeholder.markdown(summary)
else:
    summary_placeholder.info("Enter text and click 'Summarize Text' to see the result.")

st.markdown("---_Powered by Streamlit & Ollama_---")
