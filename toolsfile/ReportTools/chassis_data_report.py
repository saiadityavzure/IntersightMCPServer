import json
import logging
import base64
import io
import pandas as pd
import traceback
from datetime import datetime

from fastmcp import FastMCP
from mcp import types as mcp_types  # ✅ important
import os
from urllib.parse import quote


from utils.intersight_auth import intersight_client_connection

import intersight.api.equipment_api
import intersight.api.chassis_api
import intersight.api.asset_api

logger = logging.getLogger(__name__)


def register_chassis_data_report_tool(mcp: FastMCP):

    @mcp.tool(
        name="generate_chassis_data_report",
        description="Fetches UCS Chassis information from Cisco Intersight.",
        tags={"chassis", "ucs", "report"},
        meta={"version": "1.0", "endpoint": "/equipment/Chassis"},
    )
    def generate_chassis_data_report():
        try:
            client = intersight_client_connection()

            api_chassis = intersight.api.equipment_api.EquipmentApi(client)
            api_profiles = intersight.api.chassis_api.ChassisApi(client)
            api_asset = intersight.api.asset_api.AssetApi(client)

            logger.info("Connected to Intersight for Chassis Data Report")

            count_resp = api_chassis.get_equipment_chassis_list(count=True)
            total_chassis = count_resp["count"]

            if total_chassis == 0:
                return [mcp_types.TextContent(type="text", text=json.dumps({"message": "No chassis found."}))]

            expand_query = (
                "LocatorLed($select=OperState),"
                "RegisteredDevice($select=PlatformType,ReadOnly,DeviceHostname,ConnectionStatus),"
                "PermissionResources($select=Name)"
            )

            select_query = (
                "Tags,PermissionResources,Name,AlarmSummary,ManagementMode,ChassisId,"
                "Model,Serial,LocatorLed,RegisteredDevice,ReadOnly,DeviceHostname,"
                "ConnectionStatus,DeviceMoId"
            )

            chassis_resp = api_chassis.get_equipment_chassis_list(
                orderby="Name asc",
                expand=expand_query,
                select=select_query,
                top=total_chassis
            )
            chassis_list = chassis_resp["results"]

            profiles_resp = api_profiles.get_chassis_profile_list(
                orderby="Name asc",
                expand=expand_query
            )
            profiles_list = profiles_resp["results"]

            contract_filter = "(DeviceType eq 'CiscoUcsChassis')"
            contract_resp = api_asset.get_asset_device_contract_information_list(filter=contract_filter)
            contract_list = contract_resp["results"]

            rows = []
            for chassis in chassis_list:
                name = chassis.get("name")
                health = chassis.get("alarm_summary", {}).get("health")
                mgmt_mode = chassis.get("management_mode")
                chassis_id = chassis.get("chassis_id")
                model = chassis.get("model")
                serial = chassis.get("serial")
                orgs = [p["name"] for p in chassis.get("permission_resources", [])]

                ucs_domain = None
                reg_dev = chassis.get("registered_device")
                if reg_dev:
                    ucs_domain = reg_dev.get("device_hostname", [None])[0]

                chassis_profile = None
                for profile in profiles_list:
                    assigned = profile.get("assigned_chassis")
                    if assigned and assigned.get("moid") == chassis.get("moid"):
                        chassis_profile = profile.get("name")
                        break

                contract_status = None
                for contract in contract_list:
                    if reg_dev and reg_dev.get("moid") == contract.get("registered_device", {}).get("moid"):
                        contract_status = contract.get("contract_status")
                        break

                rows.append({
                    "Name": name,
                    "Health": health,
                    "Management Mode": mgmt_mode,
                    "Chassis ID": chassis_id,
                    "UCS Domain": ucs_domain,
                    "Model": model,
                    "Serial Number": serial,
                    "Contract Status": contract_status,
                    "Organizations": orgs,
                    "Profile": chassis_profile,
                })

            if not rows:
                return [mcp_types.TextContent(type="text", text=json.dumps({"message": "No chassis data available."}))]

            summary_keys = ["Name", "Health", "Management Mode", "UCS Domain", "Model"]
            summary = [{k: r[k] for k in summary_keys} for r in rows]

            # ✅ Build Excel in-memory (NO server-side reports/ write)
            df = pd.DataFrame(rows)
            df["Organizations"] = df["Organizations"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Chassis")

            excel_bytes = buf.getvalue()
            blob_b64 = base64.b64encode(excel_bytes).decode("utf-8")

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"chassis_data_report_{timestamp}.xlsx"
            safe_name = os.path.basename(filename)
            uri = f"file:///{quote(safe_name)}"

            # ✅ Return: text + embedded resource (client will store to MEDIA_ROOT)
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({"count": len(rows), "summary": summary})
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
            logger.error("Error generating Chassis report:\n" + traceback.format_exc())
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
