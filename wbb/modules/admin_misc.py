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
import os

from pyrogram import filters

from wbb import app
from wbb.core.decorators.permissions import adminsOnly

__MODULE__ = "ئەدمین (هەمەڕەنگ)"
__HELP__ = """
/set_chat_title - گۆڕینی ناوی گرووپ/کەناڵ.
/set_chat_photo - گۆڕینی وێنەی پرۆفایلی گرووپ/کەناڵ.
/set_user_title - گۆڕینی نازناوی ئەدمینێک.
"""


@app.on_message(filters.command("set_chat_title") & ~filters.private)
@adminsOnly("can_change_info")
async def set_chat_title(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**شێوازی بەکارهێنان:**\n/set_chat_title ناوی نوێ")
    old_title = message.chat.title
    new_title = message.text.split(None, 1)[1]
    await message.chat.set_title(new_title)
    await message.reply_text(
        f"بە سەرکەوتوویی ناوی گرووپ گۆڕدرا لە {old_title} بۆ {new_title}"
    )


@app.on_message(filters.command("set_user_title") & ~filters.private)
@adminsOnly("can_change_info")
async def set_user_title(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "ڕیپلای نامەی بەکارهێنەرێک بکە بۆ دانانی نازناوی ئەدمین بۆی"
        )
    if not message.reply_to_message.from_user:
        return await message.reply_text(
            "ناتوانم نازناوی ئەدمین بۆ کەسێکی نەناسراو بگۆڕم"
        )
    chat_id = message.chat.id
    from_user = message.reply_to_message.from_user
    if len(message.command) < 2:
        return await message.reply_text(
            "**شێوازی بەکارهێنان:**\n/set_user_title نازناوی نوێی ئەدمین"
        )
    title = message.text.split(None, 1)[1]
    await app.set_administrator_title(chat_id, from_user.id, title)
    await message.reply_text(
        f"بە سەرکەوتوویی نازناوی ئەدمینی {from_user.mention} گۆڕدرا بۆ {title}"
    )


@app.on_message(filters.command("set_chat_photo") & ~filters.private)
@adminsOnly("can_change_info")
async def set_chat_photo(_, message):
    reply = message.reply_to_message

    if not reply:
        return await message.reply_text(
            "ڕیپلای وێنەیەک بکە بۆ ئەوەی بیکەم بە وێنەی گرووپ"
        )

    file = reply.document or reply.photo
    if not file:
        return await message.reply_text(
            "ڕیپلای وێنەیەک یان فایلێک بکە بۆ ئەوەی بیکەم بە وێنەی گرووپ"
        )

    if file.file_size > 5000000:
        return await message.reply("قەبارەی فایلەکە زۆر گەورەیە.")

    photo = await reply.download()
    await message.chat.set_photo(photo)
    await message.reply_text("بە سەرکەوتوویی وێنەی گرووپ گۆڕدرا")
    os.remove(photo)
