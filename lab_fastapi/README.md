# LV-Lab Unified FastAPI Runner

This entrypoint runs **one FastAPI service** that includes:

- the original LV-Lab pages (SMU + NUS),
- the GPU monitor page UI,
- the GPU monitor backend APIs (`/api/*`) and session logic.

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
- `http://127.0.0.1:8080/SMU/gpu-monitor.html` (GPU monitor UI)
- `http://127.0.0.1:8080/gpu-monitor` (GPU monitor shortcut route)
- `http://127.0.0.1:8080/api/session` (GPU monitor backend API)

## Production command

```bash
uvicorn lab_fastapi.main:app --host 0.0.0.0 --port 8080
```

## Public access (non-localhost)

Use this command so other machines can access it:

```bash
uvicorn lab_fastapi.main:app --host 0.0.0.0 --port 8080
```

Then open from another machine using your server IP/DNS, for example:

```text
http://<your-server-public-ip>:8080/
```
