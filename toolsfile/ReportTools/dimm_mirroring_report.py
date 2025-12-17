# C:\IntersightMCPServer\toolsfile\ReportTools\dimm_mirroring_report.py

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

from utils.intersight_rest import get_intersight_rest_session

logger = logging.getLogger(__name__)


def register_dimm_mirroring_tool(mcp: FastMCP):

    @mcp.tool(
        name="dimm_mirroring_tool",
        description="Fetch details about servers with DIMM mirroring enabled using BIOS policies, server profiles, and server inventory.",
        tags={"compute", "memory", "dimm", "bios", "report"},
        meta={"version": "1.0", "endpoint": "/bios/Policies"},
    )
    def dimm_mirroring_tool():
        try:
            # -------------------------------------------------------------------
            # STEP 1 — Create REST session
            # -------------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created successfully")

            # -------------------------------------------------------------------
            # STEP 2 — Query BIOS Policies where MirroringMode != platform-default
            # -------------------------------------------------------------------
            params = {
                "$filter": "MirroringMode ne 'platform-default'",
                "$select": "Moid,MirroringMode",
            }

            bios_url = f"{base_url}/api/v1/bios/Policies"
            bios_resp = session.get(bios_url, params=params)
            bios_resp.raise_for_status()
            bios_data = bios_resp.json()

            bios_moid_list = [x["Moid"] for x in bios_data.get("Results", [])]
            logger.info(f"BIOS policies with mirroring enabled: {bios_moid_list}")

            if not bios_moid_list:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No BIOS policies found with DIMM mirroring enabled."}),
                    )
                ]

            # -------------------------------------------------------------------
            # STEP 3 — Find Server Profiles using these BIOS Policies
            # -------------------------------------------------------------------
            profile_url = f"{base_url}/api/v1/server/Profiles"
            filter_query = " or ".join([f"PolicyBucket/Moid eq '{moid}'" for moid in bios_moid_list])

            params = {
                "$select": "Name,Moid",
                "$filter": filter_query,
            }

            profiles_resp = session.get(profile_url, params=params)
            profiles_resp.raise_for_status()
            profiles_data = profiles_resp.json()

            profile_moid_list = [x["Moid"] for x in profiles_data.get("Results", [])]
            logger.info(f"Server Profiles using mirroring BIOS policies: {profile_moid_list}")

            if not profile_moid_list:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No Server Profiles found using mirrored BIOS policies."}),
                    )
                ]

            # -------------------------------------------------------------------
            # STEP 4 — Find Servers associated with those Server Profiles
            # -------------------------------------------------------------------
            server_view_url = f"{base_url}/api/v1/view/Servers"
            server_filter = " or ".join([f"ServerProfile/Moid eq '{moid}'" for moid in profile_moid_list])

            params = {"$filter": server_filter}

            servers_resp = session.get(server_view_url, params=params)
            servers_resp.raise_for_status()
            servers_data = servers_resp.json()

            server_list = servers_data.get("Results", [])
            logger.info(f"Servers associated with BIOS mirroring: {len(server_list)}")

            # -------------------------------------------------------------------
            # STEP 5 — Extract Detailed Server Data
            # -------------------------------------------------------------------
            detailed_fields = [
                "AccountMoid", "Name", "Moid", "ModTime", "ServerHealth",
                "TotalMemory", "Model", "NumCpus", "NumEthHostInterfaces",
                "NumFcHostInterfaces", "MgmtIpAddress", "UserLabel",
            ]

            detailed_server_data = []
            for server in server_list:
                row = {field: server.get(field) for field in detailed_fields}
                detailed_server_data.append(row)

            if not detailed_server_data:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": "No servers found associated with mirrored BIOS policies."}),
                    )
                ]

            # -------------------------------------------------------------------
            # STEP 6 — Build Excel in-memory (NO server-side write)
            # -------------------------------------------------------------------
            df = pd.DataFrame(detailed_server_data)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="DIMM_Mirroring")

            excel_bytes = buf.getvalue()
            blob_b64 = base64.b64encode(excel_bytes).decode("utf-8")

            # Safe filename + valid URI
            filename = f"dimm_mirroring_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            safe_name = os.path.basename(filename)
            uri = f"file:///{quote(safe_name)}"

            # -------------------------------------------------------------------
            # STEP 7 — Summary Section
            # -------------------------------------------------------------------
            summary_keys = ["Name", "Model", "ServerHealth", "TotalMemory"]
            summary = [{k: d.get(k) for k in summary_keys} for d in detailed_server_data]

            # -------------------------------------------------------------------
            # Return: text + embedded resource
            # -------------------------------------------------------------------
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({
                        "count": len(detailed_server_data),
                        "summary": summary,
                    }),
                ),
                mcp_types.EmbeddedResource(
                    type="resource",
                    resource=mcp_types.BlobResourceContents(
                        uri=uri,
                        mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        blob=blob_b64,
                    ),
                ),
            ]

        except Exception as ex:
            logger.error("DIMM Mirroring Tool Error:\n" + traceback.format_exc())
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({
                        "error": True,
                        "message": str(ex),
                        "trace": traceback.format_exc(),
                    }),
                )
            ]
