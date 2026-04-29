"""
MIT License

Copyright (c) 2024 TheHamkerCat
"""
import asyncio
import re
from contextlib import suppress
from time import time

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChatPermissions,
    ChatPrivileges,
    Message,
)

from wbb import BOT_ID, SUDOERS, app, log
from wbb.core.decorators.errors import capture_err
from wbb.core.keyboard import ikb
from wbb.utils.dbfunctions import (
    add_warn,
    get_warn,
    int_to_alpha,
    remove_warns,
    save_filter,
)
from wbb.utils.functions import (
    extract_user,
    extract_user_and_reason,
    time_converter,
)

__MODULE__ = "ئەدمین"
__HELP__ = """/ban - باندکردنی بەکارهێنەر
/dban - سڕینەوەی نامەکە و باندکردنی خاوەنەکەی
/tban - باندکردنی بەکارهێنەر بۆ کاتێکی دیاریکراو
/unban - لابردنی باندی بەکارهێنەر
/listban - باندکردنی بەکارهێنەر لەو گرووپانەی لە نامەیەکدا لیست کراون
/listunban - لابردنی باندی بەکارهێنەر لەو گرووپانەی لە نامەیەکدا لیست کراون
/warn - ئاگادارکردنەوەی بەکارهێنەر
/dwarn - سڕینەوەی نامەکە و ئاگادارکردنەوەی خاوەنەکەی
/rmwarns - سڕینەوەی هەموو ئاگادارییەکانی بەکارهێنەر
/warns - پیشاندانی ئاگادارییەکانی بەکارهێنەر
/kick - دەرکردنی بەکارهێنەر (Kick)
/dkick - سڕینەوەی نامەکە و دەرکردنی خاوەنەکەی
/purge - سڕینەوەی نامەکان بە کۆمەڵ
/purge [n] - سڕینەوەی ژمارەیەکی دیاریکراو [n] لە نامەکان
/del - سڕینەوەی ئەو نامەیەی ڕیپلای کراوە
/promote - بەرزکردنەوەی پلەی ئەندام بۆ ئەدمین
/fullpromote - پێدانی هەموو دەسەڵاتەکان بە ئەدمینی نوێ
/demote - لابردنی ئەدمین
/pin - پینکردنی نامەیەک
/mute - بێدەنگکردنی بەکارهێنەر
/tmute - بێدەنگکردنی بەکارهێنەر بۆ کاتێکی دیاریکراو
/unmute - لابردنی بێدەنگی لەسەر بەکارهێنەر
/ban_ghosts - باندکردنی ئەکاونتە سڕاوەکان (Deleted Accounts)
/report | @admins | @admin - ڕاپۆرتکردنی نامەیەک بۆ ئەدمینەکان.
/invite - ناردنی لینکی بانگێشتکردنی گرووپ."""


async def member_permissions(chat_id: int, user_id: int):
    perms = []
    member = (await app.get_chat_member(chat_id, user_id)).privileges
    if not member:
        return []
    if member.can_post_messages:
        perms.append("can_post_messages")
    if member.can_edit_messages:
        perms.append("can_edit_messages")
    if member.can_delete_messages:
        perms.append("can_delete_messages")
    if member.can_restrict_members:
        perms.append("can_restrict_members")
    if member.can_promote_members:
        perms.append("can_promote_members")
    if member.can_change_info:
        perms.append("can_change_info")
    if member.can_invite_users:
        perms.append("can_invite_users")
    if member.can_pin_messages:
        perms.append("can_pin_messages")
    if member.can_manage_video_chats:
        perms.append("can_manage_video_chats")
    return perms


from wbb.core.decorators.permissions import adminsOnly

admins_in_chat = {}


