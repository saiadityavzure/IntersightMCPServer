# C:\IntersightMCPServer\toolsfile\ReportTools\server_data_report.py

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
from intersight.api import compute_api
from intersight.exceptions import ApiException

logger = logging.getLogger(__name__)


def register_server_data_report_tool(mcp: FastMCP):

    @mcp.tool(
        name="generate_server_data_report",
        description="Fetches server data (compute.PhysicalSummaries).",
        tags={"compute", "server", "report"},
        meta={"version": "1.0", "endpoint": "/compute/PhysicalSummaries"},
    )
    def generate_server_data_report():
        try:
            # Connect to Intersight
            client = intersight_client_connection()
            compute = compute_api.ComputeApi(client)

            logger.info("Connected to Intersight successfully for Server Data Report")

            # Get count
            count_resp = compute.get_compute_physical_summary_list(count=True)
            total = count_resp["count"]

            if total == 0:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No servers found."})
                    )
                ]

            batch_size = 100
            loops = total // batch_size

            select_query = (
                "Name,UserLabel,AlarmSummary,Model,AvailableMemory,ManagementMode,"
                "Serial,NumCpus,NumCpuCores,MemorySpeed,MgmtIpAddress,Firmware"
            )

            server_rows = []

            # Loop through all servers
            for i in range(loops + 1):
                skip = i * batch_size
                response = compute.get_compute_physical_summary_list(
                    select=select_query,
                    orderby="Name asc",
                    skip=skip
                )

                # NOTE: SDK returns response.results as objects
                for item in getattr(response, "results", []) or []:
                    alarm = getattr(item, "alarm_summary", None)
                    health = getattr(alarm, "health", None) if alarm else None

                    server_rows.append({
                        "Name": getattr(item, "name", None),
                        "User Label": getattr(item, "user_label", None),
                        "Health": health,
                        "Model": getattr(item, "model", None),
                        "Memory Capacity": getattr(item, "available_memory", None),
                        "Management Mode": getattr(item, "management_mode", None),
                        "Management IP Address": getattr(item, "mgmt_ip_address", None),
                        "Firmware Version": getattr(item, "firmware", None),
                        "Serial": getattr(item, "serial", None),
                        "CPUs": getattr(item, "num_cpus", None),
                        "CPU Cores": getattr(item, "num_cpu_cores", None),
                        "Memory Speed (MHz)": getattr(item, "memory_speed", None),
                    })

            if not server_rows:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No server data found."})
                    )
                ]

            # Summary
            summary_fields = ["Name", "Health", "Model", "Firmware Version"]
            summary = [{k: r.get(k) for k in summary_fields} for r in server_rows]

            # Build Excel in-memory
            df = pd.DataFrame(server_rows)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Servers")

            excel_bytes = buf.getvalue()
            blob_b64 = base64.b64encode(excel_bytes).decode("utf-8")

            # Safe filename + valid URI
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"server_data_report_{timestamp}.xlsx"
            safe_name = os.path.basename(filename)
            uri = f"file:///{quote(safe_name)}"

            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({"count": len(server_rows), "summary": summary})
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

        except ApiException as ex:
            logger.error("Intersight API Error: " + str(ex))
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({"error": True, "message": str(ex)})
                )
            ]

        except Exception as ex:
            logger.error("Unexpected Error:\n" + traceback.format_exc())
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
