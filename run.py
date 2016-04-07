import telepot
from telepot.delegate import per_inline_from_id, create_open

from dotabuff.config import BOT_TOKEN
from dotabuff.bot import InlineHandler

bot = telepot.DelegatorBot(BOT_TOKEN, [
    (per_inline_from_id(), create_open(InlineHandler, timeout=10)),
])
bot.notifyOnMessage(run_forever=True)