async def list_admins(chat_id: int):
    global admins_in_chat
    if chat_id in admins_in_chat:
        interval = time() - admins_in_chat[chat_id]["last_updated_at"]
        if interval < 3600:
            return admins_in_chat[chat_id]["data"]

    admins_in_chat[chat_id] = {
        "last_updated_at": time(),
        "data": [
            member.user.id
            async for member in app.get_chat_members(
                chat_id, filter=ChatMembersFilter.ADMINISTRATORS
            )
        ],
    }
    return admins_in_chat[chat_id]["data"]


# Admin cache reload


@app.on_chat_member_updated()
async def admin_cache_func(_, cmu: ChatMemberUpdated):
    if cmu.old_chat_member and cmu.old_chat_member.promoted_by:
        admins_in_chat[cmu.chat.id] = {
            "last_updated_at": time(),
            "data": [
                member.user.id
                async for member in app.get_chat_members(
                    cmu.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
                )
            ],
        }
        log.info(f"نوێکردنەوەی کاشی ئەدمینەکان بۆ {cmu.chat.id} [{cmu.chat.title}]")


# Purge Messages


@app.on_message(filters.command("purge") & ~filters.private)
@adminsOnly("can_delete_messages")
async def purgeFunc(_, message: Message):
    repliedmsg = message.reply_to_message
    await message.delete()

    if not repliedmsg:
        return await message.reply_text("ڕیپلای نامەیەک بکە بۆ ئەوەی لەوێوە دەست بە سڕینەوە بکەم.")

    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purge_to = repliedmsg.id + int(cmd[1])
        if purge_to > message.id:
            purge_to = message.id
    else:
        purge_to = message.id

    chat_id = message.chat.id
    message_ids = []

    for message_id in range(
        repliedmsg.id,
        purge_to,
    ):
        message_ids.append(message_id)

        # Max message deletion limit is 100
        if len(message_ids) == 100:
            await app.delete_messages(
                chat_id=chat_id,
                message_ids=message_ids,
                revoke=True,  # For both sides
            )

            # To delete more than 100 messages, start again
            message_ids = []

    # Delete if any messages left
    if len(message_ids) > 0:
        await app.delete_messages(
            chat_id=chat_id,
            message_ids=message_ids,
            revoke=True,
        )


# Kick members


