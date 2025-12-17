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
import intersight.api.cond_api
from intersight.exceptions import ApiException

logger = logging.getLogger(__name__)


def register_intersight_alarm_tool(mcp: FastMCP):

    @mcp.tool(
        name="get_intersight_alarms",
        description="Fetch Critical and Warning alarms from Cisco Intersight after the provided date.",
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

            # Convert provided date to Intersight-compatible ISO format
            dt = datetime.strptime(from_date, "%Y-%m-%d")
            iso_dt = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Build filter for Critical + Warning alarms
            filter_crit = (
                "Severity eq 'Critical' and Acknowledge eq 'None' and "
                f"LastTransitionTime gt {iso_dt}"
            )
            filter_warn = (
                "Severity eq 'Warning' and Acknowledge eq 'None' and "
                f"LastTransitionTime gt {iso_dt}"
            )
            combined_filter = f"({filter_crit}) or ({filter_warn})"

            # Fetch alarms from Intersight
            resp = cond_api.get_cond_alarm_list(filter=combined_filter)
            alarm_results = getattr(resp, "results", []) or []

            if not alarm_results:
                return [
                    mcp_types.TextContent(
                        type="text",
                        text=json.dumps({"message": f"No alarms found after {from_date}"})
                    )
                ]

            # Summary (top fields)
            summary_keys = ["name", "severity", "description", "last_transition_time"]
            summary_list = []
            for alarm in alarm_results:
                entry = {}
                for k in summary_keys:
                    # Some SDK objects behave like dicts, some like attrs; be tolerant
                    try:
                        entry[k] = alarm.get(k)  # dict-like
                    except Exception:
                        entry[k] = getattr(alarm, k, None)  # attr-like
                summary_list.append(entry)

            # Normalize + format datetime fields
            for a in summary_list:
                ts = a.get("last_transition_time")
                if isinstance(ts, datetime):
                    a["last_transition_time"] = ts.strftime("%Y-%m-%d %H:%M:%S")

            # Sort by time desc (best-effort)
            try:
                summary_list.sort(
                    key=lambda x: datetime.strptime(x["last_transition_time"], "%Y-%m-%d %H:%M:%S")
                    if x.get("last_transition_time") else datetime.min,
                    reverse=True
                )
            except Exception as e:
                logger.warning(f"Summary sort failed: {e}")

            # Detailed list
            detailed_keys = [
                "account_moid", "acknowledge", "affected_mo_display_name", "ancestor_mo_id",
                "ancestor_mo_type", "code", "creation_time", "description", "last_transition_time",
                "moid", "name", "severity", "suppressed"
            ]

            detailed_list = []
            for alarm in alarm_results:
                entry = {}
                for k in detailed_keys:
                    try:
                        entry[k] = alarm.get(k)  # dict-like
                    except Exception:
                        entry[k] = getattr(alarm, k, None)  # attr-like

                # Normalize datetime fields
                if isinstance(entry.get("creation_time"), datetime):
                    entry["creation_time"] = entry["creation_time"].strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(entry.get("last_transition_time"), datetime):
                    entry["last_transition_time"] = entry["last_transition_time"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                detailed_list.append(entry)

            # Sort detailed list (best-effort)
            try:
                detailed_list.sort(
                    key=lambda x: datetime.strptime(x["last_transition_time"], "%Y-%m-%d %H:%M:%S")
                    if x.get("last_transition_time") else datetime.min,
                    reverse=True
                )
            except Exception as e:
                logger.warning(f"Detailed sort failed: {e}")

            # Build Excel in-memory (NO server-side write)
            df = pd.DataFrame(detailed_list)

            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Alarms")

            excel_bytes = buf.getvalue()
            blob_b64 = base64.b64encode(excel_bytes).decode("utf-8")

            # Safe filename + valid URI
            filename = f"intersight_alarms_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
            safe_name = os.path.basename(filename)
            uri = f"file:///{quote(safe_name)}"

            # Return MCP response: text + embedded file
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({
                        "count": len(summary_list),
                        "summary": summary_list[:10],   # Top 10 alarms
                    })
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
            return [
                mcp_types.TextContent(
                    type="text",
                    text=json.dumps({"error": True, "message": str(ex)})
                )
            ]

        except Exception as ex:
            logger.error("Unexpected Alarm Tool Error:\n" + traceback.format_exc())
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
