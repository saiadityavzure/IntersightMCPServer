from fastmcp import FastMCP
from typing import List
from pydantic import ValidationError

from utils.intersight_rest import get_intersight_rest_session
from models.organization import Organization
import json


def register_organization_tools(mcp: FastMCP):

    @mcp.tool(
        name="get_organization_list",
        description="Returns all Organizations from Cisco Intersight using the REST API.",
        tags={"organization", "iam", "rest"},
        meta={"version": "1.0", "endpoint": "/organization/Organizations"},
    )
    def get_organization_list() -> str:
        session, endpoint = get_intersight_rest_session()
        url = f"{endpoint}/api/v1/organization/Organizations"

        response = session.get(url)
        data = response.json().get("Results", [])

        formatted = []

        for item in data:
            try:
                # Try validation
                org = Organization(**item)
                formatted.append(org.model_dump())
            except ValidationError as ve:
                # Fallback to raw JSON
                formatted.append({
                    "raw_item": item,
                    "validation_error": str(ve)
                })

        return json.dumps({
            "count": len(formatted),
            "items": formatted
        })
