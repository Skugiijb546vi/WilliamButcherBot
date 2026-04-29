"""
MIT License

Copyright (c) 2024 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    blacklist_chat,
    blacklisted_chats,
    whitelist_chat,
)

__MODULE__ = "قەدەغەکردنی گرووپ"
__HELP__ = """
**ئەم مۆدیوڵە تەنها بۆ خاوەنی بۆتەکەیە (ئەدمینە باڵاکان)**

ئەم مۆدیوڵە بەکاربهێنە بۆ ئەوەی بۆتەکە لەو گرووپانە دەربچێت و کار نەکات کە تۆ ناتەوێت تێیاندا بێت.

/blacklist_chat [ئایدی_گرووپ] - قەدەغەکردنی گرووپێک.
/whitelist_chat [ئایدی_گرووپ] - لابردنی قەدەغەکردن لەسەر گرووپێک.
/blacklisted_chats - پیشاندانی ئەو گرووپانەی قەدەغەکراون.
"""


@app.on_message(filters.command("blacklist_chat") & SUDOERS)
@capture_err
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**شێوازی بەکارهێنان:**\n/blacklist_chat [ئایدی_گرووپ]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("ئەم گرووپە پێشتر قەدەغە کراوە.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            "بە سەرکەوتوویی گرووپەکە قەدەغە کرا و خرایە لیستی ڕەشەوە"
        )
    await message.reply_text("هەڵەیەک ڕوویدا، تکایە سەیری لۆگەکان بکە.")


@app.on_message(filters.command("whitelist_chat") & SUDOERS)
@capture_err
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**شێوازی بەکارهێنان:**\n/whitelist_chat [ئایدی_گرووپ]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("ئەم گرووپە پێشتر لە لیستی قەدەغەکراوەکان دەرهێنراوە (ڕێگەپێدراوە).")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            "بە سەرکەوتوویی قەدەغەکردن لەسەر ئەم گرووپە لابرا"
        )
    await message.reply_text("هەڵەیەک ڕوویدا، تکایە سەیری لۆگەکان بکە.")


@app.on_message(filters.command("blacklisted_chats") & SUDOERS)
@capture_err
async def blacklisted_chats_func(_, message: Message):
    text = ""
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "تایبەت (Private)"
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if text == "":
        return await message.reply_text("هیچ گرووپێکی قەدەغەکراو نەدۆزرایەوە.")
    await message.reply_text(text)
