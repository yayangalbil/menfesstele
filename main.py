import os
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

from core import db
from core.monitor import run_monitor
from core.commands import run_command_listener

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]

ACCOUNTS = ["AMELA", "BERLINE", "GEYA", "SHAZALD", "BEAR", "ABILLO"]


def make_client(name: str) -> TelegramClient:
    session = os.environ[f"SESSION_{name}"]
    return TelegramClient(StringSession(session), API_ID, API_HASH)


async def main():
    db.init_db()
    db.log("Sistem starting...")

    clients = {name.capitalize(): make_client(name) for name in ACCOUNTS}
    for name, client in clients.items():
        await client.start()
        db.log(f"{name}: connected")

    amela = clients["Amela"]
    berline = clients["Berline"]
    executor_clients = {n: c for n, c in clients.items() if n != "Amela"}

    await run_monitor(amela)
    await run_command_listener(berline, executor_clients)

    db.log("Semua worker siap. Listening...")
    await asyncio.gather(*[c.run_until_disconnected() for c in clients.values()])


if __name__ == "__main__":
    asyncio.run(main())
