import json
import logging
import traceback

from fastmcp import FastMCP

from utils.intersight_rest import get_intersight_rest_session
from utils.intersight_auth import intersight_client_connection

import intersight
from intersight.api import workflow_api
from intersight.model.workflow_workflow_info import WorkflowWorkflowInfo
from intersight.model.workflow_workflow_definition_relationship import WorkflowWorkflowDefinitionRelationship
from intersight.model.mo_base_mo_relationship import MoBaseMoRelationship

logger = logging.getLogger(__name__)

ORGANIZATION_NAME = "default"


def register_migrate_vm_tool(mcp: FastMCP):

    @mcp.tool(
        name="migrate_a_vm",
        description="Triggers an ICO workflow to migrate a Virtual Machine between hosts in the same cluster.",
        tags={"vm", "migration", "ico", "workflow"},
        meta={"version": "1.0", "endpoint": "/workflow/WorkflowInfos"},
    )
    def migrate_a_vm(
        vm_name_value: str,
        vm_target_host_value: str,
        vm_target_datastore_value: str
    ):
        try:
            # -------------------------------------------------------------
            # 1. REST session for Organization + WorkflowDefinition MOIDs
            # -------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created for VM migration workflow")

            # Helper to fetch MOID from REST
            def fetch_moid(url):
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
                results = data.get("Results", [])
                if not results:
                    return None
                return results[0]["Moid"]

            # -------------------------------------------------------------
            # 2. Fetch Organization Moid
            # -------------------------------------------------------------
            org_url = f"{base_url}/api/v1/organization/Organizations?$filter=Name eq '{ORGANIZATION_NAME}'"
            org_moid = fetch_moid(org_url)

            if not org_moid:
                return json.dumps({"error": f"Organization '{ORGANIZATION_NAME}' not found."})

            logger.info(f"Organization Moid: {org_moid}")

            # -------------------------------------------------------------
            # 3. Fetch Workflow Definition Moid for MigrateVM
            # -------------------------------------------------------------
            wf_url = (
                f"{base_url}/api/v1/workflow/WorkflowDefinitions"
                f"?$filter=Name eq 'MigrateVM'"
            )
            wf_def_moid = fetch_moid(wf_url)

            if not wf_def_moid:
                return json.dumps({"error": "Workflow Definition 'MigrateVM' not found."})

            logger.info(f"Workflow Definition Moid: {wf_def_moid}")

            # -------------------------------------------------------------
            # 4. Build VM Reference Path
            # -------------------------------------------------------------
            vm_path = f"/Vzure-Frisco/vm/{vm_name_value}"

            # -------------------------------------------------------------
            # 5. Build migration payload using SDK
            # -------------------------------------------------------------
            sdk_client = intersight_client_connection()
            wf_api = workflow_api.WorkflowApi(sdk_client)

            workflow_body = WorkflowWorkflowInfo(
                action="Start",
                name="MigrateVM",
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
                    "VmName": vm_path,
                    "MoveVirtualMachineType": {
                        "MoveVirtualMachineOptions": "ComputeStorage",
                        "TargetDatacenter": "/Vzure-Frisco",
                        "Datastore": f"/Vzure-Frisco/datastore/{vm_target_datastore_value}",
                        "Host": vm_target_host_value,
                    }
                }
            )

            logger.info(f"Migrate VM Payload: {workflow_body.input}")

            # -------------------------------------------------------------
            # 6. Trigger Migration Workflow
            # -------------------------------------------------------------
            workflow = wf_api.create_workflow_workflow_info(workflow_body)
            workflow_status = workflow.get("WorkflowStatus") or workflow.get("workflow_status")
            workflow_moid = workflow.get("Moid")

            logger.info(
                f"MigrateVM Workflow Triggered — Moid: {workflow_moid}, Status: {workflow_status}"
            )

            # -------------------------------------------------------------
            # 7. MCP JSON Response
            # -------------------------------------------------------------
            return json.dumps({
                "message": "VM migration workflow submitted successfully.",
                "vm_name": vm_name_value,
                "target_host": vm_target_host_value,
                "target_datastore": vm_target_datastore_value,
                "workflow_moid": workflow_moid,
                "workflow_status": workflow_status
            })

        except Exception as ex:
            logger.error("Error in migrate_a_vm:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
