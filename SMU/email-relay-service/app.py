from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import smtplib
from contextlib import closing
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings, SettingsConfigDict


class RelaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    source_base_url: str = 'http://10.193.104.165:8080'
    source_internal_token: str = ''
    poll_interval_minutes: int = 10
    state_db_path: str = './relay_state.db'

    smtp_host: str = ''
    smtp_port: int = 587
    smtp_username: str = ''
    smtp_password: str = ''
    smtp_from_email: str = ''
    smtp_use_tls: bool = True


settings = RelaySettings()
scheduler = BackgroundScheduler(timezone='UTC')
DB_PATH = Path(settings.state_db_path).resolve()


def _ensure_state_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS sent_events ('
            ' event_key TEXT PRIMARY KEY,'
            ' sent_at TEXT NOT NULL'
            ')'
        )
        conn.commit()


def _event_key(item: dict) -> str:
    raw = '|'.join(
        [
            item.get('host_address', ''),
            item.get('username', ''),
            item.get('event_type', ''),
            item.get('reason', ''),
        ]
    )
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _already_sent(event_key: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute('SELECT 1 FROM sent_events WHERE event_key = ?', (event_key,)).fetchone()
    return row is not None


def _mark_sent(event_key: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            'INSERT OR REPLACE INTO sent_events(event_key, sent_at) VALUES(?, ?)',
            (event_key, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()


def _fetch_candidates() -> list[dict]:
    endpoint = settings.source_base_url.rstrip('/') + '/api/internal/alert-candidates'
    req = Request(endpoint, headers={'X-Internal-Token': settings.source_internal_token})
    with closing(urlopen(req, timeout=15)) as resp:  # nosec B310 - internal trusted endpoint by design
        payload = json.loads(resp.read().decode('utf-8'))
    return payload.get('candidates', [])


def _send_email(to_email: str, subject: str, body: str, cc_email: str | None = None) -> None:
    if not settings.smtp_host:
        raise RuntimeError('SMTP is not configured for relay service.')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.smtp_from_email or settings.smtp_username
    msg['To'] = to_email
    if cc_email:
        msg['Cc'] = cc_email
    msg.set_content(body)

    recipients = [to_email] + ([cc_email] if cc_email else [])
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg, from_addr=msg['From'], to_addrs=recipients)


def run_once() -> dict[str, int]:
    candidates = _fetch_candidates()
    sent = 0
    skipped = 0
    for item in candidates:
        key = _event_key(item)
        if _already_sent(key):
            skipped += 1
            continue

        subject = f"[{item.get('host_name')}/{item.get('host_address')}] GPU usage action required - {item.get('event_type')}"
        body = (
            f"Hello {item.get('username')},\n\n"
            f"This alert was triggered on host {item.get('host_name')} ({item.get('host_address')}).\n"
            f"Reason:\n- {item.get('reason')}\n"
        )
        _send_email(item['email'], subject, body, cc_email=item.get('cc_email') or None)
        _mark_sent(key)
        sent += 1

    return {'candidates': len(candidates), 'sent': sent, 'skipped': skipped}


app = FastAPI(title='GPU Alert Relay (Windows Sender)')


@app.on_event('startup')
def on_startup() -> None:
    _ensure_state_db()
    scheduler.add_job(run_once, 'interval', minutes=max(settings.poll_interval_minutes, 1), id='relay-poll', replace_existing=True)
    scheduler.start()


@app.on_event('shutdown')
def on_shutdown() -> None:
    scheduler.shutdown(wait=False)


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok', 'db_path': str(DB_PATH)}


@app.post('/run-once')
def api_run_once() -> dict[str, int]:
    try:
        return run_once()
    except (HTTPError, URLError) as exc:
        raise HTTPException(status_code=502, detail=f'Failed to query source server: {exc}') from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('app:app', host='0.0.0.0', port=int(os.getenv('PORT', '8090')))
