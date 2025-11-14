import json
import logging
import traceback

from fastmcp import FastMCP

from utils.intersight_auth import intersight_client_connection
from utils.intersight_rest import get_intersight_rest_session

import intersight
from intersight.api import workflow_api
from intersight.model.workflow_workflow_info import WorkflowWorkflowInfo
from intersight.model.workflow_workflow_definition_relationship import WorkflowWorkflowDefinitionRelationship
from intersight.model.mo_base_mo_relationship import MoBaseMoRelationship

logger = logging.getLogger(__name__)

ORGANIZATION_NAME = "default"


def register_modify_vm_network_tool(mcp: FastMCP):

    @mcp.tool(
        name="modify_vm_network",
        description="Triggers an ICO workflow to add a network to a Virtual Machine.",
        tags={"vm", "network", "ico", "workflow"},
        meta={"version": "1.0", "endpoint": "/workflow/WorkflowInfos"},
    )
    def modify_vm_network(
        vm_name_value: str,
        vm_network_value: str
    ):
        try:
            # ------------------------------------------------------------------
            # 1. Establish REST session for Moid lookups
            # ------------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created for ModifyVM workflow")

            # Helper to fetch MOID
            def fetch_moid(url):
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
                results = data.get("Results", [])
                if not results:
                    return None
                return results[0]["Moid"]

            # ------------------------------------------------------------------
            # 2. Fetch Organization Moid
            # ------------------------------------------------------------------
            org_url = f"{base_url}/api/v1/organization/Organizations?$filter=Name eq '{ORGANIZATION_NAME}'"
            org_moid = fetch_moid(org_url)

            if not org_moid:
                return json.dumps({"error": f"Organization '{ORGANIZATION_NAME}' not found."})

            logger.info(f"Organization Moid: {org_moid}")

            # ------------------------------------------------------------------
            # 3. Fetch Workflow Definition (ModifyVM)
            # ------------------------------------------------------------------
            wf_url = (
                f"{base_url}/api/v1/workflow/WorkflowDefinitions"
                f"?$filter=Name eq 'ModifyVM'"
            )
            wf_def_moid = fetch_moid(wf_url)

            if not wf_def_moid:
                return json.dumps({"error": "Workflow Definition 'ModifyVM' not found."})

            logger.info(f"Workflow Definition Moid: {wf_def_moid}")

            # ------------------------------------------------------------------
            # 4. Build VM path (owner-specific logic)
            # ------------------------------------------------------------------
            owner_name = ""
            if vm_name_value == "Win_Dev01":
                owner_name = "/Rakesh"

            vm_path = f"/Vzure-Frisco/vm{owner_name}/{vm_name_value}"

            # ------------------------------------------------------------------
            # 5. Build workflow payload using SDK client
            # ------------------------------------------------------------------
            sdk_client = intersight_client_connection()
            wf_api = workflow_api.WorkflowApi(sdk_client)

            workflow_body = WorkflowWorkflowInfo(
                action="Start",
                name="ModifyVM",
                associated_object=MoBaseMoRelationship(
                    class_id="mo.MoRef",
                    moid=org_moid,
                    object_type="organization.Organization"
                ),
                workflow_definition=WorkflowWorkflowDefinitionRelationship(
                    class_id="mo.MoRef",
                    moid=wf_def_moid,
                    object_type="workflow.WorkflowDefinition"
                ),
                input={
                    "VirtualMachine": vm_path,
                    "Network": vm_network_value
                }
            )

            logger.info(f"Modify VM Payload: {workflow_body.input}")

            # ------------------------------------------------------------------
            # 6. Trigger ICO workflow
            # ------------------------------------------------------------------
            workflow = wf_api.create_workflow_workflow_info(workflow_body)

            workflow_status = workflow.get("WorkflowStatus") or workflow.get("workflow_status")
            workflow_moid = workflow.get("Moid")

            logger.info(
                f"ModifyVM Workflow Triggered — Moid: {workflow_moid}, Status: {workflow_status}"
            )

            # ------------------------------------------------------------------
            # 7. Return response
            # ------------------------------------------------------------------
            return json.dumps({
                "message": "Modify VM Network workflow submitted successfully.",
                "vm_name": vm_name_value,
                "vm_network": vm_network_value,
                "workflow_moid": workflow_moid,
                "workflow_status": workflow_status
            })

        except Exception as ex:
            logger.error("Error in modify_vm_network:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
