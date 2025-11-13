import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        res = await client.call_tool("list_physical_summaries", {"top": 5})
        print(res)

asyncio.run(main())