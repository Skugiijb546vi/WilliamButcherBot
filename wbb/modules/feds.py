"""
MIT License

Copyright (c) 2024 SI_NN_ER_LS 

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

import asyncio
import uuid
import html

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import FloodWait, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from wbb import BOT_ID, LOG_GROUP_ID, SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfeds import *
from wbb.utils.functions import extract_user, extract_user_and_reason

__MODULE__ = "فیدراسیۆن"
__HELP__ = """
هەموو شتێک خۆشە تا ئەو کاتەی سپامەرێک دێتە ناو گرووپەکەتەوە و دەبێت باندی بکەیت. دواتر دەبێت لە گرووپەکانی تریش باندی بکەیت و ئەمەش کاتێکی زۆرت لێ دەبات.
بەڵام کاتێک چەندین گرووپت هەیە، ناتەوێت ئەم سپامەرە لە هیچ کامیاندا بێت - چۆن چارەسەری دەکەیت؟ ئایا دەبێت بە دەستی لە هەموو گرووپەکان باندی بکەیت؟\n
**ئیتر نا!** بە فیدراسیۆن (Federation)، دەتوانیت باندێک لە یەک گرووپدا بکەیت و لە هەموو گرووپەکانی تردا جێبەجێ ببێت.\n
تەنانەت دەتوانیت ئەدمینی فیدراسیۆن دیاری بکەیت، بۆ ئەوەی ئەدمینە جێگەی متمانەکانت بتوانن سپامەرەکان لە هەموو ئەو گرووپانە باند بکەن کە دەتەوێت بییانپارێزیت.\n\n
"""


SUPPORT_CHAT = "@WBBSupport"


@app.on_message(filters.command("newfed"))
@capture_err
async def new_fed(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "دروستکردنی فیدراسیۆن تەنها لە ڕێگەی نامەی تایبەت (PV) بۆ من دەبێت."
        )

    if len(message.command) < 2:
        return await message.reply_text("تکایە ناوێک بۆ فیدراسیۆنەکە بنووسە!")

    fednam = message.text.split(None, 1)[1]
    if not fednam == "":
        fed_id = f"{user.id}:{uuid.uuid4()}"
        fed_name = fednam
        x = await fedsdb.update_one(
            {"fed_id": str(fed_id)},
            {
                "$set": {
                    "fed_name": str(fed_name),
                    "owner_id": int(user.id),
                    "fadmins": [],
                    "owner_mention": user.mention,
                    "banned_users": [],
                    "chat_ids": [],
                    "log_group_id": LOG_GROUP_ID,
                }
            },
            upsert=True,
        )
        if not x:
            return await message.reply_text(
                f"نەمتوانی فیدراسیۆن دروست بکەم! تکایە پەیوەندی بکە بە {SUPPORT_CHAT} ئەگەر کێشەکە بەردەوام بوو."
            )

        await message.reply_text(
            "**پیرۆزە! بە سەرکەوتوویی فیدراسیۆنێکی نوێت دروست کرد!**"
            "\nناو: `{}`"
            "\nئایدی: `{}`"
            "\n\nئەم فەرمانەی خوارەوە بەکاربهێنە بۆ بەستنەوەی گرووپەکەت:"
            "\n`/joinfed {}`".format(fed_name, fed_id, fed_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        try:
            await app.send_message(
                LOG_GROUP_ID,
                "فیدراسیۆنی نوێ: <b>{}</b>\nئایدی: <pre>{}</pre>".format(
                    fed_name, fed_id
                ),
                parse_mode=ParseMode.HTML,
            )
        except:
            log.info("Cannot send a message to EVENT_LOGS")
    else:
        await message.reply_text(
            "تکایە ناوێک بۆ فیدراسیۆنەکە بنووسە"
        )


@app.on_message(filters.command("delfed"))
@capture_err
async def del_fed(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "سڕینەوەی فیدراسیۆن تەنها لە ڕێگەی نامەی تایبەت (PV) بۆ من دەبێت."
        )

    args = message.text.split(" ", 1)
    if len(args) > 1:
        is_fed_id = args[1].strip()
        getinfo = await get_fed_info(is_fed_id)
        if getinfo is False:
            return await message.reply_text("ئەم فیدراسیۆنە بوونی نییە.")

        if getinfo["owner_id"] == user.id or user.id == SUDOERS:
            fed_id = is_fed_id
        else:
            return await message.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")

    else:
        return await message.reply_text("چ فیدراسیۆنێک بسڕمەوە؟")

    is_owner = await is_user_fed_owner(fed_id, user.id)
    if is_owner is False:
        return await message.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")

    await message.reply_text(
        "ئایا دڵنیایت لە سڕینەوەی فیدراسیۆنەکەت؟ ئەم کارە ناگەڕێتەوە، هەموو لیستی باندەکانت لەدەست دەدەیت و '{}' بۆ هەمیشە دەسڕێتەوە.".format(
            getinfo["fed_name"]
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⚠️ سڕینەوەی فیدراسیۆن ⚠️",
                        callback_data=f"rmfed_{fed_id}",
                    )
                ],
                [InlineKeyboardButton("پاشگەزبوونەوە", callback_data="rmfed_cancel")],
            ]
        ),
    )


@app.on_message(filters.command("fedtransfer"))
@capture_err
async def fedtransfer(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "گواستنەوەی فیدراسیۆن تەنها لە ڕێگەی نامەی تایبەت (PV) بۆ من دەبێت."
        )

    is_feds = await get_feds_by_owner(int(user.id))
    if not is_feds:
        return await message.reply_text(
            "**تۆ هیچ فیدراسیۆنێکت دروست نەکردووە.**"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "**پێویستە بەکارهێنەرێک دیاری بکەیت یان ڕیپلای نامەکەی بکەیت!**"
        )
    user_id, fed_id = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if not fed_id:
        return await message.reply(
            "پێویستە ئایدی فیدراسیۆن (Fed ID) بدەیت.\n\nشێواز:\n/fedtransfer @username Fed_Id."
        )
    is_owner = await is_user_fed_owner(fed_id, user.id)
    if is_owner is False:
        return await message.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")

    await message.reply_text(
        "**ئایا دڵنیایت لە گواستنەوەی خاوەندارێتی فیدراسیۆنەکەت؟ ئەم کارە ناگەڕێتەوە.**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⚠️ گواستنەوەی فیدراسیۆن ⚠️",
                        callback_data=f"trfed_{user_id}|{fed_id}",
                    )
                ],
                [InlineKeyboardButton("پاشگەزبوونەوە", callback_data="trfed_cancel")],
            ]
        ),
    )


@app.on_message(filters.command("myfeds"))
@capture_err
async def myfeds(client, message):
    user = message.from_user
    is_feds = await get_feds_by_owner(int(user.id))

    if is_feds:
        response_text = "\n\n".join(
            [
                f"{i + 1}) **ناوی فیدراسیۆن:** {fed['fed_name']}\n  **ئایدی فیدراسیۆن:** `{fed['fed_id']}`"
                for i, fed in enumerate(is_feds)
            ]
        )
        await message.reply_text(
            f"**ئەمە لیستی ئەو فیدراسیۆنانەیە کە تۆ دروستت کردوون:**\n\n{response_text}"
        )
    else:
        await message.reply_text("**تۆ هیچ فیدراسیۆنێکت دروست نەکردووە.**")


@app.on_message(filters.command("renamefed"))
@capture_err
async def rename_fed(client, message):
    user = message.from_user
    msg = message
    args = msg.text.split(None, 2)

    if len(args) < 3:
        return await msg.reply_text("شێواز: /renamefed fed_id ناوی_نوێ")

    fed_id, newname = args[1], args[2]
    verify_fed = await get_fed_info(fed_id)

    if not verify_fed:
        return await msg.reply_text("ئەم فیدراسیۆنە لە بنکەی زانیارییەکانمدا نییە!")

    if await is_user_fed_owner(fed_id, user.id):
        fedsdb.update_one(
            {"fed_id": str(fed_id)},
            {"$set": {"fed_name": str(newname), "owner_id": int(user.id)}},
            upsert=True,
        )
        await msg.reply_text(
            f"بە سەرکەوتوویی ناوی فیدراسیۆنەکەت گۆڕدرا بۆ {newname}!"
        )
    else:
        await msg.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")


@app.on_message(filters.command(["setfedlog", "unsetfedlog"]))
@capture_err
async def fed_log(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) < 3:
            return await message.reply_text(
                f"شێواز:\n\n /{message.command[0]} [channel_id] [fed_id]."
            )
        ids = message.text.split(" ", 2)
        chat_id = ids[1]
        fed_id = ids[2]
        try:
            await app.get_chat(chat_id)
        except Exception as e:
            return await message.reply_text(e)

    else:
        chat_id = chat.id 
        if len(message.command) < 2:
            return await message.reply_text(
                "تکایە ئایدی فیدراسیۆنەکە لەگەڵ فەرمانەکە بنووسە!"
            )
        fed_id = message.text.split(" ", 1)[1].strip()

    try:
        chat_member = await app.get_chat_member(chat_id, user.id)
        
    except ChatAdminRequired:
        return await message.reply_text("پێویستە من لە کەناڵەکە ئەدمین بم")
        
    except Exception as e:
        print(e)
        return
        
    if not chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await message.reply_text(
            "پێویستە تۆ خاوەن یان ئەدمینی کەناڵەکە بیت بۆ بەکارهێنانی ئەم فەرمانە"
        )

    info = await get_fed_info(fed_id)
    if info is False:
        return await message.reply_text("ئەم فیدراسیۆنە بوونی نییە.")

    if await is_user_fed_owner(fed_id, user.id):
        if "/unsetfedlog" in message.text:
            log_group_id = LOG_GROUP_ID
        else:
            log_group_id = chat_id
        loged = await set_log_chat(fed_id, log_group_id)
        if "/unsetfedlog" in message.text:
            return await message.reply_text(
                "کەناڵی لۆگ بە سەرکەوتوویی لادرا."
            )
        else:
            await message.reply_text("کەناڵی لۆگ بە سەرکەوتوویی دانرا.")


@app.on_message(filters.command("chatfed"))
@capture_err
async def fed_chat(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!",
        )

    fed_id = await get_fed_id(chat.id)

    member = await app.get_chat_member(chat.id, user.id)
    if (
        member.status == ChatMemberStatus.OWNER
        or member.status == ChatMemberStatus.ADMINISTRATOR
    ):
        pass
    else:
        return await message.reply_text(
            "دەبێت ئەدمین بیت بۆ جێبەجێکردنی ئەم فەرمانە"
        )

    if not fed_id:
        return await message.reply_text("ئەم گرووپە لە هیچ فیدراسیۆنێکدا نییە!")

    info = await get_fed_info(fed_id)

    text = "ئەم گرووپە بەشێکە لەم فیدراسیۆنەی خوارەوە:"
    text += "\n{} (ئایدی: <code>{}</code>)".format(info["fed_name"], fed_id)

    await message.reply_text(text, parse_mode=ParseMode.HTML)


@app.on_message(filters.command("joinfed"))
@capture_err
async def join_fed(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!",
        )

    member = await app.get_chat_member(chat.id, user.id)
    fed_id = await get_fed_id(int(chat.id))

    if user.id in SUDOERS:
        pass
    else:
        if member.status == ChatMemberStatus.OWNER:
            pass
        else:
            return await message.reply_text(
                "تەنها دروستکەری گرووپ دەتوانێت ئەم فەرمانە بەکاربهێنێت!"
            )

    if fed_id:
        return await message.reply_text(
            "ناتوانیت یەک گرووپ بە دوو فیدراسیۆنەوە ببەستیتەوە"
        )

    args = message.text.split(" ", 1)
    if len(args) > 1:
        fed_id = args[1].strip()
        getfed = await search_fed_by_id(fed_id)
        if getfed is False:
            return await message.reply_text("تکایە ئایدییەکی ڕاستی فیدراسیۆن بنووسە")
 

        x = await chat_join_fed(fed_id, chat.title, chat.id)
        if not x:
            return await message.reply_text(
                f"نەمتوانی گرووپەکە ببەستمەوە! تکایە پەیوەندی بکە بە {SUPPORT_CHAT} ئەگەر کێشەکە بەردەوام بوو!"
            )

        get_fedlog = getfed["log_group_id"]
        if get_fedlog:
            await app.send_message(
                get_fedlog,
                "گرووپی **{}** بەسترا بە فیدراسیۆنی **{}**".format(
                    chat.title, getfed["fed_name"]
                ),
                parse_mode=ParseMode.MARKDOWN,
            )

        await message.reply_text(
            "ئەم گرووپە بە سەرکەوتوویی بەسترا بە فیدراسیۆنی: {}!".format(
                getfed["fed_name"]
            )
        )
    else:
        await message.reply_text(
            "پێویستە ئایدی فیدراسیۆن (FedID) بنووسیت بۆ ئەوەی گرووپەکەی پێ ببەستیتەوە!"
        )


@app.on_message(filters.command("leavefed"))
@capture_err
async def leave_fed(client, message):
    chat = message.chat
    user = message.from_user

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!",
        )

    fed_id = await get_fed_id(int(chat.id))
    fed_info = await get_fed_info(fed_id)

    member = await app.get_chat_member(chat.id, user.id)
    if member.status == ChatMemberStatus.OWNER or user.id in SUDOERS:
        if await chat_leave_fed(int(chat.id)) is True:
            get_fedlog = fed_info["log_group_id"]
            if get_fedlog:
                await app.send_message(
                    get_fedlog,
                    "گرووپی **{}** لە فیدراسیۆنی **{}** جیا بووەوە".format(
                        chat.title, fed_info["fed_name"]
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            await message.reply_text(
                "ئەم گرووپە لە فیدراسیۆنی {} جیا بووەوە!".format(
                    fed_info["fed_name"]
                ),
            )
        else:
            await message.reply_text(
                "چۆن دەتوانیت لە فیدراسیۆنێک لێفت بکەیت کە هەرگیز جۆینت نەکردووە؟!"
            )
    else:
        await message.reply_text("تەنها دروستکەری گرووپ دەتوانێت ئەم فەرمانە بەکاربهێنێت!")


@app.on_message(filters.command("fedchats"))
@capture_err
async def fed_chat(client, message):
    chat = message.chat
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "بینینی لیستەکە تەنها لە ڕێگەی تایبەت (PV) دەبێت."
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "تکایە ئایدی فیدراسیۆنەکە بنووسە!\n\nشێواز:\n/fedchats fed_id"
        )
    args = message.text.split(" ", 1)
    if len(args) > 1:
        fed_id = args[1].strip()
        info = await get_fed_info(fed_id)
        if info is False:
            return await message.reply_text("ئەم فیدراسیۆنە بوونی نییە.")
        fed_owner = info["owner_id"]
        fed_admins = info["fadmins"]
        all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
        if user.id in all_admins or user.id in SUDOERS:
            pass
        else:
            return await message.reply_text(
                "دەبێت ئەدمینی فیدراسیۆن بیت بۆ بەکارهێنانی ئەم فەرمانە"
            )

        chat_ids, chat_names = await chat_id_and_names_in_fed(fed_id)
        if not chat_ids:
            return await message.reply_text(
                "هیچ گرووپێک لەم فیدراسیۆنەدا نییە!"
            )
        text = "\n".join(
            [
                f"$ {chat_name} [`{chat_id}`]"
                for chat_id, chat_name in zip(chat_ids, chat_names)
            ]
        )
        await message.reply_text(
            f"**ئەمە لیستی ئەو گرووپانەیە کە بەم فیدراسیۆنەوە بەستراونەتەوە:**\n\n{text}"
        )


@app.on_message(filters.command("fedinfo"))
@capture_err
async def fed_info(client, message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text("تکایە ئایدی فیدراسیۆن بنووسە بۆ وەرگرتنی زانیاری!")
    else:
        fed_id = message.text.split(" ", 1)[1].strip()
    fed_info = await get_fed_info(fed_id)

    if not fed_info:
        return await message.reply_text("فیدراسیۆن نەدۆزرایەوە.")

    fed_name = fed_info.get("fed_name")
    owner_mention = fed_info.get("owner_mention")
    fadmin_count = len(fed_info.get("fadmins", []))
    banned_users_count = len(fed_info.get("banned_users", []))
    chat_ids_count = len(fed_info.get("chat_ids", []))

    reply_text = (
        f"**زانیاری فیدراسیۆن:**\n\n"
        f"**ناوی فیدراسیۆن:** {fed_name}\n"
        f"**خاوەن:** {owner_mention}\n"
        f"**ژمارەی ئەدمینەکان:** {fadmin_count}\n"
        f"**ژمارەی باندکراوەکان:** {banned_users_count}\n"
        f"**ژمارەی گرووپەکان:** {chat_ids_count}"
    )

    await message.reply_text(reply_text)


@app.on_message(filters.command("fedadmins"))
@capture_err
async def get_all_fadmins_mentions(client, message):
    if len(message.command) < 2:
        fed_id = await get_fed_id(message.chat.id)
        if not fed_id:
            return await message.reply_text("تکایە ئایدی فیدراسیۆن بنووسە بۆ گەڕان!")
    else:
        fed_id = message.text.split(" ", 1)[1].strip()
    fed_info = await get_fed_info(fed_id)
    if not fed_info:
        return await message.reply_text("فیدراسیۆن نەدۆزرایەوە.")

    fadmin_ids = fed_info.get("fadmins", [])
    if not fadmin_ids:
        return await message.reply_text(
            f"**خاوەن: {fed_info['owner_mention']}\n\nهیچ ئەدمینێک لەم فیدراسیۆنەدا نییە."
        )

    user_mentions = []
    for user_id in fadmin_ids:
        try:
            user = await app.get_users(int(user_id))
            user_mentions.append(f"● {user.mention}[`{user.id}`]")
        except Exception:
            user_mentions.append(f"● `Admin🥷`[`{user_id}`]")
    reply_text = (
        f"**خاوەن: {fed_info['owner_mention']}\n\nلیستی ئەدمینەکان:**\n"
        + "\n".join(user_mentions)
    )

    await message.reply_text(reply_text)


@app.on_message(filters.command("fpromote"))
@capture_err
async def fpromote(client, message):
    chat = message.chat
    user = message.from_user
    msg = message

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!",
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "دەبێت سەرەتا فیدراسیۆنێک بۆ ئەم گرووپە زیاد بکەیت!"
        )

    if await is_user_fed_owner(fed_id, user.id) or user.id in SUDOERS:
        user_id = await extract_user(msg)

        if user_id is None:
            return await message.reply_text(
                "نەمتوانی بەکارهێنەرەکە بدۆزمەوە."
            )

        check_user = await check_banned_user(fed_id, user_id)
        if check_user:
            user = await app.get_users(user_id)
            reason = check_user["reason"]
            date = check_user["date"]
            return await message.reply_text(
                f"**بەکارهێنەر {user.mention} پێشتر فێد-باند کراوە.\nدەتوانیت باندی لادەیت و دواتر پلەکەی بەرز بکەیتەوە.\n\nهۆکار: {reason}.\nبەروار: {date}.**"
            )

        getuser = await search_user_in_fed(fed_id, user_id)
        info = await get_fed_info(fed_id)
        get_owner = info["owner_id"]

        if user_id == get_owner:
            return await message.reply_text(
                "ئایا دەزانیت ئەم کەسە خاوەنی فیدراسیۆنەکەیە؟"
            )

        if getuser:
            return await message.reply_text(
                "ناتوانم پلەی کەسێک بەرز بکەمەوە کە خۆی ئەدمینی فیدراسیۆنە!"
            )

        if user_id == BOT_ID:
            return await message.reply_text(
                "من خۆم لە هەموو فیدراسیۆنەکاندا ئەدمینم!"
            )

        res = await user_join_fed(str(fed_id), user_id)
        if res:
            await message.reply_text("بە سەرکەوتوویی پلەکەی بەرزکرایەوە!")
        else:
            await message.reply_text("شکستی هێنا لە بەرزکردنەوەی پلە!")
    else:
        await message.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")


@app.on_message(filters.command("fdemote"))
@capture_err
async def fdemote(client, message):
    chat = message.chat
    user = message.from_user
    msg = message

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!",
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "دەبێت سەرەتا فیدراسیۆنێک بۆ ئەم گرووپە زیاد بکەیت!"
        )

    if await is_user_fed_owner(fed_id, user.id) or user.id in SUDOERS:
        user_id = await extract_user(msg)

        if user_id is None:
            return await message.reply_text(
                "نەمتوانی بەکارهێنەرەکە بدۆزمەوە."
            )

        if user_id == BOT_ID:
            return await message.reply_text(
                "ئەگەر پلەی من دابەزێنیت، فیدراسیۆنەکە کار ناکات!"
            )

        if await search_user_in_fed(fed_id, user_id) is False:
            return await message.reply_text(
                "ناتوانم پلەی کەسێک دابەزێنم کە ئەدمینی فیدراسیۆن نییە!"
            )

        res = await user_demote_fed(fed_id, user_id)
        if res is True:
            await message.reply_text("پلەکەی دابەزێنرا و چیتر ئەدمینی فیدراسیۆن نییە!")
        else:
            await message.reply_text("شکستی هێنا لە دابەزاندنی پلە!")
    else:
        return await message.reply_text("تەنها خاوەنی فیدراسیۆن دەتوانێت ئەم کارە بکات!")


@app.on_message(filters.command(["fban", "sfban"]))
@capture_err
async def fban_user(client, message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!."
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "**ئەم گرووپە بەشێک نییە لە هیچ فیدراسیۆنێک."
        )
    info = await get_fed_info(fed_id)
    fed_owner = info["owner_id"]
    fed_admins = info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(
            "دەبێت ئەدمینی فیدراسیۆن بیت بۆ بەکارهێنانی ئەم فەرمانە"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "**پێویستە بەکارهێنەرێک دیاری بکەیت یان ڕیپلای نامەکەی بکەیت!**"
        )
    user_id, reason = await extract_user_and_reason(message)
    try:
        user = await app.get_users(user_id)
    except PeerIdInvalid:
        return await message.reply_msg("ببوورە، من هەرگیز ئەم بەکارهێنەرەم نەبینیوە.")
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id in all_admins or user_id in SUDOERS:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە باند بکەم (ئەدمینە).")
    check_user = await check_banned_user(fed_id, user_id)
    if check_user:
        reason = check_user["reason"]
        date = check_user["date"]
        return await message.reply_text(
            f"**بەکارهێنەر {user.mention} پێشتر فێد-باند کراوە.\n\nهۆکار: {reason}.\nبەروار: {date}.**"
        )
    if not reason:
        return await message.reply("تکایە هۆکارێک بنووسە.")

    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"**خەریکی فێد-باندکردنی {user.mention} م!**"
        + f" **ئەم کارە نزیکەی {len(served_chats)} چرکە دەخایەنێت.**"
    )
    await add_fban_user(fed_id, user_id, reason)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.MEMBER:
                await app.ban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(
                            served_chat, f"**بەکارهێنەر {user.mention} لە فیدراسیۆن باند کرا!**"
                        )
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(
            user.id,
            f"سڵاو، تۆ لە لایەن {from_user.mention} لە فیدراسیۆن باند کرایت،"
            + " دەتوانیت قسەی لەگەڵ بکەیت بۆ لادانی باندەکەت.",
        )
    except Exception:
        pass
    await m.edit(f"بەکارهێنەر {user.mention} فێد-باند کرا! 🚫")
    ban_text = f"""
