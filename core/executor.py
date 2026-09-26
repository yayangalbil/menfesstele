import asyncio
import random
from telethon.errors import FloodWaitError
from core import db


async def _send_one(client, name, source_peer, source_msg_id, wording):
    if not db.worker_is_on(name):
        return f"{name}: dimatikan (skip)"

    delay = random.uniform(0.5, 2.0)
    await asyncio.sleep(delay)

    try:
        await client.send_message(
            source_peer, wording, reply_to=source_msg_id,
        )
        return f"{name}: ✓ berhasil kirim"
    except FloodWaitError as e:
        db.log(f"{name}: FLOODWAIT {e.seconds}s — coba lagi setelah selesai")
        await asyncio.sleep(e.seconds)
        try:
            await client.send_message(
                source_peer, wording, reply_to=source_msg_id,
            )
            return f"{name}: ✓ berhasil kirim (setelah floodwait {e.seconds}s)"
        except Exception as e2:
            return f"{name}: ✗ gagal setelah retry ({e2})"
    except Exception as e:
        return f"{name}: ✗ gagal ({e})"


async def execute_command(executor_clients, accounts, source_peer, source_msg_id, wording):
    tasks = [
        _send_one(executor_clients[name], name, source_peer, source_msg_id, wording)
        for name in accounts if name in executor_clients
    ]
    return await asyncio.gather(*tasks)
