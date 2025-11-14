import os
import json
import logging
import pandas as pd
import traceback
from datetime import datetime

from fastmcp import FastMCP

from utils.intersight_auth import intersight_client_connection

import intersight.api.cond_api
from intersight.exceptions import ApiException

logger = logging.getLogger(__name__)


def register_intersight_alarm_tool(mcp: FastMCP):

    @mcp.tool(
        name="get_intersight_alarms",
        description="Fetch Critical and Warning alarms from Cisco Intersight after the provided date, and generate an XLSX report.",
        tags={"alarms", "intersight", "monitoring", "report"},
        meta={"version": "1.0", "endpoint": "/cond/Alarms"},
    )
    def get_intersight_alarms(from_date: str):
        """
        from_date format: YYYY-MM-DD
        """

        try:
            # Connect using your authentication wrapper
            client = intersight_client_connection()
            cond_api = intersight.api.cond_api.CondApi(client)

            logger.info(f"Fetching Intersight alarms since: {from_date}")

            # -----------------------------------------------------------
            # Convert provided date to Intersight-compatible ISO format
            # -----------------------------------------------------------
            dt = datetime.strptime(from_date, "%Y-%m-%d")
            iso_dt = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Build filter for Critical + Warning alarms
            filter_crit = f"Severity eq 'Critical' and Acknowledge eq 'None' and LastTransitionTime gt {iso_dt}"
            filter_warn = f"Severity eq 'Warning' and Acknowledge eq 'None' and LastTransitionTime gt {iso_dt}"

            combined_filter = f"({filter_crit}) or ({filter_warn})"

            # -----------------------------------------------------------
            # Fetch alarms from Intersight
            # -----------------------------------------------------------
            resp = cond_api.get_cond_alarm_list(filter=combined_filter)
            alarm_results = resp.results

            if not alarm_results:
                return json.dumps({
                    "message": f"No alarms found after {from_date}"
                })

            # -----------------------------------------------------------
            # Clean + extract summary alarm data
            # -----------------------------------------------------------
            summary_keys = ["name", "severity", "description", "last_transition_time"]
            summary_list = []

            for alarm in alarm_results:
                entry = {}
                for k in summary_keys:
                    if k in alarm:
                        entry[k] = alarm[k]
                summary_list.append(entry)

            # Format datetime fields
            for a in summary_list:
                ts = a.get("last_transition_time")
                if isinstance(ts, datetime):
                    a["last_transition_time"] = ts.strftime("%Y-%m-%d %H:%M:%S")

            # Sort by time desc
            try:
                summary_list.sort(
                    key=lambda x: datetime.strptime(x["last_transition_time"], "%Y-%m-%d %H:%M:%S"),
                    reverse=True
                )
            except Exception as e:
                logger.error("Sort failed:", e)

            # -----------------------------------------------------------
            # Build detailed alarm list
            # -----------------------------------------------------------
            detailed_keys = [
                "account_moid", "acknowledge", "affected_mo_display_name", "ancestor_mo_id",
                "ancestor_mo_type", "code", "creation_time", "description", "last_transition_time",
                "moid", "name", "severity", "suppressed"
            ]

            detailed_list = []

            for alarm in alarm_results:
                entry = {}
                for k in detailed_keys:
                    entry[k] = alarm.get(k)

                # Normalize datetime fields
                if isinstance(entry.get("creation_time"), datetime):
                    entry["creation_time"] = entry["creation_time"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(entry.get("last_transition_time"), datetime):
                    entry["last_transition_time"] = entry["last_transition_time"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                detailed_list.append(entry)

            # Sort detailed list
            try:
                detailed_list.sort(
                    key=lambda x: datetime.strptime(x["last_transition_time"], "%Y-%m-%d %H:%M:%S")
                    if x.get("last_transition_time") else datetime.min,
                    reverse=True
                )
            except:
                pass

            # -----------------------------------------------------------
            # Save Excel report under /reports/
            # -----------------------------------------------------------
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)

            filename = f"intersight_alarms_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = os.path.join(reports_dir, filename)

            df = pd.DataFrame(detailed_list)
            df.to_excel(file_path, index=False)

            absolute_path = os.path.abspath(file_path)

            # -----------------------------------------------------------
            # Return MCP response
            # -----------------------------------------------------------
            return json.dumps({
                "count": len(summary_list),
                "summary": summary_list[:10],   # Top 10 alarms
                "download_link": absolute_path,
                "items": detailed_list
            })

        except ApiException as ex:
            return json.dumps({"error": True, "message": str(ex)})
        except Exception as ex:
            logger.error("Unexpected Alarm Tool Error:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
