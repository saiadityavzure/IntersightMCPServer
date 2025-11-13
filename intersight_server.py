from fastmcp import FastMCP


from dotenv import load_dotenv
load_dotenv()

from utils.intersight_auth import intersight_client_connection
from utils.intersight_rest import get_intersight_rest_session

from intersight.api import compute_api
from intersight.exceptions import ApiException

from models.organization import Organization


mcp = FastMCP("IntersightMCPServer")


# ------------------------------------------------------------------
# 🔹 Simple greeting test tool (works for health checks)
# ------------------------------------------------------------------
@mcp.tool(
    name="greet_user",
    description="Returns a friendly greeting for the provided name.",
    tags={"utility", "test"},
    meta={"version": "1.0"}
)
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum with return annotation."""
    return a + b  # Returns the sum of a and b


# ------------------------------------------------------------------
# 🔹 Physical Summaries Tool
# ------------------------------------------------------------------
@mcp.tool(
    name="list_physical_summaries",
    description="Fetches a list of compute PhysicalSummaries from Cisco Intersight.",
    tags={"compute", "hardware", "summaries"},
    meta={"version": "1.0", "endpoint": "/compute/PhysicalSummaries"}
)
def list_physical_summaries(filter: str = None, top: int = 25):
    """
    Fetch compute PhysicalSummaries from Cisco Intersight.
    """
    client = intersight_client_connection()
    compute = compute_api.ComputeApi(client)

    request_args = {"top": top}
    if filter:
        request_args["filter"] = filter

    try:
        response = compute.get_compute_physical_summary_list(**request_args)
        results = [item.to_dict() for item in response.results]
        return {
            "count": len(results),
            "items": results
        }
    except ApiException as e:
        return {
            "error": True,
            "message": f"API Error: {e}",
            "status": getattr(e, 'status', None)
        }
    except Exception as ex:
        return {
            "error": True,
            "message": f"Unexpected error: {str(ex)}"
        }
    

# ------------------------------------------------------------------
# 🔹 Organization List Tool (REST)
# ------------------------------------------------------------------
@mcp.tool(
    name="get_organization_list",
    description="Returns all Organizations from Cisco Intersight using the REST API.",
    tags={"organization", "iam", "rest"},
    meta={"version": "1.0", "endpoint": "/organization/Organizations"}
)
def get_organization_list() -> list[Organization]:
    session, endpoint = get_intersight_rest_session()
    url = f"{endpoint}/api/v1/organization/Organizations"
    r = session.get(url)

    data = r.json().get("Results", [])
    return [Organization(**item) for item in data]


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)