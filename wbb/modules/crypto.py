from pyrogram import filters

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.keyboard import ikb
from wbb.core.sections import section
from wbb.utils.http import get

__MODULE__ = "کڕیپتۆ"
__HELP__ = """
/crypto [ناوی_دراو]
        بۆ وەرگرتنی نرخی ڕاستەقینە و ساتی دراوە دیجیتاڵییەکان.
"""


@app.on_message(filters.command("crypto"))
@capture_err
async def crypto(_, message):
    if len(message.command) < 2:
        return await message.reply("تکایە بەم شێوەیە بنووسە:\n/crypto [ناوی_دراو]")

    currency = message.text.split(None, 1)[1].lower()

    btn = ikb(
        {"دراوە بەردەستەکان 💰": "https://plotcryptoprice.herokuapp.com"},
    )

    m = await message.reply("`لە جێبەجێکردندایە...`")

    try:
        r = await get(
            "https://x.wazirx.com/wazirx-falcon/api/v2.0/crypto_rates",
            timeout=5,
        )
    except Exception:
        return await m.edit("[هەڵە]: کێشەیەک ڕوویدا لە وەرگرتنی نرخەکان.")

    if currency not in r:
        return await m.edit(
            "[هەڵە]: ناوی دراوەکە هەڵەیە یان نەدۆزرایەوە.",
            reply_markup=btn,
        )

    body = {i.upper(): j for i, j in r.get(currency).items()}

    text = section(
        "نرخی ئێستای دراوی " + currency.upper(),
        body,
    )
    await m.edit(text, reply_markup=btn)
