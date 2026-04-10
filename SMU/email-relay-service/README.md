# GPU Email Relay Service (Windows sender)

This service is for the machine that **can send email** but cannot access full GPU data directly.

It polls `10.193.104.165` for internal alert candidates and sends email from this machine.

## 1) Configure source server (10.193.104.165)

In `SMU/gpu-monitor-backend/.env` on 10.193.104.165, set:

```env
INTERNAL_API_TOKEN=<a-long-random-token>
```

Restart the GPU monitor backend so `/api/internal/alert-candidates` is available.

## 2) Configure this relay service

```bash
cd SMU/email-relay-service
python -m venv .venv
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows cmd
# or: cp .env.example .env
```

Edit `.env` and set:
- `SOURCE_BASE_URL` to `http://10.193.104.165:8080`
- `SOURCE_INTERNAL_TOKEN` to same token as source server
- SMTP credentials for this sender machine

## 3) Run

```bash
uvicorn app:app --host 0.0.0.0 --port 8090
```

Manual trigger:

```bash
curl -X POST http://127.0.0.1:8090/run-once
```

Health check:

```bash
curl http://127.0.0.1:8090/healthz
```

## Test (Windows relay send logic)

```bash
python -m unittest test_relay.py -v
```