__**فێد-باندێکی نوێ**__
**سەرچاوە:** {message.chat.title} [`{message.chat.id}`]
**ئەدمین:** {from_user.mention}
**باندکراو:** {user.mention}
**ئایدی باندکراو:** `{user_id}`
**هۆکار:** __{reason}__
**گرووپەکان:** `{number_of_chats}`"""
    try:
        m2 = await app.send_message(
            info["log_group_id"],
            text=ban_text,
            disable_web_page_preview=True,
        )
        await m.edit(
            f"بەکارهێنەر {user.mention} فێد-باند کرا! 🚫\nلۆگی کارەکە: {m2.link}",
            disable_web_page_preview=True,
        )
    except Exception:
        await message.reply_text(
            "بەکارهێنەر باند کرا، بەڵام لۆگ نەکرا. تکایە من لە LOG_GROUP زیاد بکە."
        )


@app.on_message(filters.command(["unfban", "sunfban"]))
@capture_err
async def funban_user(client, message):
    chat = message.chat
    from_user = message.from_user
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!."
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "**ئەم گرووپە بەشێک نییە لە هیچ فیدراسیۆنێک."
        )
    info = await get_fed_info(fed_id)
    fed_owner = info["owner_id"]
    fed_admins = info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(
            "دەبێت ئەدمینی فیدراسیۆن بیت بۆ بەکارهێنانی ئەم فەرمانە"
        )
    if len(message.command) < 2:
        return await message.reply_text(
            "**پێویستە بەکارهێنەرێک دیاری بکەیت یان ڕیپلای نامەکەی بکەیت!**"
        )
    user_id, reason = await extract_user_and_reason(message)
    user = await app.get_users(user_id)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id in all_admins or user_id in SUDOERS:
        return await message.reply_text(
            "**چۆن ئەدمینێک باند کراوە؟! گەمژانەیە.**"
        )
    check_user = await check_banned_user(fed_id, user_id)
    if not check_user:
        return await message.reply_text(
            "**ناتوانم باندی کەسێک لادەم کە هەرگیز فێد-باند نەکراوە.**"
        )
    if not reason:
        return await message.reply("تکایە هۆکارێک بنووسە.")

    served_chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"**خەریکی لابردنی باندی فیدراسیۆنی {user.mention} م!**"
        + f" **ئەم کارە نزیکەی {len(served_chats)} چرکە دەخایەنێت.**"
    )
    await remove_fban_user(fed_id, user_id)
    number_of_chats = 0
    for served_chat in served_chats:
        try:
            chat_member = await app.get_chat_member(served_chat, user.id)
            if chat_member.status == ChatMemberStatus.BANNED:
                await app.unban_chat_member(served_chat, user.id)
                if served_chat != chat.id:
                    if not message.text.startswith("/s"):
                        await app.send_message(
                            served_chat, f"**باندی فیدراسیۆنی {user.mention} لادرا! ✅**"
                        )
                number_of_chats += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    try:
        await app.send_message(
            user.id,
            f"سڵاو، باندی فیدراسیۆنەکەت لادرا لە لایەن {from_user.mention},"
            + " دەتوانیت سوپاسی بکەیت.",
        )
    except Exception:
        pass
    await m.edit(f"باندی فیدراسیۆنی {user.mention} لادرا! ✅")
    ban_text = f"""
