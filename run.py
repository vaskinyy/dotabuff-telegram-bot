import asyncio
import telepot
from telepot.async.delegate import per_from_id, create_open

from dotabuff.config import BOT_TOKEN
from dotabuff.bot import UserTracker

bot = telepot.async.DelegatorBot(BOT_TOKEN, [
    (per_from_id(), create_open(UserTracker, timeout=20)),
])
loop = asyncio.get_event_loop()

loop.create_task(bot.messageLoop())
print('Listening ...')

loop.run_forever()