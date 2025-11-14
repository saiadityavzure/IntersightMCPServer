import json
import logging
import os
import pandas as pd
from datetime import datetime

from fastmcp import FastMCP
from utils.intersight_auth import intersight_client_connection
from intersight.api import compute_api
from intersight.exceptions import ApiException
import traceback

logger = logging.getLogger(__name__)


def register_server_data_report_tool(mcp: FastMCP):

    @mcp.tool(
        name="generate_server_data_report",
        description="Fetches server data (compute.PhysicalSummaries) and generates a downloadable XLSX report.",
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
                return json.dumps({"message": "No servers found."})

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

                for item in response.results:
                    alarm = item.alarm_summary
                    health = alarm.health if alarm else None

                    row = {
                        "Name": item.name,
                        "User Label": item.user_label,
                        "Health": health,
                        "Model": item.model,
                        "Memory Capacity": item.available_memory,
                        "Management Mode": item.management_mode,
                        "Management IP Address": item.mgmt_ip_address,
                        "Firmware Version": item.firmware,
                        "Serial": item.serial,
                        "CPUs": item.num_cpus,
                        "CPU Cores": item.num_cpu_cores,
                        "Memory Speed (MHz)": item.memory_speed,
                    }
                    server_rows.append(row)

            if not server_rows:
                return json.dumps({"message": "No server data found."})

            # Summary (like your FI tool)
            summary_fields = ["Name", "Health", "Model", "Firmware Version"]
            summary = [{key: row.get(key) for key in summary_fields} for row in server_rows]

            # Timestamp file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"server_data_report_{timestamp}.xlsx"

            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)

            output_path = os.path.join(reports_dir, filename)

            # Save XLSX
            df = pd.DataFrame(server_rows)
            df.to_excel(output_path, index=False)

            absolute_path = os.path.abspath(output_path)

            return json.dumps({
                "count": len(server_rows),
                "summary": summary,
                "download_link": absolute_path,
                "items": server_rows
            })

        except ApiException as ex:
            logger.error("Intersight API Error: " + str(ex))
            return json.dumps({"error": True, "message": str(ex)})

        except Exception as ex:
            logger.error("Unexpected Error:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
