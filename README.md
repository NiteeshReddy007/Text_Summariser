# Ollama Text Summarizer with Streamlit

This project provides a web interface to summarize text using Ollama and large language models, all running locally via Docker.

## Prerequisites

*   **Docker and Docker Compose:** Ensure you have Docker Desktop (or Docker Engine + Docker Compose) installed and running on your system.
    *   [Install Docker](https://docs.docker.com/get-docker/)
    *   [Install Docker Compose](https://docs.docker.com/compose/install/) (Often included with Docker Desktop)
*   **Git:** To clone the repository (if you host it on GitHub/GitLab etc.).

## Setup and Running the Application

1.  **Clone the Repository (if applicable):**
    If you've hosted this project on a Git platform, clone it:
    ```bash
    git clone <your-repository-url>
    cd <repository-folder-name>
    ```
    
2.  **Build and Run with Docker Compose:**
    This command will build the Streamlit application image and start both the application container and the Ollama service container.
    ```bash
    docker-compose up --build
    ```
    *   The `--build` flag ensures the Docker image for the app is built (or rebuilt if changes were made).
    *   The first time you run this, it might take a few minutes to download the `python:3.9-slim` and `ollama/ollama` base images.

3.  **Pull the Required Ollama Model:**
    The Ollama service container (`ollama_service`) starts without any models. This application uses the `llama3.2:latest` model.
    *   Open a **new terminal window** (while `docker-compose up` is running in the first one).
    *   Execute the following command to pull the required model:
        ```bash
        docker exec -it ollama_service ollama pull llama3.2:latest
        ```
    *   Model pulling can take some time depending on its size and your internet speed. The model will be saved in a Docker volume (`ollama_data`) and will persist across container restarts.
    *   You can pull other models (e.g., `mistral`, `phi3`) for other purposes if you use Ollama for different tasks, but this specific Streamlit application is configured to use only `llama3.2:latest`.

4.  **Access the Application:**
    Once the containers are running and the `llama3.2:latest` model is pulled, open your web browser and go to:
    [http://localhost:8501](http://localhost:8501)

    You should see the AI Text Summarizer interface.

## Usage

1.  **Input Text:**
    *   Paste your text directly into the "Paste Text Here" area on the main page.
    *   Alternatively, upload a `.txt` file using the "📂 Upload .txt File" button.
    *   You can clear the current input text using the "🗑️ Clear Input" button.

2.  **Custom Prompt (Optional):**
    *   In the sidebar, expand the "Custom Prompt Instruction (Optional)" section.
    *   Enter any specific instructions for the summarizer (e.g., "Focus on the main conclusions", "Extract key entities").
    *   The application will automatically append your input text to this instruction. **Do not** include placeholders like `{text_to_summarize}` in your custom instruction.
    *   Click "✅ Apply Prompt" to confirm your instruction. A toast message will appear.
    *   Click "🔄 Reset Instruction" to clear your custom prompt and revert to the default internal prompt.

3.  **Generate Summary:**
    *   Click the "🚀 Generate Summary" button located in the sidebar.
    *   The summary will appear in the "Editable Summary Output" area.
    *   The application attempts to remove markdown formatting (like `**bold**` or `*italic*`) from the generated summary for a cleaner output.
    *   Word counts for both input and output text are displayed.

4.  **Download Summary:**
    *   Click the "📋 Download Summary" button below the summary output to save it as a `.txt` file.

## Stopping the Application

*   To stop the application, go to the terminal window where `docker-compose up` is running and press `Ctrl+C`.
*   To remove the containers (but keep the `ollama_data` volume with your models), you can run:
    ```bash
    docker-compose down
    ```
*   To remove the containers AND the `ollama_data` volume (deleting all pulled models within Docker):
    ```bash
    docker-compose down -v
    ```

## Project Structure

```
/Test
├── .git/                # Git version control files (if initialized)
├── .gitignore           # Specifies intentionally untracked files that Git should ignore
├── Dockerfile           # Instructions to build the Streamlit application Docker image
├── README.md            # This file: project overview, setup, and usage instructions
├── docker-compose.yml   # Defines and runs multi-container Docker applications (Streamlit app + Ollama service)
├── requirements.txt     # Python dependencies for the Streamlit application
├── summarizer_app.py    # Main Streamlit application script (UI and frontend logic)
├── summarizer_engine.py # Backend logic for text summarization using Ollama
└── __pycache__/         # Python bytecode cache (auto-generated)
```

*   **`Dockerfile`**: Defines the environment for the Streamlit application, installing Python, dependencies, and setting up the entry point.
*   **`docker-compose.yml`**: Orchestrates the deployment of the Streamlit app and the Ollama service. It manages networking, volumes for persistent Ollama model storage (`ollama_data`), and environment variables.
*   **`requirements.txt`**: Lists Python packages required by `summarizer_app.py` and `summarizer_engine.py` (e.g., `streamlit`, `ollama`).
*   **`summarizer_app.py`**: Contains all the Streamlit code to create the user interface, handle user inputs, manage session state, and display results.
*   **`summarizer_engine.py`**: Includes the core function `summarize_text_ollama` that communicates with the Ollama API to perform text summarization.
                