__**لابردنی فێد-باند**__
**سەرچاوە:** {message.chat.title} [`{message.chat.id}`]
**ئەدمین:** {from_user.mention}
**ئەندامی ئازادکراو:** {user.mention}
**ئایدی ئەندام:** `{user_id}`
**هۆکار:** __{reason}__
**گرووپەکان:** `{number_of_chats}`"""
    try:
        m2 = await app.send_message(
            info["log_group_id"],
            text=ban_text,
            disable_web_page_preview=True,
        )
        await m.edit(
            f"باندی {user.mention} لادرا! ✅\nلۆگی کارەکە: {m2.link}",
            disable_web_page_preview=True,
        )
    except Exception:
        await message.reply_text(
            "باندی لادرا، بەڵام لۆگ نەکرا."
        )


async def status(message, user_id):
    status = await get_user_fstatus(user_id)
    user = await app.get_users(user_id)
    if status:
        response_text = "\n\n".join(
            [
                f"{i + 1}) **ناوی فیدراسیۆن:** {fed['fed_name']}\n  **ئایدی فیدراسیۆن:** `{fed['fed_id']}`"
                for i, fed in enumerate(status)
            ]
        )
        await message.reply_text(
            f"**ئەمە لیستی ئەو فیدراسیۆنانەیە کە {user.mention} تێیاندا باند کراوە:**\n\n{response_text}"
        )
    else:
        return await message.reply_text(f"**بەکارهێنەر {user.mention} لە هیچ فیدراسیۆنێکدا باند نەکراوە.**")


@app.on_message(filters.command("fedstat"))
@capture_err
async def fedstat(client, message):
    user = message.from_user
    if message.chat.type != ChatType.PRIVATE:
        return await message.reply_text(
            "پشکنینی باندی فیدراسیۆن تەنها لە ڕێگەی تایبەت (PV) دەبێت."
        )

    if len(message.command) < 2:
        user_id = user.id
        return await status(message, user_id)

    user_id, fed_id = await extract_user_and_reason(message)
    if not user_id:
        user_id = message.from_user.id
        fed_id = message.text.split(" ", 1)[1].strip()
    if not fed_id:
        return await status(message, user_id)

    info = await get_fed_info(fed_id)
    if not info:
        await message.reply_text("تکایە ئایدییەکی ڕاستی فیدراسیۆن بنووسە")
    else:
        check_user = await check_banned_user(fed_id, user_id)
        if check_user:
            user = await app.get_users(user_id)
            reason = check_user["reason"]
            date = check_user["date"]
            return await message.reply_text(
                f"**بەکارهێنەر {user.mention} لەم فیدراسیۆنەدا باند کراوە بەهۆی:\n\nهۆکار: {reason}.\nبەروار: {date}.**"
            )
        else:
            await message.reply_text(
                f"**بەکارهێنەر {user.mention} لەم فیدراسیۆنەدا باند نەکراوە.**"
            )


@app.on_message(filters.command("fbroadcast"))
@capture_err
async def fbroadcast_message(client, message):
    chat = message.chat
    from_user = message.from_user
    reply_message = message.reply_to_message
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "ئەم فەرمانە تایبەتە بە گرووپەکان، نەک تایبەت!."
        )

    fed_id = await get_fed_id(chat.id)
    if not fed_id:
        return await message.reply_text(
            "**ئەم گرووپە بەشێک نییە لە هیچ فیدراسیۆنێک."
        )
    info = await get_fed_info(fed_id)
    fed_owner = info["owner_id"]
    fed_admins = info["fadmins"]
    all_admins = [fed_owner] + fed_admins + [int(BOT_ID)]
    if from_user.id in all_admins or from_user.id in SUDOERS:
        pass
    else:
        return await message.reply_text(
            "دەبێت ئەدمینی فیدراسیۆن بیت بۆ بەکارهێنانی ئەم فەرمانە"
        )
    if not reply_message:
        return await message.reply_text(
            "**پێویستە ڕیپلای نامەیەک بکەیت بۆ ئەوەی بڕۆدکاستی بکەیت.**"
        )
    sleep_time = 0.1

    sent = 0
    chats, _ = await chat_id_and_names_in_fed(fed_id)
    m = await message.reply_text(
        f"بڕۆدکاستەکە دەستی پێکرد، نزیکەی {len(chats) * sleep_time} چرکە دەخایەنێت."
    )
    to_copy = not reply_message.poll
    for i in chats:
        try:
            if to_copy:
                await reply_message.copy(i)
            else:
                await reply_message.forward(i)
            sent += 1
            await asyncio.sleep(sleep_time)
        except FloodWait as e:
            await asyncio.sleep(int(e.value))
        except Exception:
            pass
    await m.edit(f"**نامەکە بە سەرکەوتوویی نێردرا بۆ {sent} گرووپ.**")


@app.on_callback_query(filters.regex("rmfed_(.*)"))
async def del_fed_button(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    fed_id = query.split("_")[1]

    if fed_id == "cancel":
        await cb.message.edit_text("سڕینەوەی فیدراسیۆن هەڵوەشایەوە")
        return

    getfed = await get_fed_info(fed_id)
    if getfed:
        delete = fedsdb.delete_one({"fed_id": str(fed_id)})
        if delete:
            await cb.message.edit_text(
                "تۆ فیدراسیۆنەکەت سڕییەوە! ئێستا هەموو ئەو گرووپانەی بە `{}` بەسترابوونەوە بێ فیدراسیۆن ماونەتەوە.".format(
                    getfed["fed_name"]
                ),
                parse_mode=ParseMode.MARKDOWN,
            )


@app.on_callback_query(filters.regex("trfed_(.*)"))
async def fedtransfer_button(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    data = query.split("_")[1]

    if data == "cancel":
        return await cb.message.edit_text("گواستنەوەی فیدراسیۆن هەڵوەشایەوە")

    data2 = data.split("|", 1)
    new_owner_id = int(data2[0])
    fed_id = data2[1]
    transferred = await transfer_owner(fed_id, userid, new_owner_id)
    if transferred:
        await cb.message.edit_text(
            "**خاوەندارێتی بە سەرکەوتوویی گواسترایەوە بۆ خاوەنە نوێیەکە.**"
        )


@app.on_callback_query(filters.regex("fed_(.*)"))
async def fed_owner_help(client, cb):
    query = cb.data
    userid = cb.message.chat.id
    data = query.split("_")[1]
    if data == "owner":
        text = """**👑 تایبەت بە خاوەنی فیدراسیۆن:**
 • /newfed <ناو>**:** دروستکردنی فیدراسیۆن (یەک دانە بۆ هەر کەسێک)
 • /renamefed <ئایدی> <ناوی_نوێ>**:** گۆڕینی ناوی فیدراسیۆن
 • /delfed <ئایدی>**:** سڕینەوەی فیدراسیۆن و هەموو زانیارییەکانی
 • /myfeds**:** لیستی ئەو فیدراسیۆنانەی تۆ دروستت کردوون
 • /fedtransfer <خاوەنی_نوێ> <ئایدی>**:** گواستنەوەی خاوەندارێتی
 • /fpromote <یوزەر>**:** دیاریکردنی کەسێک وەک ئەدمینی فیدراسیۆن
 • /fdemote <یوزەر>**:** لابردنی کەسێک لە ئەدمینی فیدراسیۆن
 • /setfedlog <ئایدی>**:** دیاریکردنی گرووپێک وەک لۆگی فیدراسیۆن
 • /unsetfedlog <ئایدی>**:** لابردنی گرووپی لۆگ
 • /fbroadcast **:** ناردنی نامە بۆ هەموو گرووپە بەستراوەکان """
    elif data == "admin":
        text = """**🔱 ئەدمینەکانی فیدراسیۆن:**
 • /fban <یوزەر> <هۆکار>**:** باندکردنی کەسێک لە فیدراسیۆن
 • /sfban**:** باندکردن بە بێ ناردنی نامە بۆ گرووپەکان
 • /unfban <یوزەر> <هۆکار>**:** لابردنی باندی فیدراسیۆن
 • /sunfban**:** لابردنی باند بە بێ ناردنی نامە
 • /fedadmins**:** پیشاندانی ئەدمینەکانی فیدراسیۆن
 • /fedchats <ئایدی>**:** پیشاندانی هەموو گرووپە بەستراوەکان
 • /fbroadcast **:** ناردنی نامە بۆ هەموو گرووپە بەستراوەکان
 """
    else:
        text = """**فەرمانەکانی بەکارهێنەر:**
• /fedinfo <ئایدی>: زانیاری دەربارەی فیدراسیۆنێک.
• /fedadmins <ئایدی>: لیستی ئەدمینەکانی فیدراسیۆن.
• /joinfed <ئایدی>: بەستنەوەی گرووپەکەت بە فیدراسیۆنێک (تەنها خاوەن گرووپ).
• /leavefed: جیابوونەوە لە فیدراسیۆن (تەنها خاوەن گرووپ).
• /fedstat: لیستی هەموو ئەو فیدراسیۆنانەی تۆیان تێدا باند کراوە.
• /fedstat <ئایدی_یوزەر>: لیستی ئەو فیدراسیۆنانەی یوزەرێکی تێدا باند کراوە.
• /chatfed: زانیاری دەربارەی ئەو فیدراسیۆنەی کە گرووپەکەی تێدایە.
"""
    await cb.message.edit(
        html.escape(text),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "گەڕانەوە", callback_data="help_module(federation)"
                    ),
                ]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN,
    )