@app.on_message(filters.command(["kick", "dkick"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def kickFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id == BOT_ID:
        return await message.reply_text(
            "ناتوانم خۆم دەربکەم، ئەگەر دەتەوێت دەتوانم خۆم بڕۆم."
        )
    if user_id in SUDOERS:
        return await message.reply_text("دەتەوێت گەورەی بۆتەکە دەربکەیت؟ مەحاڵە!")
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "ناتوانم ئەدمین دەربکەم، تۆ یاساکان دەزانیت و منیش دەیانزانم."
        )
    mention = (await app.get_users(user_id)).mention
    msg = f"""
**ئەندامی دەرکراو:** {mention}
**دەرکرا لەلایەن:** {message.from_user.mention if message.from_user else 'نەناسراو'}
**هۆکار:** {reason or 'هیچ هۆکارێک نەنووسراوە.'}"""
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)
    await asyncio.sleep(1)
    await message.chat.unban_member(user_id)


# Ban members


@app.on_message(filters.command(["ban", "dban", "tban"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def banFunc(_, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)

    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id == BOT_ID:
        return await message.reply_text(
            "ناتوانم خۆم باند بکەم، ئەگەر دەتەوێت دەتوانم خۆم بڕۆم."
        )
    if user_id in SUDOERS:
        return await message.reply_text(
            "دەتەوێت گەورەی بۆتەکە باند بکەیت؟ پێداچوونەوە بە بڕیارەکەتدا بکە!"
        )
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "ناتوانم ئەدمین باند بکەم، تۆ یاساکان دەزانیت و منیش دەیانزانم."
        )

    try:
        mention = (await app.get_users(user_id)).mention
    except IndexError:
        mention = (
            message.reply_to_message.sender_chat.title
            if message.reply_to_message
            else "نەناسراو"
        )

    msg = (
        f"**ئەندامی باندکراو:** {mention}\n"
        f"**باندکرا لەلایەن:** {message.from_user.mention if message.from_user else 'نەناسراو'}\n"
    )
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if message.command[0] == "tban":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_ban = await time_converter(message, time_value)
        msg += f"**باندکرا بۆ ماوەی:** {time_value}\n"
        if temp_reason:
            msg += f"**هۆکار:** {temp_reason}"
        with suppress(AttributeError):
            if len(time_value[:-1]) < 3:
                await message.chat.ban_member(user_id, until_date=temp_ban)
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg)
            else:
                await message.reply_text("ناتوانیت زیاتر لە ٩٩ بەکاربهێنیت")
        return
    if reason:
        msg += f"**هۆکار:** {reason}"
    await message.chat.ban_member(user_id)
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg)


# Unban members


@app.on_message(filters.command("unban") & ~filters.private)
@adminsOnly("can_restrict_members")
async def unban_func(_, message: Message):
    # we don't need reasons for unban, also, we
    # don't need to get "text_mention" entity, because
    # normal users won't get text_mention if the user
    # they want to unban is not in the group.
    reply = message.reply_to_message

    if reply and reply.sender_chat and reply.sender_chat != message.chat.id:
        return await message.reply_text("ناتوانیت باندی کەناڵێک لابدەیت")

    if len(message.command) == 2:
        user = message.text.split(None, 1)[1]
    elif len(message.command) == 1 and reply:
        user = message.reply_to_message.from_user.id
    else:
        return await message.reply_text(
            "یوزەرنەیمێک بنووسە یان ڕیپلای نامەی کەسێک بکە بۆ لابردنی باندەکەی."
        )
    await message.chat.unban_member(user)
    umention = (await app.get_users(user)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"باندی لەسەر لابرا! {umention}")


# Ban users listed in a message


@app.on_message(SUDOERS & filters.command("listban") & ~filters.private)
async def list_ban_(c, message: Message):
    userid, msglink_reason = await extract_user_and_reason(message)
    if not userid or not msglink_reason:
        return await message.reply_text(
            "پێویستە ئایدی/یوزەرنەیم لەگەڵ لینکی نامە و هۆکارێک بنووسیت بۆ باندکردنی لە لیستەکەدا"
        )
    if (
        len(msglink_reason.split(" ")) == 1
    ):  # message link included with the reason
        return await message.reply_text(
            "دەبێت هۆکارێک بنووسیت"
        )
    # seperate messge link from reason
    lreason = msglink_reason.split()
    messagelink, reason = lreason[0], " ".join(lreason[1:])

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", messagelink
    ):  # validate link
        return await message.reply_text("لینکی نامەکە هەڵەیە")

    if userid == BOT_ID:
        return await message.reply_text("ناتوانم خۆم باند بکەم.")
    if userid in SUDOERS:
        return await message.reply_text(
            "دەتەوێت گەورەی بۆتەکە باند بکەیت؟ پێداچوونەوە بە بڕیارەکەتدا بکە!"
        )
    splitted = messagelink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(
        "`خەریکی باندکردنی بەکارهێنەرم لە چەندین گرووپەوە. \
         ئەمە لەوانەیە کەمێک کاتی بوێت`"
    )
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\\w+", msgtext)
    except:
        return await m.edit_text("نەمتوانی یوزەرنەیمی گرووپەکان دەربهێنم")
    count = 0
    for username in gusernames:
        try:
            await app.ban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention

    msg = f"""
**لیستی ئەندامی باندکراو:** {mention}
**ئایدی ئەندامی باندکراو:** `{userid}`
**ئەدمین:** {message.from_user.mention}
**گرووپە کارلێککراوەکان:** `{count}`
**هۆکار:** {reason}
"""
    await m.edit_text(msg)


# Unban users listed in a message


