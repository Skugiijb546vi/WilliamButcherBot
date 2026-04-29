from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, USERBOT_PREFIX, app, app2

__MODULE__ = "زار"
__HELP__ = """
/dice
    هاویشتنی زارێک.
    (ئەگەر ئەدمینی باڵا بیت، هەمیشە ژمارە ٦ت بۆ دەردەچێت!)
"""


@app2.on_message(
    filters.command("dice", prefixes=USERBOT_PREFIX)
    & SUDOERS
    & ~filters.forwarded
    & ~filters.via_bot
)
@app.on_message(filters.command("dice"))
async def throw_dice(client, message: Message):
    # پشکنین بۆ ئەوەی بزانین نێرەرەکە ئەدمینی باڵایە یان نا
    six = (message.from_user.id in SUDOERS) if message.from_user else False

    c = message.chat.id
    if not six:
        # بۆ بەکارهێنەری ئاسایی، تەنها یەک زار بهاوێژە
        return await client.send_dice(c, "🎲")

    # بۆ ئەدمینی باڵا، ئەوەندە بهاوێژە تا ٦ دەردەچێت
    m = await client.send_dice(c, "🎲")

    while m.dice.value != 6:
        await m.delete()
        m = await client.send_dice(c, "🎲")
