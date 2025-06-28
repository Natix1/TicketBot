import asyncio
import config
import helpers.persistent_store as persistent_store
import atexit

from helpers.async_requests import close_session
from pathlib import Path
from bot import bot
from helpers.extensions import extensions
from misc.on_tree_error import on_tree_error

print(f"Loading {len(extensions)} extensions:")
for index, ext in enumerate(extensions):
    print(f"{index}. {ext}")

print("\n", end="")

def close_session_sync():
    asyncio.run(close_session())

atexit.register(close_session_sync)

async def main():
    async with bot:
        for ext in extensions:
            print(f"Loading extension '{ext}'...")
            await bot.load_extension(ext)

        print("Initliazing sqlite connection...")
        persistent_store.initialize_db()

        print("All extensions loaded")
        print("Logging in...")
        
        bot.tree.on_error = on_tree_error

        try:
            await bot.start(config.TOKEN)
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\rClosing bot..")

asyncio.run(main())