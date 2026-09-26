import os
from telethon import events
from core.keywords import match_category
from core.topics import fetch_topic_map, parse_chat_id, SPECIAL_TOPIC
from core import db

WTB_GROUP = os.environ["WTB_GROUP"]
SOURCE_BASES = [b.strip() for b in os.environ["SOURCE_BASES"].split(",") if b.strip()]
JOCKEY_BASE = os.environ.get("JOCKEY_BASE", "jockeyfess").lower().lstrip("@")
MONEY_BASE = os.environ.get("MONEY_BASE", "moneyfess").lower().lstrip("@")


async def run_monitor(client):
    """client = Telethon client logged in as Amela."""
    topic_map = await fetch_topic_map(client, WTB_GROUP)
    wtb_entity = await client.get_entity(parse_chat_id(WTB_GROUP))

    for base in SOURCE_BASES:
        try:
            ent = await client.get_entity(base)
            db.log(f"DEBUG: Amela resolve @{base} -> OK (id={ent.id})")
        except Exception as e:
            db.log(f"DEBUG: Amela GAGAL resolve @{base}: {e}")

    @client.on(events.NewMessage(chats=SOURCE_BASES))
    async def handler(event):
        base_username = (event.chat.username or "").lower()
        db.log(f"DEBUG: pesan masuk dari @{base_username or '?'} "
               f"(chat_id={event.chat_id}) #{event.message.id}")

        if not db.system_is_on() or not db.worker_is_on("Amela"):
            return
        text = event.raw_text or ""
        if not text.strip():
            return

        # logic khusus JOCKEY & MONEY
        if base_username == JOCKEY_BASE:
            target_topic = SPECIAL_TOPIC
        elif base_username == MONEY_BASE:
            cat, _kw = match_category(text)
            target_topic = SPECIAL_TOPIC if cat else None
        else:
            cat, _kw = match_category(text)
            target_topic = cat

        if not target_topic:
            return

        topic_id = topic_map.get(target_topic)
        if topic_id is None:
            db.log(f"WARNING: topic '{target_topic}' belum ketemu di WTB!, skip.")
            return

        _cat, kw = match_category(text)
        forwarded = await client.forward_messages(
            wtb_entity, event.message, reply_to=topic_id,
        )
        # simpan mapping supaya command handler bisa nemuin menfess asli
        menfess_key = f"{base_username}:{event.message.id}"
        db.log(f"@{base_username} #{event.message.id} -> {target_topic}"
               + (f"; keyword: {kw}" if kw else "; unfiltered (jockeyfess)"))
        return forwarded
