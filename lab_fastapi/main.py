from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(title='LV-Lab Site')

# Shared static assets
app.mount('/assets', StaticFiles(directory=ROOT / 'assets'), name='assets')
app.mount('/css', StaticFiles(directory=ROOT / 'css'), name='css')
app.mount('/js', StaticFiles(directory=ROOT / 'js'), name='js')
app.mount('/images', StaticFiles(directory=ROOT / 'images'), name='images')
app.mount('/fonts', StaticFiles(directory=ROOT / 'fonts'), name='fonts')

# Campus site sections
app.mount('/SMU', StaticFiles(directory=ROOT / 'SMU', html=True), name='smu')
app.mount('/nus', StaticFiles(directory=ROOT / 'nus', html=True), name='nus')


@app.get('/healthz')
def healthz() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/')
def smu_home() -> FileResponse:
    return FileResponse(ROOT / 'SMU' / 'index.html')


@app.get('/index.html')
def root_index() -> FileResponse:
    return FileResponse(ROOT / 'SMU' / 'index.html')


@app.get('/history_lv_lab.html')
def history_page() -> FileResponse:
    return FileResponse(ROOT / 'history_lv_lab.html')


@app.get('/favicon.ico')
def favicon() -> FileResponse:
    return FileResponse(ROOT / 'favicon.ico')


@app.get('/site.webmanifest')
def site_manifest() -> FileResponse:
    return FileResponse(ROOT / 'site.webmanifest')


@app.get('/apple-touch-icon.png')
def apple_touch_icon() -> FileResponse:
    return FileResponse(ROOT / 'apple-touch-icon.png')


@app.get('/favicon-32x32.png')
def favicon_32() -> FileResponse:
    return FileResponse(ROOT / 'favicon-32x32.png')


@app.get('/android-chrome-192x192.png')
def android_icon_192() -> FileResponse:
    return FileResponse(ROOT / 'android-chrome-192x192.png')


@app.get('/android-chrome-512x512.png')
def android_icon_512() -> FileResponse:
    return FileResponse(ROOT / 'android-chrome-512x512.png')
