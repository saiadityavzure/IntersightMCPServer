import json
import logging
import traceback
import base64
import io
import os
from urllib.parse import quote
from datetime import datetime

import pandas as pd
from fastmcp import FastMCP
from mcp import types as mcp_types  # ✅ important

from utils.intersight_auth import intersight_client_connection
import intersight.api.network_api

logger = logging.getLogger(__name__)


def register_fabric_interconnect_tools(mcp: FastMCP):

    @mcp.tool(
        name="get_fabric_interconnect_report",
        description="Fetches Fabric Interconnect data from Cisco Intersight and builds a summary.",
        tags={"network", "fabric-interconnect", "report"},
        meta={"version": "1.0", "endpoint": "/network/ElementSummaries"},
    )
    def get_fabric_interconnect_report():
        """
        Returns:
            List of MCP content blocks:
            - TextContent JSON (count + summary)
            - EmbeddedResource with XLSX blob (client stores to MEDIA_ROOT)
        """
        try:
            # Connect to Intersight
            client = intersight_client_connection()
            api = intersight.api.network_api.NetworkApi(client)

            logger.info("Connected to Intersight successfully for Fabric Interconnect Report")

            # Sorting and filtering
            orderby = "Name asc"
            filter_query = "SwitchType eq FabricInterconnect"
            expand_query = "RegisteredDevice,PermissionResources($select=Name)"
            select_query = (
                "Tags,PermissionResources,Name,AlarmSummary,OutOfBandIpAddress,"
                "Model,NumExpansionModules,BundleVersion,FirmwareVersion,Serial,"
                "RegisteredDevice,SwitchType,NumEtherPorts,NumFcPorts,"
                "NumEtherPortsConfigured,NumFcPortsConfigured,"
                "DeviceMoId,ManagementMode,Presence,Status,SourceObjectType,Dn"
            )

            # Query FI inventory
            response = api.get_network_element_summary_list(
                orderby=orderby,
                filter=filter_query,
                select=select_query,
                expand=expand_query
            )

            fabric_list = response.get("results", []) or []
            fabrics = []

            for fi in fabric_list:
                orgs = [p["name"] for p in fi.get("permission_resources", [])]

                ports_total = fi.get("num_ether_ports", 0) or 0
                ports_used = fi.get("num_ether_ports_configured", 0) or 0

                row = {
                    "Name": fi.get("name"),
                    "Health": (fi.get("alarm_summary") or {}).get("health"),
                    "Management IP": fi.get("out_of_band_ip_address"),
                    "Model": fi.get("model"),
                    "Expansion Modules": fi.get("num_expansion_modules"),
                    "Bundle Version": fi.get("bundle_version"),
                    "NX-OS Version": fi.get("firmware_version"),
                    "Ports": ports_total,
                    "Used Ports": ports_used,
                    "Available Ports": ports_total - ports_used,
                    "Serial": fi.get("serial"),
                    "Organizations": orgs,
                }

                fabrics.append(row)

            if not fabrics:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No Fabric Interconnects found."})
                    )
                ]

            # Summary
            summary_keys = ["Name", "Health", "Model", "Bundle Version"]
            summary = [{k: r.get(k) for k in summary_keys} for r in fabrics]

            # Build Excel in-memory
            df = pd.DataFrame(fabrics)
            df["Organizations"] = df["Organizations"].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else x
            )

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="FabricInterconnects")

            excel_bytes = buf.getvalue()
            blob_b64 = base64.b64encode(excel_bytes).decode("utf-8")

            # Safe filename + valid URI
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"fabric_interconnect_report_{timestamp}.xlsx"
            safe_name = os.path.basename(filename)
            uri = f"file:///{quote(safe_name)}"

            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({"count": len(fabrics), "summary": summary})
                ),
                mcp_types.EmbeddedResource(
                    type="resource",
                    resource=mcp_types.BlobResourceContents(
                        uri=uri,
                        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        blob=blob_b64
                    )
                )
            ]

        except Exception as ex:
            logger.error("Error getting Fabric Interconnect report:\n" + traceback.format_exc())
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": True,
                        "message": str(ex),
                        "trace": traceback.format_exc()
                    })
                )
            ]
