# NLP to API (Calendar)

This project trains a sequence-to-sequence model to translate natural language commands into structured JSON payloads for a Calendar API. It demonstrates how to fine-tune a small language model to act as an interface between users and backend services.

The codebase is featuring a FastAPI backend, a Streamlit frontend, Pydantic data validation, and Docker support.

## Features

- **Synthetic Data Generation**: Automatically creates a dataset of English commands and their corresponding JSON API targets (e.g., scheduling meetings, setting reminders, querying schedules, updating events).
- **Parameter-Efficient Fine-Tuning (PEFT)**: Uses LoRA (Low-Rank Adaptation) to efficiently fine-tune a `t5-small` model, making it lightweight and fast to train.
- **Modular Architecture**: Clean separation of concerns with a dedicated `backend` (FastAPI, Models, Services) and `frontend` (Streamlit).
- **Dockerized**: Easily spin up the entire application stack using Docker Compose.

## Project Structure

```
nlp/
├── backend/                  # FastAPI backend service
│   ├── app/
│   │   ├── api/              # API router and endpoints
│   │   ├── core/             # Pydantic settings and config
│   │   ├── models/           # LoRA / T5 Model logic
│   │   ├── schemas/          # Request/Response Pydantic schemas
│   │   └── services/         # Parsing logic and regex post-processing
│   ├── tests/                # Pytest unit tests
├── frontend/                 # Streamlit frontend service
│   └── app.py
├── model_artifacts/          # Directory containing the fine-tuned LoRA adapter
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile.backend        # Backend container instructions
├── Dockerfile.frontend       # Frontend container instructions
└── nlp2api_calls.ipynb       # Original Notebook for training and synthetic data
```

## Running the Application

### Option 1: Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed.
2. Build and start the services:
   ```bash
   docker-compose up --build
   ```
3. The frontend will be available at [http://localhost:8501](http://localhost:8501)
4. The backend API docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs)

### Option 2: Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Backend**:
   Set `PYTHONPATH` so the `backend` directory is recognized.
   ```bash
   # Windows PowerShell
   $env:PYTHONPATH=".\backend"
   uvicorn backend.app.main:app --reload --port 8000
   ```
3. **Run the Frontend**:
   In a new terminal:
   ```bash
   streamlit run frontend/app.py
   ```

## Testing and Benchmarking

This project includes a comprehensive test suite covering both individual components and the complete pipeline.

### Running Automated Tests
The `pytest` suite includes small unit tests for the regex logic (`test_parser.py`) and full integration tests for the API endpoint (`test_api.py`).
```bash
$env:PYTHONPATH=".\backend"
pytest backend/tests/ -v
```

### Running the Benchmark
To measure model latency, throughput, and accuracy against a known evaluation dataset, run the standalone benchmark script:
```bash
$env:PYTHONPATH=".\backend"
python backend/benchmark.py
```
This script will load the LoRA weights, parse `eval_data.json`, and output detailed performance metrics to your terminal.
