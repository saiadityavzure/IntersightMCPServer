# power_vm_tools.py

import logging
import traceback
import json

from fastmcp import FastMCP
from utils.intersight_rest import get_intersight_rest_session
from utils.intersight_auth import intersight_client_connection

import intersight
import intersight.api.virtualization_api

logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Helper: Get VM Moid by Name (SDK Lookup)
# -----------------------------------------------------
def get_vm_moid_by_name(vm_name: str):
    """
    Returns VM Moid using Intersight SDK.
    """
    try:
        api = intersight_client_connection()
        vm_api = intersight.api.virtualization_api.VirtualizationApi(api)

        vm_list = vm_api.get_virtualization_virtual_machine_list(
            filter=f"Name eq '{vm_name}'"
        ).results

        if not vm_list:
            return None

        return vm_list[0].moid

    except Exception:
        logger.error("Error in get_vm_moid_by_name:\n" + traceback.format_exc())
        return None


# =====================================================
# Register Power Tools
# =====================================================
def register_vm_power_tools(mcp: FastMCP):

    # ---------------------------------------------------------
    # POWER ON VM
    # ---------------------------------------------------------
    @mcp.tool(
        name="power_on_a_vm",
        description="Powers ON a Virtual Machine via Intersight REST API.",
        tags={"virtualization", "vm", "power", "on"},
        meta={"version": "1.0"}
    )
    def power_on_a_vm(vm_name: str):

        try:
            # 1) Get REST session
            session, base_url = get_intersight_rest_session()
            logger.info(f"REST session created for powering ON '{vm_name}'")

            # 2) Find VM Moid
            vm_moid = get_vm_moid_by_name(vm_name)
            if not vm_moid:
                return {"error": f"VM '{vm_name}' not found"}

            url = f"{base_url}/api/v1/virtualization/VirtualMachines/{vm_moid}"
            payload = {
                "Action": "PowerState",
                "PowerState": "PowerOn"
            }

            logger.debug(f"[VM POWER ON] POST {url} Payload: {payload}")
            response = session.post(url, json=payload)

            if response.ok:
                return None, {
                    "status": "success",
                    "message": f"VM '{vm_name}' has been powered ON successfully"
                }
            else:
                return None, {
                    "error": f"{response.status_code} {response.reason}",
                    "details": response.text
                }

        except Exception as ex:
            logger.error("Error in power_on_a_vm:\n" + traceback.format_exc())
            return {"error": str(ex)}


    # ---------------------------------------------------------
    # POWER OFF VM
    # ---------------------------------------------------------
    @mcp.tool(
        name="power_off_a_vm",
        description="Powers OFF a Virtual Machine via Intersight REST API.",
        tags={"virtualization", "vm", "power", "off"},
        meta={"version": "1.0"}
    )
    def power_off_a_vm(vm_name: str):

        try:
            # 1) REST session
            session, base_url = get_intersight_rest_session()
            logger.info(f"REST session created for powering OFF '{vm_name}'")

            # 2) Lookup VM Moid
            vm_moid = get_vm_moid_by_name(vm_name)
            if not vm_moid:
                return {"error": f"VM '{vm_name}' not found"}

            url = f"{base_url}/api/v1/virtualization/VirtualMachines/{vm_moid}"
            payload = {
                "Action": "PowerState",
                "PowerState": "PowerOff"
            }

            logger.debug(f"[VM POWER OFF] POST {url} Payload: {payload}")
            response = session.post(url, json=payload)

            if response.ok:
                return None, {
                    "status": "success",
                    "message": f"VM '{vm_name}' has been powered OFF successfully"
                }
            else:
                return None, {
                    "error": f"{response.status_code} {response.reason}",
                    "details": response.text
                }

        except Exception as ex:
            logger.error("Error in power_off_a_vm:\n" + traceback.format_exc())
            return {"error": str(ex)}
