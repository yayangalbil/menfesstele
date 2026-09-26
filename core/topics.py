"""
Auto-matching topic_id di grup WTB! berdasarkan nama topic, tanpa hardcode ID.
Nama topic di Telegram cuma perlu MENGANDUNG nama kategori (case-insensitive) -
emoji/simbol tambahan ("♡", "🐾", dst di judul topic) nggak masalah.
"""
from telethon.tl.functions.channels import GetForumTopicsRequest
from core.keywords import CATEGORIES

SPECIAL_TOPIC = "JOCKEY & MONEY"


def parse_chat_id(value: str):
    """Env var selalu string. Kalau isinya angka (boleh minus di depan,
    format ID grup Telegram), ubah jadi int biar Telethon treat sebagai
    Peer ID, bukan nyoba resolve sebagai username."""
    value = value.strip()
    if value.lstrip("-").isdigit():
        return int(value)
    return value.lstrip("@")


async def fetch_topic_map(client, wtb_group):
    """Return dict: category_name -> topic_id (thread id untuk reply_to)."""
    # Perlu ini dulu supaya Telethon punya cache entity kalau wtb_group
    # dikasih dalam bentuk ID mentah (bukan username) - Telethon cuma bisa
    # resolve ID kalau entity-nya udah pernah "ketemu" (misal lewat dialog).
    await client.get_dialogs()
    entity = await client.get_entity(parse_chat_id(wtb_group))
    result = await client(GetForumTopicsRequest(
        channel=entity, offset_date=None, offset_id=0, offset_topic=0, limit=100,
    ))
    topic_map = {}
    wanted = list(CATEGORIES.keys()) + [SPECIAL_TOPIC]
    for topic in result.topics:
        title = getattr(topic, "title", "") or ""
        low = title.lower()
        for name in wanted:
            if name.lower() in low:
                topic_map[name] = topic.id
                break
    return topic_map
