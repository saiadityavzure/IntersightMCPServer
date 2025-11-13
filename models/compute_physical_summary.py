from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime



# ---------------------------------------------------------
# Shared reusable nested models
# ---------------------------------------------------------

class MoRef(BaseModel):
    class_id: Optional[str]
    moid: Optional[str]
    object_type: Optional[str]
    link: Optional[str] = None


class Tag(BaseModel):
    key: Optional[str]
    value: Optional[str]
    propagated: Optional[bool] = None
    type: Optional[str] = None


class AlarmSummary(BaseModel):
    class_id: Optional[str]
    object_type: Optional[str]
    critical: Optional[int]
    health: Optional[str]
    info: Optional[int]
    suppressed: Optional[bool]
    suppressed_critical: Optional[int]
    suppressed_info: Optional[int]
    suppressed_warning: Optional[int]
    warning: Optional[int]


class IpAddress(BaseModel):
    class_id: Optional[str]
    object_type: Optional[str]
    address: Optional[str]
    category: Optional[str]
    default_gateway: Optional[str]
    dn: Optional[str]
    http_port: Optional[int]
    https_port: Optional[int]
    kvm_port: Optional[int]
    kvm_vlan: Optional[int]
    name: Optional[str]
    subnet: Optional[str]
    type: Optional[str]


# ---------------------------------------------------------
# Main PhysicalSummary Model (strictly matches SDK output)
# ---------------------------------------------------------

class ComputePhysicalSummary(BaseModel):
    # required
    moid: str
    name: str

    # simple fields
    class_id: Optional[str]
    object_type: Optional[str]
    account_moid: Optional[str]
    admin_power_state: Optional[str]
    asset_tag: Optional[str]
    available_memory: Optional[int]
    bios_post_complete: Optional[bool]
    chassis_id: Optional[str]
    connection_status: Optional[str]
    cooling_mode: Optional[str]
    cpu_capacity: Optional[float]
    create_time: Optional[datetime]
    device_mo_id: Optional[str]
    dn: Optional[str]
    domain_group_moid: Optional[str]
    fault_summary: Optional[int]
    firmware: Optional[str]
    front_panel_lock_state: Optional[str]
    hardware_uuid: Optional[str]
    has_e3_s_support: Optional[bool]
    ipv4_address: Optional[str]
    is_upgraded: Optional[bool]
    kvm_server_state_enabled: Optional[bool]
    kvm_vendor: Optional[str]
    last_power_state_changed_time: Optional[str]
    lifecycle: Optional[str]
    management_mode: Optional[str]
    memory_speed: Optional[str]
    mgmt_ip_address: Optional[str]
    mod_time: Optional[datetime]
    model: Optional[str]
    num_adaptors: Optional[int]
    num_cpu_cores: Optional[int]
    num_cpu_cores_enabled: Optional[int]
    num_cpus: Optional[int]
    num_eth_host_interfaces: Optional[int]
    num_fc_host_interfaces: Optional[int]
    num_threads: Optional[int]
    oper_power_state: Optional[str]
    oper_reason: Optional[List[Any]]
    oper_state: Optional[str]
    operability: Optional[str]
    package_version: Optional[str]
    personality: Optional[str]
    platform_type: Optional[str]
    presence: Optional[str]
    revision: Optional[str]
    rn: Optional[str]
    scaled_mode: Optional[str]
    serial: Optional[str]
    server_id: Optional[int]
    service_profile: Optional[str]
    shared_scope: Optional[str]
    slot_id: Optional[int]
    source_object_type: Optional[str]
    topology_scan_status: Optional[str]
    total_memory: Optional[int]
    tunneled_kvm: Optional[bool]
    user_label: Optional[str]
    uuid: Optional[str]
    vendor: Optional[str]

    # composite objects
    alarm_summary: Optional[AlarmSummary]
    ancestors: Optional[List[MoRef]]
    custom_permission_resources: Optional[List[Any]]
    equipment_chassis: Optional[Any]
    inventory_device_info: Optional[Any]
    inventory_parent: Optional[MoRef]
    kvm_ip_addresses: Optional[List[IpAddress]]
    owners: Optional[List[str]]
    parent: Optional[MoRef]
    permission_resources: Optional[List[MoRef]]
    registered_device: Optional[MoRef]
    tags: Optional[List[Tag]]
