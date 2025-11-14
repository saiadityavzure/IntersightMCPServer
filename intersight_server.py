from fastmcp import FastMCP


from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import platform

from intersight.api import compute_api
from intersight.exceptions import ApiException


# Importing the Tools from the respective files to register with MCP
from toolsfile.organization_tools import register_organization_tools
from toolsfile.ReportTools.server_data_report import register_server_data_report_tool
from toolsfile.ReportTools.fabric_interconnect_tools import register_fabric_interconnect_tools
from toolsfile.ReportTools.chassis_data_report import register_chassis_data_report_tool
from toolsfile.ReportTools.dimm_mirroring_report import register_dimm_mirroring_tool
from toolsfile.ReportTools.intersight_alarms_report import register_intersight_alarm_tool

#Virtual Machine Management Tools can be registered here as needed
from toolsfile.virtualmachinemanagement.create_vm_tool import register_create_vm_tool
from toolsfile.virtualmachinemanagement.create_vm_snapshot_tool import register_create_vm_snapshot_tool
from toolsfile.virtualmachinemanagement.modify_vm_network_tool import register_modify_vm_network_tool
from toolsfile.virtualmachinemanagement.migrate_vm_tool import register_migrate_vm_tool
from toolsfile.virtualmachinemanagement.power_vm_tools import register_vm_power_tools

#Virtual Machine Info Tools
from toolsfile.virtualmachineinfo.vm_utilization_tools import register_vm_utilization_tools
from toolsfile.virtualmachineinfo.vm_powerstatus_tool import register_vm_powerstatus_tool

mcp = FastMCP("IntersightMCPServer")


# ------------------------------------------------------------------
# Simple health check
# ------------------------------------------------------------------

@mcp.tool(
    name="health_check",
    description="Returns the health status of the Intersight MCP Server.",
    tags={"system", "health", "status"},
    meta={"version": "1.0"}
)
def health_check() -> dict:
    return {
        "status": "healthy",
        "message": "Intersight MCP Server is running.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server": {
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "release": platform.release()
        }
    }


@mcp.tool
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum with return annotation."""
    return a + b  # Returns the sum of a and b


##############################################################
# Register tools
##############################################################


# Report Tools
register_server_data_report_tool(mcp)
register_organization_tools(mcp)
register_fabric_interconnect_tools(mcp)
register_fabric_interconnect_tools(mcp)
register_chassis_data_report_tool(mcp)
register_dimm_mirroring_tool(mcp)
register_intersight_alarm_tool(mcp)

#Register Virtual Machine Management Tools
register_create_vm_tool(mcp)
register_create_vm_snapshot_tool(mcp)
register_modify_vm_network_tool(mcp)
# register_migrate_vm_tool(mcp)
register_vm_power_tools(mcp)

register_vm_utilization_tools(mcp)
register_vm_powerstatus_tool(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)