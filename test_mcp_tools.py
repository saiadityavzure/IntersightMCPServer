import asyncio
from fastmcp import Client

MCP_ENDPOINT = "http://localhost:8000/mcp"


# ---------------------------------------
#  Test: Generate Server Data Report
# ---------------------------------------
async def test_generate_server_data_report():
    print("\n=== Testing generate_server_data_report ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("generate_server_data_report", {})
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
#  Test Tools Info
# -----------------------------
async def test_tools_info():
    print("\n=== Testing health_check ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.list_tools()
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

async def test_generate_chassis_data_report():
    print("\n=== Testing generate_chassis_data_report ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("generate_chassis_data_report", {})
        print("\nResult:")
        print(result)


async def test_list_tools():
    print("\n=== Testing list_tools ===")
    async with Client(MCP_ENDPOINT) as client:
        tools = await client.list_tools()
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")


async def test_dimm_mirroring_tool():
    print("\n=== Testing dimm_mirroring_tool ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("dimm_mirroring_tool", {})
        print("\nResult:")
        print(result)

async def test_get_intersight_alarms():
    print("\n=== Testing get_intersight_alarms ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_intersight_alarms", {
            "from_date": "2025-03-01"
        })
        print("\nResult:")
        print(result)


# Create VM through ICO Test
async def test_create_a_vm_through_ico():
    print("\n=== Testing create_a_vm_through_ico ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("create_a_vm_through_ico", {
            "vm_name_value": "TestVM11142025",
            "vm_cpu_value": "4",
            "vm_mem_value": "1024",
            "vm_network_value": "vlan70",
            "cluster_name_value": "Cluster01"
        })
        print("\nResult:")
        print(result)

# Create VM Snapshot Test
async def test_create_vm_snapshot():
    print("\n=== Testing create_vm_snapshot ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("create_vm_snapshot", {
            "vm_name_value": "TestVM11142025",
            "vm_snapshot_name_value": "SNap123",
            "vm_snapshot_desc_value": "Snapshot before system upgrade"
        })
        print("\nResult:")
        print(result)

async def test_modify_vm_network():
    print("\n=== Testing modify_vm_network ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("modify_vm_network", {
            "vm_name_value": "TestVM01",
            "vm_network_value": "vlan007"
        })
        print("\nResult:")
        print(result)

async def test_migrate_a_vm():
    print("\n=== Testing migrate_a_vm ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("migrate_a_vm", {
            "vm_name_value": "TestVM01",
            "vm_target_host_value": "esxi05.vzure.local",
            "vm_target_datastore_value": "NVMe-DS-01"
        })
        print("\nResult:")
        print(result)

# ---------------------------------------------------------
# Test power_on_a_vm
# ---------------------------------------------------------
async def test_power_on_vm():
    print("\n=== Testing power_on_a_vm ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool(
            "power_on_a_vm",
            {"vm_name": "TestVM11142025"}   # <-- change to valid VM name
        )
        print("\nResult:")
        print(result)


# ---------------------------------------------------------
# Test power_off_a_vm
# ---------------------------------------------------------
async def test_power_off_vm():
    print("\n=== Testing power_off_a_vm ===")
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool(
            "power_off_a_vm",
            {"vm_name": "TestVM11142025"}   # <-- change to valid VM name
        )
        print("\nResult:")
        print(result)



async def test_get_vm_cpu_utilization():
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_vm_cpu_utilization", {})
        print(result)


async def test_get_vm_memory_utilization():
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_vm_memory_utilization", {})
        print(result)


async def test_get_virtual_machines_powerstatus_on():
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_virtual_machines_powerstatus", {"power_state": "on"})
        print(result)


async def test_get_virtual_machines_powerstatus_off():
    async with Client(MCP_ENDPOINT) as client:
        result = await client.call_tool("get_virtual_machines_powerstatus", {"power_state": "off"})
        print(result)




async def main():
    # Run whichever tools you want to test
    # await test_generate_server_data_report()
    # await test_generate_chassis_data_report()
    # await test_dimm_mirroring_tool()
    # await test_get_intersight_alarms()
    # await test_get_organization_list()     # Uncomment after creating this tool
    # await test_fabric_interconnect_report()
    # await test_health_check()
    # await test_tools_info()

    # await test_create_a_vm_through_ico()
    # await test_create_vm_snapshot()
    # await test_modify_vm_network()
    # await test_migrate_a_vm()
    # await test_power_off_vm()
    await test_power_on_vm()

    # await test_get_vm_cpu_utilization()
    # await test_get_vm_memory_utilization()
    # await test_get_virtual_machines_powerstatus_on()
    # await test_get_virtual_machines_powerstatus_off()   
    
    

if __name__ == "__main__":
    asyncio.run(main())
