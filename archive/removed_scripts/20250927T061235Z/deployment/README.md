# Deployment helpers for yeling-ai

Files:

- `start_server.py`: wrapper to run `ai/server.py` (full feature Flask server)
- `start_minimal.py`: wrapper to run `ai/server_minimal.py` (lightweight test server)
- `start_assistant.py`: wrapper to run `ai/start_ai_assistant.py` (scan + reports)
- `install_requirements.txt`: recommended Python packages (legacy name)
- `requirements.txt`: minimal runtime requirements (preferred)

How to use:

1. Create and activate a virtual environment (recommended):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install runtime dependencies (recommended layered approach):

   - Base (required for running the server):

   ```bash
   pip install -r deployment/requirements.base.txt
   ```

   - Model backends (install only if you need in-project model inference):

   ```bash
   pip install -r deployment/requirements.model.txt
   ```

   - Developer tools (tests, security scans):

   ```bash
   pip install -r deployment/requirements.dev.txt
   ```

3. Run the wrapper you need (example):

   ```bash
   python3 deployment/start_minimal.py
   ```

Troubleshooting:

- If you see ImportError for Flask or other packages, ensure you installed `deployment/requirements.txt` in the active venv.
- If the assistant cannot find models, ensure model files are placed under `ai/models` or update your configuration accordingly.
- For permission errors when binding to port 5000, ensure the port is free.

Notes:

- Deployment wrappers intentionally do not modify original source files. They only adjust `sys.path` and run the target script to provide a central entrypoint for CI and simple launches.
- Consider containerizing the app (Dockerfile) as a next step for reproducible deployments.

Runtime verification (items requiring environment/runtime):

- Flask server start and `/` or `/ask` endpoint checks — requires `flask` installed.
- Full `auto_deploy` end-to-end (bandit, safety scans, model downloads) — requires `bandit`, `safety` and network access.
- Model loading / multi-backend tests — requires torch/onnxruntime/pygpt4all etc., depending on configured backends.

Current static import report (run `python3 scripts/verify_imports.py` to refresh):

Summary (import-only smoke test):

- OK: cli.cli
- OK: services.server
- OK: services.server_minimal
- OK: services.assistant
- OK: scanners.dispatcher
- OK: scanners.file_scanner
- OK: scanners.complexity_scanner
- OK: scanners.dependency_scanner
- OK: scanners.security_scanner
- OK: utils.model_loader
- OK: utils.memory_cache
- OK: utils.responder
- OK: utils.context_manager
- OK: utils.report_generator

- FAIL: ai.server — No module named 'flask'
- FAIL: ai.server_minimal — No module named 'flask'
- FAIL: ai.start_ai_assistant — No module named 'flask'

The failures above indicate runtime dependencies (Flask) are not installed in the current environment. To run the full server and assistant checks, create and activate a virtualenv and install the packages listed in `deployment/requirements.txt` before re-running the import verifier or starting the wrappers.

For reproducible runtime verification, create and activate a virtualenv and install `deployment/requirements.txt` before running the wrappers.