@app.on_message(SUDOERS & filters.command("listunban") & ~filters.private)
async def list_unban_(c, message: Message):
    userid, msglink = await extract_user_and_reason(message)
    if not userid or not msglink:
        return await message.reply_text(
            "پێویستە ئایدی/یوزەرنەیم لەگەڵ لینکی نامە بنووسیت بۆ لابردنی باند لە لیستەکەدا"
        )

    if not re.search(
        r"(https?://)?t(elegram)?\.me/\w+/\d+", msglink
    ):  # validate link
        return await message.reply_text("لینکی نامەکە هەڵەیە")

    splitted = msglink.split("/")
    uname, mid = splitted[-2], int(splitted[-1])
    m = await message.reply_text(
        "`خەریکی لابردنی باندی بەکارهێنەرم لە چەندین گرووپەوە. \
         ئەمە لەوانەیە کەمێک کاتی بوێت`"
    )
    try:
        msgtext = (await app.get_messages(uname, mid)).text
        gusernames = re.findall(r"@\\w+", msgtext)
    except:
        return await m.edit_text("نەمتوانی یوزەرنەیمی گرووپەکان دەربهێنم")
    count = 0
    for username in gusernames:
        try:
            await app.unban_chat_member(username.strip("@"), userid)
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except:
            continue
        count += 1
    mention = (await app.get_users(userid)).mention
    msg = f"""
**لیستی لابردنی باندی ئەندام:** {mention}
**ئایدی ئەندام:** `{userid}`
**ئەدمین:** {message.from_user.mention}
**گرووپە کارلێککراوەکان:** `{count}`
"""
    await m.edit_text(msg)


# Delete messages


@app.on_message(filters.command("del") & ~filters.private)
@adminsOnly("can_delete_messages")
async def deleteFunc(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("ڕیپلای نامەیەک بکە بۆ ئەوەی بیسڕمەوە")
    await message.reply_to_message.delete()
    await message.delete()


# Promote Members


@app.on_message(filters.command(["promote", "fullpromote"]) & ~filters.private)
@adminsOnly("can_promote_members")
async def promoteFunc(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")

    bot = (await app.get_chat_member(message.chat.id, BOT_ID)).privileges
    if user_id == BOT_ID:
        return await message.reply_text("ناتوانم پلەی خۆم بەرز بکەمەوە.")
    if not bot:
        return await message.reply_text("من ئەدمین نیم لەم گرووپەدا.")
    if not bot.can_promote_members:
        return await message.reply_text("من دەسەڵاتی پێویستم نییە بۆ ئەم کارە")

    umention = (await app.get_users(user_id)).mention

    if message.command[0][0] == "f":
        await message.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.can_change_info,
                can_invite_users=bot.can_invite_users,
                can_delete_messages=bot.can_delete_messages,
                can_restrict_members=bot.can_restrict_members,
                can_pin_messages=bot.can_pin_messages,
                can_promote_members=bot.can_promote_members,
                can_manage_chat=bot.can_manage_chat,
                can_manage_video_chats=bot.can_manage_video_chats,
            ),
        )
        return await message.reply_text(f"بە تەواوی کرا بە ئەدمین! {umention}")

    await message.chat.promote_member(
        user_id=user_id,
        privileges=ChatPrivileges(
            can_change_info=False,
            can_invite_users=bot.can_invite_users,
            can_delete_messages=bot.can_delete_messages,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=bot.can_manage_chat,
            can_manage_video_chats=bot.can_manage_video_chats,
        ),
    )
    await message.reply_text(f"کرا بە ئەدمین! {umention}")


# Demote Member


