# vm_powerstatus_tool.py

import logging
import traceback
import pandas as pd
import os
from datetime import datetime

from fastmcp import FastMCP
from utils.intersight_rest import get_intersight_rest_session

logger = logging.getLogger(__name__)


# ====================================================================
# Register VM PowerState Report Tool
# ====================================================================
def register_vm_powerstatus_tool(mcp: FastMCP):

    @mcp.tool(
        name="get_virtual_machines_powerstatus",
        description="Retrieve VMs by power state (on/off). Returns top 10 summary.",
        tags={"virtualization", "vm", "powerstate", "report"},
        meta={"version": "1.0", "endpoint": "/virtualization/VirtualMachines"}
    )
    def get_virtual_machines_powerstatus(power_state: str):
        """
        power_state: "on" or "off"
        """

        try:
            # --------------------------------------------------------------
            # Create REST session
            # --------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info(f"REST session established for VM powerstate query ({power_state})")

            # --------------------------------------------------------------
            # Validate input power state
            # --------------------------------------------------------------
            power_state_map = {
                "on": "PowerOn",
                "off": "PowerOff",
            }

            if power_state not in power_state_map:
                return {"error": f"Invalid power_state: {power_state}. Use 'on' or 'off'."}

            intersight_state = power_state_map[power_state]

            url = f"{base_url}/api/v1/virtualization/VirtualMachines"
            params = {
                "$select": "Name,PowerState",
                "$filter": f"PowerState eq '{intersight_state}'"
            }

            logger.debug(f"Querying Intersight → {url} | params={params}")

            # --------------------------------------------------------------
            # Perform API Call
            # --------------------------------------------------------------
            response = session.get(url, params=params)

            if not response.ok:
                return {
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

            vm_results = response.json().get("Results", [])
            logger.info(f"Found {len(vm_results)} VMs with PowerState '{intersight_state}'")

            # --------------------------------------------------------------
            # Build VM list
            # --------------------------------------------------------------
            items = [
                {"Name": vm.get("Name"), "PowerState": vm.get("PowerState")}
                for vm in vm_results
            ]

            # --------------------------------------------------------------
            # Save Excel report under /reports/
            # --------------------------------------------------------------
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"vm_powerstate_report_{power_state}_{timestamp}.xlsx"
            output_path = os.path.join(reports_dir, filename)

            df = pd.DataFrame(items)
            df.to_excel(output_path, index=False)

            absolute_path = os.path.abspath(output_path)

            # --------------------------------------------------------------
            # Build summary of top 10
            # --------------------------------------------------------------
            summary = items[:10]

            # --------------------------------------------------------------
            # Final output (same format as Fabric Interconnect Tool)
            # --------------------------------------------------------------
            return {
                "count": len(items),
                "summary": summary,
                "download_link": absolute_path,
                "items": items
            }

        except Exception:
            logger.error("Error in get_virtual_machines_powerstatus:\n" + traceback.format_exc())
            return {
                "error": True,
                "message": "Unexpected error occurred",
                "trace": traceback.format_exc()
            }
