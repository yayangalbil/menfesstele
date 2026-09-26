"""
Jalanin ini SEKALI per akun (di laptop kamu, bukan di Railway), buat generate
session string. Nanti string yang keluar tinggal copy ke .env / Railway env var
(SESSION_AMELA, SESSION_BERLINE, dst).

Cara pakai:
    python accounts/generate_session.py

Nanti diminta login: nomor HP -> kode OTP yang masuk ke Telegram -> (2FA
password kalau aktif). Session string dicetak di akhir, jangan di-share ke
siapa pun karena setara password akun.
"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(input("API_ID (dari akun Amela di my.telegram.org): "))
API_HASH = input("API_HASH: ").strip()


async def main():
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        me = await client.get_me()
        print(f"\nLogin sukses sebagai: {me.first_name} (@{me.username})")
        print("\n=== SESSION STRING (simpan ke .env, JANGAN di-share) ===")
        print(client.session.save())


asyncio.run(main())
