"""Dev entrypoint for the local Mistral Workflows worker."""

import asyncio

from src.discover import main

if __name__ == "__main__":
    asyncio.run(main())
