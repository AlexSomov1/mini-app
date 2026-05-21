import asyncio
import logging
from .loader import bot, dp, on_startup, on_shutdown
from .routers.start import router as start_router
from .routers.requests import router as requests_router
from .routers.admin import router as admin_router
from .routers.fallback import router as fallback_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    dp.include_router(start_router)
    dp.include_router(requests_router)
    dp.include_router(admin_router)
    dp.include_router(fallback_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Выход по Ctrl+C")