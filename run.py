#!/usr/bin/env python3
"""
Main entry point for the Email Monitor Discord Bot
This file serves as a wrapper to run the bot from the src directory
"""

import asyncio
from src.bot import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
        import sys
        sys.exit(1)
