import asyncio
from fastmcp import Client

MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"

async def test_list_physical_summaries():
    print("\n=== Testing list_physical_summaries ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("list_physical_summaries", {"top": 5})
        print("\nResult:")
        print(result)

async def test_get_organization_list():
    print("\n=== Testing get_organization_list ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_organization_list", {})
        print("\nResult:")
        print(result)

async def main():
    # Run whichever tools you want to test
    # await test_list_physical_summaries()
    await test_get_organization_list()     # Uncomment after creating this tool

if __name__ == "__main__":
    asyncio.run(main())
