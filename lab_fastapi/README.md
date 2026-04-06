# LV-Lab FastAPI Site Runner

This app serves the existing LV-Lab website (SMU + NUS pages and all static assets) using FastAPI.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
uvicorn lab_fastapi.main:app --host 0.0.0.0 --port 8080 --reload
```

Then open:

- `http://127.0.0.1:8080/` (SMU homepage)
- `http://127.0.0.1:8080/SMU/`
- `http://127.0.0.1:8080/nus/`
- `http://127.0.0.1:8080/SMU/gpu-monitor.html`

## Production command

```bash
uvicorn lab_fastapi.main:app --host 0.0.0.0 --port 8080
```
