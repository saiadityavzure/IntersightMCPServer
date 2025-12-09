import json
import logging
import traceback
import os
import pandas as pd
from datetime import datetime

from fastmcp import FastMCP
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
    def get_fabric_interconnect_report() -> str:
        """
        Returns:
            JSON string containing:
            - list of fabrics
            - summary fields
            - download link for the XLSX file
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

            fabric_list = response.get("results", [])
            fabrics = []

            for fi in fabric_list:
                orgs = [p["name"] for p in fi.get("permission_resources", [])]

                ports_total = fi.get("num_ether_ports", 0)
                ports_used = fi.get("num_ether_ports_configured", 0)

                row = {
                    "Name": fi.get("name"),
                    "Health": fi.get("alarm_summary", {}).get("health"),
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
                return json.dumps({"message": "No Fabric Interconnects found."})

            # Create the summary list
            summary_keys = ["Name", "Health", "Model", "Bundle Version"]
            summary = [{k: fi[k] for k in summary_keys} for fi in fabrics]

            # Create timestamped filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"fabric_interconnect_report_{timestamp}.xlsx"

            # Save under /reports/
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            output_path = os.path.join(reports_dir, filename)
            

            df = pd.DataFrame(fabrics)
            df.to_excel(output_path, index=False)

            absolute_path = os.path.abspath(output_path)

            return json.dumps({
                "count": len(fabrics),
                "summary": summary,
                "download_link": absolute_path,
                "items": fabrics
            })

        except Exception as ex:
            logger.error("Error getting Fabric Interconnect report:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
