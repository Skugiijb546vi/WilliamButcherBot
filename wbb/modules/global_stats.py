"""
MIT License
Copyright (c) 2024 TheHamkerCat
"""
import asyncio

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from wbb import BOT_ID, BOT_NAME, SUDOERS, USERBOT_NAME, app, app2
from wbb.core.decorators.errors import capture_err
from wbb.modules import ALL_MODULES
from wbb.utils.dbfunctions import (
    get_blacklist_filters_count,
    get_filters_count,
    get_gbans_count,
    get_karmas_count,
    get_notes_count,
    get_rss_feeds_count,
    get_served_chats,
    get_served_users,
    get_warns_count,
    remove_served_chat,
)
from wbb.utils.http import get
from wbb.utils.inlinefuncs import keywords_list


@app.on_message(filters.command("clean_db") & SUDOERS)
@capture_err
async def clean_db(_, message):
    served_chats = [int(i["chat_id"]) for i in (await get_served_chats())]
    m = await message.reply(
        f"__**خەریکی پاککردنەوەی بنکەی زانیارییەکانم، لەوانەیە نزیکەی {len(served_chats) * 2} چرکە بخایەنێت.**__",
    )
    for served_chat in served_chats:
        try:
            await app.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(int(e.x))
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
    await m.edit("**بنکەی زانیارییەکان بە سەرکەوتوویی پاککرایەوە.**")


async def get_total_users_count():
    schats = await get_served_chats()
    chats = [int(chat["chat_id"]) for chat in schats]
    total_count = 0
    for chat_id in chats:
        try:
            count = await app.get_chat_members_count(chat_id)
            total_count += count
        except Exception:
            print(f"Error fetching members count for chat: {chat_id}")
    return total_count


@app.on_message(filters.command("gstats") & SUDOERS)
@capture_err
async def global_stats(_, message):
    m = await app.send_message(
        message.chat.id,
        text="__**خەریکی شیکردنەوەی ئامارەکانم...**__",
        disable_web_page_preview=True,
    )

    # For bot served chat and users count
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_users = await get_total_users_count()  # get total user count
    # Gbans count
    gbans = await get_gbans_count()
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Blacklisted filters count across chats
    _filters = await get_blacklist_filters_count()
    blacklist_filters_count = _filters["filters_count"]
    blacklist_filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # Contributors/Developers count and commits on github
    url = "https://api.github.com/repos/thehamkercat/williambutcherbot/contributors"
    rurl = "https://github.com/thehamkercat/williambutcherbot"
    developers = await get(url)
    commits = 0
    for developer in developers:
        commits += developer["contributions"]
    developers = len(developers)

    # Rss feeds
    rss_count = await get_rss_feeds_count()
    # Modules info
    modules_count = len(ALL_MODULES)

    # Userbot info
    groups_ub = channels_ub = bots_ub = privates_ub = total_ub = 0
    async for i in app2.get_dialogs():
        t = i.chat.type
        total_ub += 1

        if t in [ChatType.SUPERGROUP, ChatType.GROUP]:
            groups_ub += 1
        elif t == ChatType.CHANNEL:
            channels_ub += 1
        elif t == ChatType.BOT:
            bots_ub += 1
        elif t == ChatType.PRIVATE:
            privates_ub += 1

    msg = f"""
**ئامارە گشتییەکانی {BOT_NAME}**:
    **{modules_count}** مۆدیوڵ بارکراون.
    **{len(keywords_list)}** مۆدیوڵی ئینلاین بارکراون.
    **{rss_count}** فیدی RSS چالاک.
    **{gbans}** بەکارهێنەری گڵۆبڵ-باندکراو.
    **{filters_count}** فلتەر، لە ناو **{filters_chats_count}** گرووپدا.
    **{blacklist_filters_count}** فلتەری لیستی ڕەش، لە ناو **{blacklist_filters_chats_count}** گرووپدا.
    **{notes_count}** تێبینی (Notes)، لە ناو **{notes_chats_count}** گرووپدا.
    **{warns_count}** ئاگادارکردنەوە (Warns)، لە ناو **{warns_chats_count}** گرووپدا.
    **{karmas_count}** کارما (Karma)، لە ناو **{karmas_chats_count}** گرووپدا.
    **{served_users}** بەکارهێنەر، لە ناو **{served_chats}** گرووپدا.
    **{total_users}** کۆی گشتی بەکارهێنەران لە گرووپەکاندا.
    **{developers}** گەشەپێدەر و **{commits}** کۆمیت (Commits) لەسەر **[گیتھەب]({rurl})**.

**ئامارە گشتییەکانی {USERBOT_NAME} (یوزەربۆت)**:
    **{total_ub} گفتوگۆ (Dialogs).**
    **{groups_ub} گرووپ جۆین کراوە.**
    **{channels_ub} کەناڵ جۆین کراوە.**
    **{bots_ub} بۆت.**
    **{privates_ub} بەکارهێنەر (PV).**
"""
    await m.edit(msg, disable_web_page_preview=True)
