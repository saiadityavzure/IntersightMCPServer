import asyncio
from fastmcp import Client

async def main():
    client = Client("http://10.20.1.53:8000/mcp")

    await client.start()
    await client.initialize()

    print("\n=== AVAILABLE TOOLS ON MCP SERVER ===")
    for tool in client.tools:
        print(f"- {tool.name}: {tool.description}")

    await client.close()

asyncio.run(main())
