# vm_utilization_tools.py

import logging
import traceback

from fastmcp import FastMCP
from utils.intersight_rest import get_intersight_rest_session

logger = logging.getLogger(__name__)


# --------------------------------------------------------------
# Helper: Extract CPU & Memory data
# --------------------------------------------------------------
def extract_vm_utilization_info(vm_list):
    """
    Extracts Name, CpuUtilization, MemoryUtilization from the Search API results.
    """
    return [
        {
            "Name": vm.get("Name"),
            "CpuUtilization": vm.get("CpuUtilization"),
            "MemoryUtilization": vm.get("MemoryUtilization"),
        }
        for vm in vm_list
    ]


def top_10_cpu(vms):
    return sorted(vms, key=lambda x: x.get("CpuUtilization", 0), reverse=True)[:10]


def top_10_memory(vms):
    return sorted(vms, key=lambda x: x.get("MemoryUtilization", 0), reverse=True)[:10]


# ==============================================================
# Register Tools
# ==============================================================
def register_vm_utilization_tools(mcp: FastMCP):

    # ----------------------------------------------------------
    # GET TOP 10 CPU UTILIZATION
    # ----------------------------------------------------------
    @mcp.tool(
        name="get_vm_cpu_utilization",
        description="Retrieves CPU utilization metrics for the top 10 VMs across the infrastructure.",
        tags={"virtualization", "vm", "utilization", "cpu"},
        meta={"version": "1.0"}
    )
    def get_vm_cpu_utilization():

        try:
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created for CPU utilization query")

            url = (
                f"{base_url}/api/v1/search/SearchItems"
                "?$inlinecount=allpages"
                "&$skip=0"
                "&$top=500"
                "&$filter=(IndexMotypes eq virtualization.BaseVirtualMachine)"
                " and (Provider in (VMwarevSphere))"
                " and (IsTemplate ne 'true')"
                "&$orderby=Name desc"
            )

            logger.debug(f"GET → {url}")

            response = session.get(url)

            if not response.ok:
                return None, {
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

            results = response.json().get("Results", [])

            vm_info = extract_vm_utilization_info(results)
            top_vms = top_10_cpu(vm_info)

            return None, {
                "count": len(top_vms),
                "metric": "CPU Utilization",
                "items": top_vms
            }

        except Exception:
            logger.error("Error in get_vm_cpu_utilization:\n" + traceback.format_exc())
            return {"error": "Unexpected error"}


    # ----------------------------------------------------------
    # GET TOP 10 MEMORY UTILIZATION
    # ----------------------------------------------------------
    @mcp.tool(
        name="get_vm_memory_utilization",
        description="Retrieves Memory utilization metrics for the top 10 VMs across the infrastructure.",
        tags={"virtualization", "vm", "utilization", "memory"},
        meta={"version": "1.0"}
    )
    def get_vm_memory_utilization():

        try:
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created for Memory utilization query")

            url = (
                f"{base_url}/api/v1/search/SearchItems"
                "?$inlinecount=allpages"
                "&$skip=0"
                "&$top=500"
                "&$filter=(IndexMotypes eq virtualization.BaseVirtualMachine)"
                " and (Provider in (VMwarevSphere))"
                " and (IsTemplate ne 'true')"
                "&$orderby=Name desc"
            )

            logger.debug(f"GET → {url}")

            response = session.get(url)

            if not response.ok:
                return None, {
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

            results = response.json().get("Results", [])

            vm_info = extract_vm_utilization_info(results)
            top_vms = top_10_memory(vm_info)

            return None, {
                "count": len(top_vms),
                "metric": "Memory Utilization",
                "items": top_vms
            }

        except Exception:
            logger.error("Error in get_vm_memory_utilization:\n" + traceback.format_exc())
            return {"error": "Unexpected error"}
