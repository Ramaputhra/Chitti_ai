import asyncio
import sys
import os

# Ensure V3 path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tests.test_intent_corpus import run_corpus

if __name__ == "__main__":
    asyncio.run(run_corpus())
