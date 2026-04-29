"""
MIT License

Copyright (c) 2024 TheHamkerCat
"""
import asyncio
import time
import os
from inspect import getfullargspec
from os import path
from pathlib import Path

from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from Python_ARQ import ARQ
from telegraph import Telegraph

is_config = path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

Path("sessions").mkdir(exist_ok=True)

USERBOT_PREFIX = USERBOT_PREFIX
GBAN_LOG_GROUP_ID = GBAN_LOG_GROUP_ID
WELCOME_DELAY_KICK_SEC = WELCOME_DELAY_KICK_SEC
LOG_GROUP_ID = LOG_GROUP_ID
MESSAGE_DUMP_CHAT = MESSAGE_DUMP_CHAT
MOD_LOAD = []
MOD_NOLOAD = []
SUDOERS = filters.user()
bot_start_time = time.time()


class Log:
    def __init__(self, save_to_file=False, file_name="wbb.log"):
        self.save_to_file = save_to_file
        self.file_name = file_name

    def info(self, msg):
        print(f"[+]: {msg}")
        if self.save_to_file:
            with open(self.file_name, "a") as f:
                f.write(f"[INFO]({time.ctime(time.time())}): {msg}\n")

    def error(self, msg):
        print(f"[-]: {msg}")
        if self.save_to_file:
            with open(self.file_name, "a") as f:
                f.write(f"[ERROR]({time.ctime(time.time())}): {msg}\n")


log = Log(True, "bot.log")

# MongoDB client
log.info("Initializing MongoDB client")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.wbb


async def load_sudoers():
    global SUDOERS
    log.info("Loading sudoers")
    sudoersdb = db.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    for user_id in SUDO_USERS_ID:
        SUDOERS.add(user_id)
        if user_id not in sudoers:
            sudoers.append(user_id)
            await sudoersdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"sudoers": sudoers}},
                upsert=True,
            )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)


loop = asyncio.get_event_loop()
loop.run_until_complete(load_sudoers())

# فێڵێکی زیرەک بۆ خوێندنەوەی کلیلەکە بە هەر ناوێک بێت
SESSION = os.environ.get("SESSION_STRING") or os.environ.get("STRING_SESSION") or (SESSION_STRING if 'SESSION_STRING' in locals() else None)

if not SESSION or SESSION.strip() == "":
    log.info("SESSION_STRING missing, userbot client will be skipped.")
    app2 = None
else:
    app2 = Client(
        name="sessions/userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION,
        in_memory=True,
    )

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)
app = Client("sessions/wbb", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

log.info("Starting bot client")
app.start()

# پێناسەکردنی نرخەکان بۆ ئەوەی ئەگەر ئاسیستانت نەبوو، بۆتەکە کراش نەکات
USERBOT_ID = 0
USERBOT_NAME = "None"
USERBOT_USERNAME = "None"
USERBOT_MENTION = "None"
USERBOT_DC_ID = 0

if app2:
    try:
        log.info("Starting userbot client")
        app2.start()
        log.info("Gathering profile info for assistant")
        y = app2.get_me()
        USERBOT_ID = y.id
        USERBOT_NAME = y.first_name + (y.last_name or "")
        USERBOT_USERNAME = y.username
        USERBOT_MENTION = y.mention
        USERBOT_DC_ID = y.dc_id
        if USERBOT_ID not in SUDOERS:
            SUDOERS.add(USERBOT_ID)
    except Exception as e:
        log.error(f"Userbot failed to start: {e}. Bot will run without assistant.")
        app2 = None

log.info("Gathering profile info for bot")
x = app.get_me()
BOT_ID = x.id
BOT_NAME = x.first_name + (x.last_name or "")
BOT_USERNAME = x.username
BOT_MENTION = x.mention
BOT_DC_ID = x.dc_id

log.info("Initializing Telegraph client")
telegraph = Telegraph(domain="graph.org")
telegraph.create_account(short_name=BOT_USERNAME)


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})
