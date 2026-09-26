import os
import re
from telethon import events
from core import db
from core.executor import execute_command
from core.topics import parse_chat_id

WTB_GROUP = os.environ["WTB_GROUP"]
COMMAND_RE = re.compile(r"^\s*r([1-4])\s*$", re.IGNORECASE)

# command -> daftar akun yang eksekusi
COMMAND_ACCOUNTS = {
    "1": ["Geya", "Shazald", "Bear", "Abillo"],
    "2": ["Geya", "Shazald", "Bear", "Abillo"],
    "3": ["Geya", "Shazald", "Bear", "Abillo"],
    "4": ["Berline"],
}


async def run_command_listener(berline_client, executor_clients):
    """
    berline_client: Telethon client logged in sebagai Berline, listen di grup WTB!.
    executor_clients: dict nama_akun -> TelegramClient (Geya, Shazald, Bear, Abillo, Berline).
    """
    # Wajib panggil get_dialogs() dulu biar Telethon bisa resolve WTB_GROUP
    # kalau dikasih dalam bentuk ID mentah (bukan username) - sama kaya
    # masalah yang kejadian di topics.py sebelumnya.
    await berline_client.get_dialogs()
    wtb_id = parse_chat_id(WTB_GROUP)

    @berline_client.on(events.NewMessage(chats=wtb_id))
    async def handler(event):
        if not event.is_reply:
            return
        m = COMMAND_RE.match(event.raw_text or "")
        if not m:
            return
        if not db.system_is_on():
            await event.reply("⚠️ Sistem sedang dimatikan dari dashboard.")
            return

        command = m.group(1)
        target = await event.get_reply_message()
        fwd = getattr(target, "fwd_from", None)
        if not fwd or not getattr(fwd, "channel_post", None):
            await event.edit(event.raw_text + "\n\n⚠️ Nggak bisa nemuin menfess aslinya.")
            return

        source_msg_id = fwd.channel_post
        source_peer = fwd.from_id  # PeerChannel milik base asli
        menfess_key = f"{source_peer}:{source_msg_id}"

        if db.already_sent(menfess_key, command):
            await event.edit(event.raw_text + "\n\n⚠️ Command R{} sudah pernah dipakai di menfess ini.".format(command))
            return

        accounts = COMMAND_ACCOUNTS[command]
        wording = db.get_wording(int(command))

        status_lines = await execute_command(
            executor_clients, accounts, source_peer, source_msg_id, wording,
        )
        db.mark_sent(menfess_key, command)

        summary = "MENFESS TERKIRIM OLEH SEMUA AKUN" if all(
            "✓" in line for line in status_lines
        ) else "MENFESS TERKIRIM (sebagian)"
        report = event.raw_text + "\n\n" + summary + "\n" + "\n".join(status_lines)
        await event.edit(report)
        db.log(f"command R{command} -> {menfess_key}: {summary}")
