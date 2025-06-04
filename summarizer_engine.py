import ollama
import json
import os

OLLAMA_API_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

try:
    client = ollama.Client(host=OLLAMA_API_HOST)
except Exception as e:
    print(f"Error initializing Ollama client with host {OLLAMA_API_HOST}: {e}")
    client = None

def summarize_text_ollama(text, model_name='llama3', custom_prompt=None):
    """
    Summarizes the input text using a specified Ollama model.

    Args:
        text (str): The text to summarize.
        model_name (str): The name of the Ollama model to use (e.g., 'llama3', 'mistral').
        custom_prompt (str, optional): A custom prompt template.
                                     Must include '{text_to_summarize}' placeholder.

    Returns:
        str: The summarized text, or an error message if summarization fails.
    """
    if not client:
        return f"Ollama client not initialized. Check OLLAMA_HOST ({OLLAMA_API_HOST}) and Ollama service."

    if not text.strip():
        return "Input text is empty."

    if custom_prompt:
        prompt = custom_prompt.format(text_to_summarize=text)
    else:
        prompt = f"""Please provide a concise and comprehensive summary of the following text.
Highlight the key points and main ideas, while maintaining the original context and meaning.
Do not add any information that is not present in the original text.
Avoid personal opinions or interpretations. The summary should be easy to read and understand.

Text to summarize:
{text}

Summary:"""

    try:
        response = client.chat(
            model=model_name,
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ]
        )
        summary = response['message']['content']
        return summary.strip()
    except ollama.ResponseError as e:
        if "model not found" in str(e).lower() or (hasattr(e, 'status_code') and e.status_code == 404):
            return f"Error: Model '{model_name}' not found on Ollama server ({OLLAMA_API_HOST}). Please ensure it is pulled. Inside Docker, use: docker exec -it ollama_service ollama pull {model_name}"
        elif "connection refused" in str(e).lower() or isinstance(e, ollama.ConnectionError) or (hasattr(e, 'status_code') and e.status_code == 503):
             return f"Ollama API Error: Could not connect to Ollama at {OLLAMA_API_HOST}. Ensure Ollama service is running and accessible. Details: {e}"
        return f"Ollama API Error ({e.status_code if hasattr(e, 'status_code') else 'N/A'}): {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    sample_text = """
    The James Webb Space Telescope (JWST) is a space telescope designed primarily to conduct infrared astronomy.
    As the largest optical telescope in space, its high infrared resolution and sensitivity allow it to view objects
    too old, distant, or faint for the Hubble Space Telescope. This is expected to enable a broad range of
    investigations across the fields of astronomy and cosmology, such as observation of the first stars and
    the formation of the first galaxies, and detailed atmospheric characterization of potentially habitable exoplanets.
    JWST was launched in December 2021 and, as of 2024, is operational.
    """

    print(f"Attempting to summarize with Ollama (client configured for: {OLLAMA_API_HOST})...\n")

    if not client:
        print("Ollama client could not be initialized. Please check Ollama setup and OLLAMA_HOST environment variable.")
    else:
        summary_default = summarize_text_ollama(sample_text)
        print(f"Summary (default model 'llama3'):\n{summary_default}\n")

        custom_prompt_template = "Summarize this text in one sentence: {text_to_summarize}"
        summary_custom_prompt = summarize_text_ollama(sample_text, model_name='llama3', custom_prompt=custom_prompt_template)
        print(f"Summary (custom prompt, model 'llama3'):\n{summary_custom_prompt}\n")

        empty_text_summary = summarize_text_ollama("")
        print(f"Summary of empty text: {empty_text_summary}")
