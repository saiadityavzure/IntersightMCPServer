from fastmcp import FastMCP
from intersight.api import compute_api
from intersight.exceptions import ApiException

from utils.intersight_auth import intersight_client_connection
from models.compute_physical_summary import ComputePhysicalSummary


def register_physical_summary_tools(mcp: FastMCP):

    @mcp.tool(
        name="list_physical_summaries",
        description="Fetches compute.PhysicalSummaries from Cisco Intersight using the Python SDK and returns structured data.",
        tags={"compute", "hardware", "summaries"},
        meta={"version": "1.0", "endpoint": "/compute/PhysicalSummaries"}
    )
    def list_physical_summaries(filter: str = None, top: int = 25):

        # SDK Client
        client = intersight_client_connection()
        compute = compute_api.ComputeApi(client)

        # Build query args
        request_args = {"top": top}
        if filter:
            request_args["filter"] = filter

        try:
            # Call Intersight SDK
            response = compute.get_compute_physical_summary_list(**request_args)

            # Convert SDK objects → dict → Pydantic → clean JSON
            parsed_items = []
            for item in response.results:
                raw = item.to_dict()                        
                parsed = ComputePhysicalSummary(**raw)      
                parsed_items.append(parsed.model_dump())    

            return {
                "count": len(parsed_items),
                "items": parsed_items
            }

        except ApiException as e:
            return {
                "error": True,
                "message": f"API Error: {e}",
                "status": getattr(e, "status", None)
            }

        except Exception as ex:
            return {
                "error": True,
                "message": f"Unexpected error: {str(ex)}"
            }
