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


def register_create_vm_tool(mcp: FastMCP):

    @mcp.tool(
        name="create_a_vm_through_ico",
        description="Triggers an Intersight Cloud Orchestrator workflow to provision a new Virtual Machine.",
        tags={"vm", "ico", "workflow", "compute"},
        meta={"version": "1.0", "endpoint": "/workflow/WorkflowInfos"},
    )
    def create_a_vm_through_ico(
        vm_name_value: str,
        vm_cpu_value: str,
        vm_mem_value: str,
        vm_network_value: str,
        cluster_name_value: str,
    ):
        try:
            # ------------------------------------------------------------------
            # 1) Create REST Session for Moid lookups
            # ------------------------------------------------------------------
            session, base_url = get_intersight_rest_session()
            logger.info("REST session created successfully for VM provisioning workflow")

            # ------------------------------------------------------------------
            # 2) Helper function to fetch MOID for any object
            # ------------------------------------------------------------------
            def fetch_moid(url):
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
                results = data.get("Results", [])
                if not results:
                    return None
                return results[0]["Moid"]

            # ------------------------------------------------------------------
            # 3) Fetch Organization Moid
            # ------------------------------------------------------------------
            org_url = f"{base_url}/api/v1/organization/Organizations?$filter=Name eq '{ORGANIZATION_NAME}'"
            org_moid = fetch_moid(org_url)
            if not org_moid:
                return json.dumps({"error": f"Organization '{ORGANIZATION_NAME}' not found."})

            logger.info(f"Organization Moid: {org_moid}")

            # ------------------------------------------------------------------
            # 4) Fetch Workflow Definition Moid
            # ------------------------------------------------------------------
            wf_def_url = (
                f"{base_url}/api/v1/workflow/WorkflowDefinitions"
                f"?$filter=Name eq 'ProvisionNewVM'"
            )
            wf_def_moid = fetch_moid(wf_def_url)

            if not wf_def_moid:
                return json.dumps({"error": "Workflow Definition 'ProvisionNewVM' not found."})

            logger.info(f"Workflow Definition Moid: {wf_def_moid}")

            # ------------------------------------------------------------------
            # 5) Build workflow payload using SDK
            # ------------------------------------------------------------------
            api_sdk = intersight_client_connection()
            wf_api = workflow_api.WorkflowApi(api_sdk)

            workflow_body = WorkflowWorkflowInfo(
                action="Start",
                name="ProvisionNewVM",
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
                    "Cluster": f"/Vzure-Frisco/host/{cluster_name_value}",
                    "VM_Name": vm_name_value,
                    "CPU": int(vm_cpu_value),
                    "Memory": int(vm_mem_value),
                    "Network": vm_network_value
                }
            )

            logger.info(f"VM Input Payload: {workflow_body.input}")

            # ------------------------------------------------------------------
            # 6) Trigger ICO Workflow
            # ------------------------------------------------------------------
            workflow = wf_api.create_workflow_workflow_info(workflow_body)
            workflow_status = workflow.get("WorkflowStatus") or workflow.get("workflow_status")

            logger.info(f"VM Workflow Triggered. Status: {workflow_status}, Moid: {workflow.get('Moid')}")

            return json.dumps({
                "message": "VM creation request submitted successfully.",
                "workflow_moid": workflow.get("Moid"),
                "workflow_status": workflow_status,
                "vm_name": vm_name_value,
                "cpu": vm_cpu_value,
                "memory": vm_mem_value,
                "network": vm_network_value,
                "cluster": cluster_name_value
            })

        except Exception as ex:
            logger.error("Error in create_a_vm_through_ico:\n" + traceback.format_exc())
            return json.dumps({
                "error": True,
                "message": str(ex),
                "trace": traceback.format_exc()
            })
