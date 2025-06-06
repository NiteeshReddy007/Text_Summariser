import ollama
import json
import os
import httpx

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
                                      If provided, this is treated as the full prompt. The app will construct it.

    Returns:
        str: The summarized text, or an error message if summarization fails.
    """
    if not client:
        return f"Ollama client not initialized. Check OLLAMA_HOST ({OLLAMA_API_HOST}) and Ollama service."

    if not text.strip():
        return "Input text is empty."

    if custom_prompt:
        prompt = custom_prompt
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
        summary = summary.replace('*', '')
        return summary.strip()
    except ollama.ResponseError as e:
        if "model not found" in str(e).lower() or \
           (hasattr(e, 'status_code') and e.status_code == 404):
            return f"Error: Model '{model_name}' not found on Ollama server ({OLLAMA_API_HOST}). Please ensure it is pulled. Inside Docker, use: docker exec -it ollama_service ollama pull {model_name}"
        elif "connection refused" in str(e).lower() or \
             (hasattr(e, 'status_code') and e.status_code == 503):
             return f"Ollama API Error: Could not connect to Ollama at {OLLAMA_API_HOST}. Ensure Ollama service is running and accessible. Details: {e}"
        return f"Ollama API Error ({e.status_code if hasattr(e, 'status_code') else 'N/A'}): {e}"
    except httpx.RequestError as e:
        return f"Ollama Connection Error: Could not connect to Ollama at {OLLAMA_API_HOST}. Network issue: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    sample_text = """
    Cricket is a bat-and-ball game played between two teams of eleven players on a field at the centre of which is a 22-yard (20-metre) pitch
    with a wicket at each end, each comprising two bails balanced on three stumps. The batting side scores runs by striking the ball bowled
    at the wicket with the bat and running between the wickets, while the bowling and fielding side tries to prevent this (by preventing the
    ball from leaving the field, and getting the ball to either wicket) and dismiss each batter (so they are "out"). Means of dismissal
    include being bowled, when the ball hits the stumps and dislodges the bails, and by the fielding side catching the ball after it is hit
    by the bat, but before it hits the ground. When ten batters have been dismissed, the innings ends and the teams swap roles. The game is
    adjudicated by two umpires, aided by a third umpire and match referee in international matches.
    """

    print(f"Attempting to summarize with Ollama (client configured for: {OLLAMA_API_HOST})...\n")

    if not client:
        print("Ollama client could not be initialized. Please check Ollama setup and OLLAMA_HOST environment variable.")
    else:
        # Test with default prompt
        summary_default = summarize_text_ollama(sample_text, model_name='llama3.2:latest')
        print(f"Summary (default prompt, model 'llama3.2:latest'):\n{summary_default}\n")

        # Test with a custom instruction (simulating how the app would construct the full prompt)
        user_instruction_example = "Explain the basic objective of cricket in one sentence."
        # The summarize_text_ollama function expects the combined prompt if custom_prompt is used.
        full_custom_prompt_for_test = f"{user_instruction_example}\n\nText to summarize:\n{sample_text}"

        summary_custom_prompt = summarize_text_ollama(
            sample_text, # This 'text' argument is used by the default prompt if custom_prompt is None.
                                 # If custom_prompt is provided, the actual text being summarized is part of full_custom_prompt_for_test.
            model_name='llama3.2:latest',
            custom_prompt=full_custom_prompt_for_test
        )
        print(f"Summary (custom instruction, model 'llama3.2:latest'):\n{summary_custom_prompt}\n")

        empty_text_summary = summarize_text_ollama("")
        print(f"Summary of empty text: {empty_text_summary}")
