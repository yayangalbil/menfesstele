import os
import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Text,
                         Boolean, DateTime)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///menfess.db")
# Railway/Postgres kasih URL format "postgresql://...", tapi kita pakai driver
# pg8000 (pure Python, nggak perlu compile) jadi perlu diubah jadi
# "postgresql+pg8000://...".
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

WORKER_NAMES = ["Amela", "Berline", "Geya", "Shazald", "Bear", "Abillo"]


class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.datetime.utcnow)
    text = Column(Text)


class Wording(Base):
    __tablename__ = "wording"
    slot = Column(Integer, primary_key=True)  # 1..5
    text = Column(Text, default="")


class KeywordOverride(Base):
    __tablename__ = "keyword_overrides"
    id = Column(Integer, primary_key=True)
    keyword = Column(String, unique=True)


class WorkerState(Base):
    __tablename__ = "worker_state"
    name = Column(String, primary_key=True)
    on = Column(Boolean, default=True)


class SystemState(Base):
    __tablename__ = "system_state"
    id = Column(Integer, primary_key=True, default=1)
    on = Column(Boolean, default=True)


# menfess yang udah pernah kena command apa aja, biar nggak double-kirim command sama
class CommandLog(Base):
    __tablename__ = "command_log"
    id = Column(Integer, primary_key=True)
    menfess_key = Column(String, index=True)  # f"{base}:{message_id}"
    command = Column(String)
    ts = Column(DateTime, default=datetime.datetime.utcnow)


def init_db():
    Base.metadata.create_all(engine)
    with SessionLocal() as s:
        for name in WORKER_NAMES:
            if not s.get(WorkerState, name):
                s.add(WorkerState(name=name, on=True))
        if not s.get(SystemState, 1):
            s.add(SystemState(id=1, on=True))
        for slot in range(1, 6):
            if not s.get(Wording, slot):
                s.add(Wording(slot=slot, text=""))
        s.commit()


def log(text: str):
    with SessionLocal() as s:
        s.add(LogEntry(text=text))
        # keep table small - trim old rows past 500
        count = s.query(LogEntry).count()
        if count > 500:
            oldest = (s.query(LogEntry).order_by(LogEntry.ts.asc())
                      .limit(count - 500).all())
            for row in oldest:
                s.delete(row)
        s.commit()


def worker_is_on(name: str) -> bool:
    with SessionLocal() as s:
        row = s.get(WorkerState, name)
        return row.on if row else True


def system_is_on() -> bool:
    with SessionLocal() as s:
        row = s.get(SystemState, 1)
        return row.on if row else True


def get_wording(slot: int) -> str:
    with SessionLocal() as s:
        row = s.get(Wording, slot)
        return row.text if row else ""


def already_sent(menfess_key: str, command: str) -> bool:
    with SessionLocal() as s:
        return s.query(CommandLog).filter_by(
            menfess_key=menfess_key, command=command).first() is not None


def mark_sent(menfess_key: str, command: str):
    with SessionLocal() as s:
        s.add(CommandLog(menfess_key=menfess_key, command=command))
        s.commit()
