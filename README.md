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
    If you are running this from your local files directly, navigate to the project directory (`/Users/niteeshreddy/Desktop/Test/`) in your terminal.

2.  **Build and Run with Docker Compose:**
    This command will build the Streamlit application image and start both the application container and the Ollama service container.
    ```bash
    docker-compose up --build
    ```
    *   The `--build` flag ensures the Docker image for the app is built (or rebuilt if changes were made).
    *   The first time you run this, it might take a few minutes to download the `python:3.9-slim` and `ollama/ollama` base images.

3.  **Pull Ollama Models:**
    The Ollama service container (`ollama_service`) starts without any models. You need to pull the models you want to use.
    *   Open a **new terminal window** (while `docker-compose up` is running in the first one).
    *   Execute the following commands to pull desired models. You can pull them one by one:
        ```bash
        docker exec -it ollama_service ollama pull llama3.2:latest
        docker exec -it ollama_service ollama pull mistral
        # Add other models as needed, e.g., phi3, gemma:2b
        ```
        Or pull multiple models with a single command:
        ```bash
        docker exec -it ollama_service sh -c "ollama pull llama3.2:latest && ollama pull llama3 && ollama pull mistral && ollama pull phi3 && ollama pull gemma:2b"
        ```
    *   Model pulling can take some time depending on model size and internet speed. These models will be saved in a Docker volume (`ollama_data`) and will persist across container restarts.

4.  **Access the Application:**
    Once the containers are running and models are pulled, open your web browser and go to:
    [http://localhost:8501](http://localhost:8501)

    You should see the Text Summarizer interface. Select the model you pulled, paste your text, and get your summary.

## Usage

*   Enter text directly into the input area or upload a `.txt` file.
*   Select an available Ollama model from the sidebar. The default list includes `llama3.2:latest`, `llama3`, `mistral`, `phi3`, and `gemma:2b`.
*   If the model you pulled isn't listed or you want to use a different one you've pulled into the `ollama_service` container, you can type its name into the "**Enter new model name (and press Enter):**" field in the sidebar.
*   Optionally, provide a custom prompt template in the sidebar. Ensure your custom prompt includes `{text_to_summarize}` where the input text should be inserted.
*   Click "**Summarize Text**".

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