@app.on_message(filters.command("demote") & ~filters.private)
@adminsOnly("can_promote_members")
async def demote(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id == BOT_ID:
        return await message.reply_text("ناتوانم پلەی خۆم دابەزێنم.")
    if user_id in SUDOERS:
        return await message.reply_text(
            "دەتەوێت پلەی گەورەی بۆتەکە دابەزێنیت؟ پێداچوونەوە بە بڕیارەکەتدا بکە!"
        )
    try:
        member = await app.get_chat_member(message.chat.id, user_id)
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.chat.promote_member(
                user_id=user_id,
                privileges=ChatPrivileges(
                    can_change_info=False,
                    can_invite_users=False,
                    can_delete_messages=False,
                    can_restrict_members=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                    can_manage_chat=False,
                    can_manage_video_chats=False,
                ),
            )
            umention = (await app.get_users(user_id)).mention
            await message.reply_text(f"لە ئەدمین لابرا! {umention}")
        else:
            await message.reply_text(
                "ئەو کەسەی تۆ باست کرد ئەدمین نییە."
            )
    except Exception as e:
        await message.reply_text(e)


# Pin Messages


@app.on_message(filters.command(["pin", "unpin"]) & ~filters.private)
@adminsOnly("can_pin_messages")
async def pin(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("ڕیپلای نامەیەک بکە بۆ ئەوەی پین یان ئەنپینی بکەم.")
    r = message.reply_to_message
    if message.command[0][0] == "u":
        await r.unpin()
        return await message.reply_text(
            f"**پینی [ئەم]({r.link}) نامەیە لابرا.**",
            disable_web_page_preview=True,
        )
    await r.pin(disable_notification=True)
    await message.reply(
        f"**[ئەم]({r.link}) نامەیە پین کرا.**",
        disable_web_page_preview=True,
    )
    msg = "تکایە سەیری ئەم نامە پینکراوە بکە: ~ " + f"[سەیرکردن, {r.link}]"
    filter_ = dict(type="text", data=msg)
    await save_filter(message.chat.id, "~pinned", filter_)


# Mute members


@app.on_message(filters.command(["mute", "tmute"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def mute(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id == BOT_ID:
        return await message.reply_text("ناتوانم خۆم بێدەنگ بکەم.")
    if user_id in SUDOERS:
        return await message.reply_text(
            "دەتەوێت گەورەی بۆتەکە بێدەنگ بکەیت؟ پێداچوونەوە بە بڕیارەکەتدا بکە!"
        )
    if user_id in (await list_admins(message.chat.id)):
        return await message.reply_text(
            "ناتوانم ئەدمین بێدەنگ بکەم، تۆ یاساکان دەزانیت و منیش دەیانزانم."
        )
    mention = (await app.get_users(user_id)).mention
    keyboard = ikb({"🚨  لابردنی بێدەنگی  🚨": f"unmute_{user_id}"})
    msg = (
        f"**ئەندامی بێدەنگکراو:** {mention}\n"
        f"**بێدەنگکرا لەلایەن:** {message.from_user.mention if message.from_user else 'نەناسراو'}\n"
    )
    if message.command[0] == "tmute":
        split = reason.split(None, 1)
        time_value = split[0]
        temp_reason = split[1] if len(split) > 1 else ""
        temp_mute = await time_converter(message, time_value)
        msg += f"**بێدەنگکرا بۆ ماوەی:** {time_value}\n"
        if temp_reason:
            msg += f"**هۆکار:** {temp_reason}"
        try:
            if len(time_value[:-1]) < 3:
                await message.chat.restrict_member(
                    user_id,
                    permissions=ChatPermissions(),
                    until_date=temp_mute,
                )
                replied_message = message.reply_to_message
                if replied_message:
                    message = replied_message
                await message.reply_text(msg, reply_markup=keyboard)
            else:
                await message.reply_text("ناتوانیت زیاتر لە ٩٩ بەکاربهێنیت")
        except AttributeError:
            pass
        return
    if reason:
        msg += f"**هۆکار:** {reason}"
    await message.chat.restrict_member(user_id, permissions=ChatPermissions())
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(msg, reply_markup=keyboard)


# Unmute members


@app.on_message(filters.command("unmute") & ~filters.private)
@adminsOnly("can_restrict_members")
async def unmute(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    await message.chat.unban_member(user_id)
    umention = (await app.get_users(user_id)).mention
    replied_message = message.reply_to_message
    if replied_message:
        message = replied_message
    await message.reply_text(f"بێدەنگی لەسەر لابرا! {umention}")


# Ban deleted accounts


@app.on_message(filters.command("ban_ghosts") & ~filters.private)
@adminsOnly("can_restrict_members")
async def ban_deleted_accounts(_, message: Message):
    chat_id = message.chat.id
    deleted_users = []
    banned_users = 0
    m = await message.reply("گەڕان بەدوای ئەکاونتە سڕاوەکاندا...")

    async for i in app.get_chat_members(chat_id):
        if i.user.is_deleted:
            deleted_users.append(i.user.id)
    if len(deleted_users) > 0:
        for deleted_user in deleted_users:
            try:
                await message.chat.ban_member(deleted_user)
            except Exception:
                pass
            banned_users += 1
        await m.edit(f"({banned_users}) ئەکاونتی سڕاوە باند کران")
    else:
        await m.edit("هیچ ئەکاونتێکی سڕاوە لەم گرووپەدا بوونی نییە")


@app.on_message(filters.command(["warn", "dwarn"]) & ~filters.private)
@adminsOnly("can_restrict_members")
async def warn_user(_, message: Message):
    user_id, reason = await extract_user_and_reason(message)
    chat_id = message.chat.id
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    if user_id == BOT_ID:
        return await message.reply_text(
            "ناتوانم خۆم ئاگادار بکەمەوە، ئەگەر دەتەوێت دەتوانم خۆم بڕۆم."
        )
    if user_id in SUDOERS:
        return await message.reply_text(
            "دەتەوێت گەورەی بۆتەکە ئاگادار بکەیتەوە؟ پێداچوونەوە بە بڕیارەکەتدا بکە!"
        )
    if user_id in (await list_admins(chat_id)):
        return await message.reply_text(
            "ناتوانم ئەدمین ئاگادار بکەمەوە، تۆ یاساکان دەزانیت و منیش دەیانزانم."
        )
    user, warns = await asyncio.gather(
        app.get_users(user_id),
        get_warn(chat_id, await int_to_alpha(user_id)),
    )
    mention = user.mention
    keyboard = ikb({"🚨  لابردنی ئاگادارکردنەوە  🚨": f"unwarn_{user_id}"})
    if warns:
        warns = warns["warns"]
    else:
        warns = 0
    if message.command[0][0] == "d":
        await message.reply_to_message.delete()
    if warns >= 2:
        await message.chat.ban_member(user_id)
        await message.reply_text(
            f"ژمارەی ئاگادارکردنەوەکانی {mention} لە سنوور دەرچوو، باند کرا!"
        )
        await remove_warns(chat_id, await int_to_alpha(user_id))
    else:
        warn = {"warns": warns + 1}
        msg = f"""
**ئەندامی ئاگادارکراوە:** {mention}
**ئاگادارکرایەوە لەلایەن:** {message.from_user.mention if message.from_user else 'نەناسراو'}
**هۆکار:** {reason or 'هیچ هۆکارێک نەنووسراوە.'}
**ژمارەی ئاگادارکردنەوە:** {warns + 1}/3"""
        replied_message = message.reply_to_message
        if replied_message:
            message = replied_message
        await message.reply_text(msg, reply_markup=keyboard)
        await add_warn(chat_id, await int_to_alpha(user_id), warn)


@app.on_callback_query(filters.regex("unwarn_"))
async def remove_warning(_, cq: CallbackQuery):
    from_user = cq.from_user
    chat_id = cq.message.chat.id
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        return await cq.answer(
            "دەسەڵاتی پێویستت نییە بۆ ئەنجامدانی ئەم کارە.\n"
            + f"دەسەڵاتی پێویست: {permission}",
            show_alert=True,
        )
    user_id = cq.data.split("_")[1]
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if not warns or warns == 0:
        return await cq.answer("ئەم بەکارهێنەرە هیچ ئاگادارییەکی نییە.")
    warn = {"warns": warns - 1}
    await add_warn(chat_id, await int_to_alpha(user_id), warn)
    text = cq.message.text.markdown
    text = f"~~{text}~~\n\n"
    text += f"__ئاگادارکردنەوەکە لابرایە لەلایەن {from_user.mention}__"
    await cq.message.edit(text)


# Rmwarns


@app.on_message(filters.command("rmwarns") & ~filters.private)
@adminsOnly("can_restrict_members")
async def remove_warnings(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text(
            "ڕیپلای نامەیەک بکە بۆ سڕینەوەی هەموو ئاگادارییەکانی."
        )
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    chat_id = message.chat.id
    warns = await get_warn(chat_id, await int_to_alpha(user_id))
    if warns:
        warns = warns["warns"]
    if warns == 0 or not warns:
        await message.reply_text(f"{mention} هیچ ئاگادارییەکی نییە.")
    else:
        await remove_warns(chat_id, await int_to_alpha(user_id))
        await message.reply_text(f"هەموو ئاگادارییەکانی {mention} سڕانەوە.")


# Warns


@app.on_message(filters.command("warns") & ~filters.private)
@capture_err
async def check_warns(_, message: Message):
    user_id = await extract_user(message)
    if not user_id:
        return await message.reply_text("ناتوانم ئەو بەکارهێنەرە بدۆزمەوە.")
    warns = await get_warn(message.chat.id, await int_to_alpha(user_id))
    mention = (await app.get_users(user_id)).mention
    if warns:
        warns = warns["warns"]
    else:
        return await message.reply_text(f"{mention} هیچ ئاگادارییەکی نییە.")
    return await message.reply_text(f"{mention} خاوەنی {warns}/3 ئاگادارییە.")


# Report


@app.on_message(
    (
        filters.command("report")
        | filters.command(["admins", "admin"], prefixes="@")
    )
    & ~filters.private
)
@capture_err
async def report_user(_, message):
    if len(message.text.split()) <= 1 and not message.reply_to_message:
        return await message.reply_text(
            "ڕیپلای نامەیەک بکە بۆ ڕاپۆرتکردنی ئەو ئەندامە."
        )

    reply = message.reply_to_message if message.reply_to_message else message
    reply_id = reply.from_user.id if reply.from_user else reply.sender_chat.id
    user_id = (
        message.from_user.id if message.from_user else message.sender_chat.id
    )

    list_of_admins = await list_admins(message.chat.id)
    linked_chat = (await app.get_chat(message.chat.id)).linked_chat
    if linked_chat is not None:
        if (
            reply_id in list_of_admins
            or reply_id == message.chat.id
            or reply_id == linked_chat.id
        ):
            return await message.reply_text(
                "ئایا دەزانیت ئەو کەسەی ڕیپلایت کردووە ئەدمینە؟"
            )
    else:
        if reply_id in list_of_admins or reply_id == message.chat.id:
            return await message.reply_text(
                "ئایا دەزانیت ئەو کەسەی ڕیپلایت کردووە ئەدمینە؟"
            )

    user_mention = (
        reply.from_user.mention if reply.from_user else reply.sender_chat.title
    )
    text = f"{user_mention} ڕاپۆرت کرا بۆ ئەدمینەکان!."
    admin_data = [
        i
        async for i in app.get_chat_members(
            chat_id=message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        )
    ]  # will it give floods ???
    for admin in admin_data:
        if admin.user.is_bot or admin.user.is_deleted:
            # return bots or deleted admins
            continue
        text += f"[\u2063](tg://user?id={admin.user.id})"

    await reply.reply_text(text)


@app.on_message(filters.command("invite"))
@adminsOnly("can_invite_users")
async def invite(_, message):
    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        link = (await app.get_chat(message.chat.id)).invite_link
        if not link:
            link = await app.export_chat_invite_link(message.chat.id)
        text = f"فەرموو ئەمە لینکی بانگێشتکردنی گرووپە.\n\n{link}"
        if message.reply_to_message:
            await message.reply_to_message.reply_text(
                text, disable_web_page_preview=True
            )
        else:
            await message.reply_text(text, disable_web_page_preview=True)
