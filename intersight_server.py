from fastmcp import FastMCP


from dotenv import load_dotenv
load_dotenv()

from utils.intersight_auth import intersight_client_connection
from utils.intersight_rest import get_intersight_rest_session

from intersight.api import compute_api
from intersight.exceptions import ApiException

from models.organization import Organization


mcp = FastMCP("Intersight MCP Server")


@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def list_physical_summaries(filter: str = None, top: int = 25):
    """
    Fetch compute PhysicalSummaries from Cisco Intersight.

    Args:
        filter (str): Optional OData filter string
        top (int): Max results to return (default: 25)

    Returns:
        List of compute.PhysicalSummary objects as dicts
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
    

@mcp.tool(
    description="Returns all Organizations from Cisco Intersight."
)
def get_organization_list() -> list[Organization]:
    session, endpoint = get_intersight_rest_session()
    url = f"{endpoint}/api/v1/organization/Organizations"
    r = session.get(url)

    data = r.json().get("Results", [])
    return [Organization(**item) for item in data]


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)