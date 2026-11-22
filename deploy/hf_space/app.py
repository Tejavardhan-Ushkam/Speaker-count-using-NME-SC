"""Speaker-count web API (FastAPI) for a Hugging Face Docker Space.

GET  /         -> minimal built-in upload page (works even without the Lovable front-end)
GET  /health   -> {"status": "ready" | "loading", ...}
GET  /model    -> model description, settings and measured accuracy
POST /predict  -> multipart form field "file" (any audio/video ffmpeg reads) -> JSON result
"""

from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_in_threadpool

from speakercount.infer import SpeakerCounter

MAX_MB = float(os.environ.get("MAX_UPLOAD_MB", "100"))
MAX_SEC = float(os.environ.get("MAX_AUDIO_SEC", "1800"))  # 30 min: CPU time stays a few minutes

app = FastAPI(title="Speaker Count API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST", "OPTIONS"],
                   allow_headers=["*"])

_state = {"counter": None, "error": None, "started": time.time()}
_lock = threading.Lock()  # one analysis at a time on a 2-vCPU machine


def _load():
    try:
        c = SpeakerCounter("deploy/model.yaml")
        c.warmup()
        _state["counter"] = c
    except Exception as e:  # noqa: BLE001 - reported by /health
        _state["error"] = f"{type(e).__name__}: {e}"


threading.Thread(target=_load, daemon=True).start()


def _counter() -> SpeakerCounter:
    if _state["counter"] is None:
        if _state["error"]:
            raise HTTPException(500, f"model failed to load: {_state['error']}")
        raise HTTPException(503, "model is still loading, try again in a minute")
    return _state["counter"]


def _run(counter: SpeakerCounter, src: Path) -> dict:
    if not _lock.acquire(timeout=600):
        raise HTTPException(429, "server is busy with another file, try again shortly")
    try:
        return counter.predict(src, max_sec=MAX_SEC)
    except ValueError as e:  # undecodable / too long
        raise HTTPException(422, str(e)) from e
    finally:
        _lock.release()


@app.get("/health")
def health():
    status = "ready" if _state["counter"] else ("error" if _state["error"] else "loading")
    return {"status": status, "error": _state["error"], "uptime_sec": round(time.time() - _state["started"]),
            "busy": _lock.locked(), "max_upload_mb": MAX_MB, "max_audio_min": MAX_SEC / 60}


@app.get("/model")
def model():
    return _counter().info()


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    counter = _counter()
    suffix = Path(file.filename or "audio").suffix[:10] or ".bin"
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"upload{suffix}"
        size = 0
        with open(src, "wb") as f:
            while chunk := await file.read(1 << 20):
                size += len(chunk)
                if size > MAX_MB * 1e6:
                    raise HTTPException(413, f"file is larger than {MAX_MB:.0f} MB")
                f.write(chunk)
        if size == 0:
            raise HTTPException(400, "empty file")
        result = await run_in_threadpool(_run, counter, src)  # keeps /health responsive meanwhile
    result["filename"] = file.filename
    return result


PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Speaker Count API</title><style>body{font-family:system-ui,sans-serif;max-width:640px;margin:40px auto;padding:0 16px}
pre{background:#f4f4f4;padding:12px;overflow:auto;max-height:420px}</style></head><body>
<h1>Speaker Count API</h1><p>Upload an audio file to count its speakers. (Back-end test page; the main site is the Lovable app.)</p>
<p id="h">Checking server...</p><input type="file" id="f" accept="audio/*,video/*"> <button onclick="go()">Count speakers</button>
<h2 id="k"></h2><pre id="o"></pre><script>
fetch('health').then(r=>r.json()).then(j=>h.textContent='Server: '+j.status);
async function go(){const x=f.files[0];if(!x)return;k.textContent='Analysing...';o.textContent='';
const d=new FormData();d.append('file',x);const r=await fetch('predict',{method:'POST',body:d});const j=await r.json();
k.textContent=r.ok?('Speakers: '+j.num_speakers):('Error: '+j.detail);o.textContent=JSON.stringify(j,null,2);}
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE
