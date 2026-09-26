import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import select
from core import db
from core.keywords import all_keywords_flat

app = FastAPI(title="Berline's Menfess Control API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup():
    db.init_db()


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))


@app.get("/api/workers")
def get_workers():
    with db.SessionLocal() as s:
        rows = s.query(db.WorkerState).all()
        return {r.name: r.on for r in rows}


class ToggleBody(BaseModel):
    on: bool


@app.post("/api/workers/{name}/toggle")
def toggle_worker(name: str, body: ToggleBody):
    with db.SessionLocal() as s:
        row = s.get(db.WorkerState, name)
        if row:
            row.on = body.on
            s.commit()
    db.log(f"dashboard: worker {name} -> {'ON' if body.on else 'OFF'}")
    return {"ok": True}


@app.get("/api/system")
def get_system():
    return {"on": db.system_is_on()}


@app.post("/api/system/toggle")
def toggle_system(body: ToggleBody):
    with db.SessionLocal() as s:
        row = s.get(db.SystemState, 1)
        row.on = body.on
        s.commit()
    db.log(f"dashboard: sistem -> {'ON' if body.on else 'OFF'}")
    return {"ok": True}


@app.get("/api/wording")
def get_all_wording():
    with db.SessionLocal() as s:
        rows = s.query(db.Wording).order_by(db.Wording.slot).all()
        return {r.slot: r.text for r in rows}


class WordingBody(BaseModel):
    text: str


@app.post("/api/wording/{slot}")
def save_wording(slot: int, body: WordingBody):
    with db.SessionLocal() as s:
        row = s.get(db.Wording, slot)
        row.text = body.text
        s.commit()
    db.log(f"dashboard: wording {slot} diperbarui")
    return {"ok": True}


@app.get("/api/keywords")
def get_keywords():
    with db.SessionLocal() as s:
        overrides = [r.keyword for r in s.query(db.KeywordOverride).all()]
    return {"keywords": overrides or all_keywords_flat()}


class KeywordsBody(BaseModel):
    keywords: list[str]


@app.post("/api/keywords")
def save_keywords(body: KeywordsBody):
    with db.SessionLocal() as s:
        s.query(db.KeywordOverride).delete()
        for kw in body.keywords:
            s.add(db.KeywordOverride(keyword=kw.strip()))
        s.commit()
    db.log("dashboard: keywords diperbarui")
    return {"ok": True}


@app.get("/api/logs")
def get_logs(limit: int = 50):
    with db.SessionLocal() as s:
        rows = (s.query(db.LogEntry)
                .order_by(db.LogEntry.ts.desc()).limit(limit).all())
        return [{"ts": r.ts.isoformat(), "text": r.text} for r in reversed(rows)]
