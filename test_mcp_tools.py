import asyncio
from fastmcp import Client

MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"


# -----------------------------
#  Test Physical Summaries
# -----------------------------
async def test_list_physical_summaries():
    print("\n=== Testing list_physical_summaries ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("list_physical_summaries", {"top": 5})
        print("\nResult:")
        print(result)


# -----------------------------
#  Test Organization List
# -----------------------------
async def test_get_organization_list():
    print("\n=== Testing get_organization_list ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_organization_list", {})
        print("\nResult:")
        print(result)

# -----------------------------
#  Test Server Health
# -----------------------------
async def test_health_check():
    print("\n=== Testing health_check ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("health_check", {})
        print("\nResult:")
        print(result)

# -----------------------------
#  Test Fabric Interconnect Report
# -----------------------------
async def test_fabric_interconnect_report():
    print("\n=== Testing get_fabric_interconnect_report ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_fabric_interconnect_report", {})
        print("\nResult:")
        print(result)


async def main():
    # Run whichever tools you want to test
    await test_list_physical_summaries()
    # await test_get_organization_list()     # Uncomment after creating this tool
    # await test_fabric_interconnect_report()
    # await test_health_check()

if __name__ == "__main__":
    asyncio.run(main())
