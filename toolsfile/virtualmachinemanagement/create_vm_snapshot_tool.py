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


def register_create_vm_snapshot_tool(mcp: FastMCP):

    @mcp.tool(
        name="create_vm_snapshot",
        description="Triggers an ICO workflow to create a snapshot of a Virtual Machine.",
        tags={"vm", "snapshot", "ico", "workflow"},
        meta={"version": "1.0", "endpoint": "/workflow/WorkflowInfos"},
    )
    def create_vm_snapshot(
        vm_name_value: str,
        vm_snapshot_name_value: str,
        vm_snapshot_desc_value: str
    ):
        try:
            # --------------------------------------------------------------
            # 1. Establish REST session for Moid lookups
            # --------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created for VM snapshot workflow")

            # Helper to fetch Moid
            def fetch_moid(url):
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
                results = data.get("Results", [])
                if not results:
                    return None
                return results[0]["Moid"]

            # --------------------------------------------------------------
            # 2. Fetch Organization Moid
            # --------------------------------------------------------------
            org_url = f"{base_url}/api/v1/organization/Organizations?$filter=Name eq '{ORGANIZATION_NAME}'"
            org_moid = fetch_moid(org_url)

            if not org_moid:
                return json.dumps({"error": f"Organization '{ORGANIZATION_NAME}' not found."})

            logger.info(f"Organization Moid: {org_moid}")

            # --------------------------------------------------------------
            # 3. Fetch Workflow Definition Moid for "CreateVMSnapshot"
            # --------------------------------------------------------------
            wf_url = (
                f"{base_url}/api/v1/workflow/WorkflowDefinitions"
                f"?$filter=Name eq 'CreateVMSnapshot'"
            )
            wf_def_moid = fetch_moid(wf_url)

            if not wf_def_moid:
                return json.dumps({"error": "Workflow Definition 'CreateVMSnapshot' not found."})

            logger.info(f"Workflow Definition Moid: {wf_def_moid}")

            # --------------------------------------------------------------
            # 4. Construct workflow body (SDK)
            # --------------------------------------------------------------
            sdk_client = intersight_client_connection()
            wf_api = workflow_api.WorkflowApi(sdk_client)

            workflow_body = WorkflowWorkflowInfo(
                action="Start",
                name="CreateVMSnapshot",
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
                    "VmName": vm_name_value,
                    "SnapshotName": vm_snapshot_name_value,
                    "Description": vm_snapshot_desc_value
                }
            )

            logger.info(f"Snapshot Input Payload: {workflow_body.input}")

            # --------------------------------------------------------------
            # 5. Trigger ICO Workflow
            # --------------------------------------------------------------
            workflow = wf_api.create_workflow_workflow_info(workflow_body)

            workflow_status = workflow.get("WorkflowStatus") or workflow.get("workflow_status")
            workflow_moid = workflow.get("Moid")

            logger.info(
                f"Snapshot Workflow Triggered — Moid: {workflow_moid}, Status: {workflow_status}"
            )

            # --------------------------------------------------------------
            # 6. Return workflow details
            # --------------------------------------------------------------
            return json.dumps({
                "message": "Snapshot creation workflow submitted successfully.",
                "workflow_moid": workflow_moid,
                "workflow_status": workflow_status,
                "vm_name": vm_name_value,
                "snapshot_name": vm_snapshot_name_value,
                "snapshot_description": vm_snapshot_desc_value
            })

        except Exception as ex:
            logger.error("Error in create_vm_snapshot:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
