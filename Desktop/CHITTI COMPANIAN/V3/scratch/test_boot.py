import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop.app.kernel import BootManager
from desktop.app.kernel import RuntimeConfiguration

async def main():
    print("--- Booting CHITTI Cognitive Engine (Architecture Validation) ---")
    boot_manager = BootManager()
    kernel = boot_manager.compose_runtimes()
    await kernel.boot()
    await kernel.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
