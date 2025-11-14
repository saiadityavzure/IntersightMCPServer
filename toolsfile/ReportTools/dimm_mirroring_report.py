import os
import json
import logging
import pandas as pd
import traceback
from datetime import datetime

from fastmcp import FastMCP

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
                "$select": "Moid,MirroringMode"
            }

            bios_url = f"{base_url}/api/v1/bios/Policies"
            bios_resp = session.get(bios_url, params=params)
            bios_resp.raise_for_status()
            bios_data = bios_resp.json()

            bios_moid_list = [x["Moid"] for x in bios_data.get("Results", [])]
            logger.info(f"BIOS policies with mirroring enabled: {bios_moid_list}")

            if not bios_moid_list:
                return json.dumps({"message": "No BIOS policies found with DIMM mirroring enabled."})

            # -------------------------------------------------------------------
            # STEP 3 — Find Server Profiles using these BIOS Policies
            # -------------------------------------------------------------------
            profile_url = f"{base_url}/api/v1/server/Profiles"

            filter_query = " or ".join([f"PolicyBucket/Moid eq '{moid}'" for moid in bios_moid_list])

            params = {
                "$select": "Name,Moid",
                "$filter": filter_query
            }

            profiles_resp = session.get(profile_url, params=params)
            profiles_resp.raise_for_status()
            profiles_data = profiles_resp.json()

            profile_moid_list = [x["Moid"] for x in profiles_data.get("Results", [])]
            logger.info(f"Server Profiles using mirroring BIOS policies: {profile_moid_list}")

            if not profile_moid_list:
                return json.dumps({"message": "No Server Profiles found using mirrored BIOS policies."})

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
                'AccountMoid', 'Name', 'Moid', 'ModTime', 'ServerHealth',
                'TotalMemory', 'Model', 'NumCpus', 'NumEthHostInterfaces',
                'NumFcHostInterfaces', 'MgmtIpAddress', 'UserLabel'
            ]

            detailed_server_data = []
            for server in server_list:
                row = {field: server.get(field) for field in detailed_fields}
                detailed_server_data.append(row)

            # -------------------------------------------------------------------
            # STEP 6 — Save report to /reports/
            # -------------------------------------------------------------------
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)

            filename = f"dimm_mirroring_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path = os.path.join(reports_dir, filename)

            df = pd.DataFrame(detailed_server_data)
            df.to_excel(output_path, index=False)

            absolute_path = os.path.abspath(output_path)

            # -------------------------------------------------------------------
            # STEP 7 — Summary Section
            # -------------------------------------------------------------------
            summary_keys = ["Name", "Model", "ServerHealth", "TotalMemory"]
            summary = [{k: d.get(k) for k in summary_keys} for d in detailed_server_data]

            return json.dumps({
                "count": len(detailed_server_data),
                "summary": summary,
                "download_link": absolute_path,
                "items": detailed_server_data
            })

        except Exception as ex:
            logger.error("DIMM Mirroring Tool Error:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
