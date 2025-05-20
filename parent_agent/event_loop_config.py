import asyncio
import sys

def configure_event_loop():
    if sys.platform == 'win32':
        # Set the event loop policy to use ProactorEventLoop on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        # Create and set a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop) 