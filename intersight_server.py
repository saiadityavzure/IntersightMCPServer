from fastmcp import FastMCP


from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import platform

from utils.intersight_auth import intersight_client_connection
from utils.intersight_rest import get_intersight_rest_session

from intersight.api import compute_api
from intersight.exceptions import ApiException


# Importing the Tools from the respective files to register with MCP
from toolsfile.organization_tools import register_organization_tools
from toolsfile.compute.compute_physical_summaries import register_physical_summary_tools
from toolsfile.network.fabric_interconnect_tools import register_fabric_interconnect_tools
from toolsfile.network.fabric_interconnect_tools import register_fabric_interconnect_tools


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

register_physical_summary_tools(mcp)
register_organization_tools(mcp)
register_fabric_interconnect_tools(mcp)
register_fabric_interconnect_tools(mcp)




if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)