from pydantic import BaseModel
from typing import List, Optional, Any


class MoRef(BaseModel):
    ClassId: Optional[str]
    Moid: Optional[str]
    ObjectType: Optional[str]
    link: Optional[str] = None


class Tag(BaseModel):
    Key: Optional[str]
    Value: Optional[str]


class PermissionResource(MoRef):
    """Alias for clarity; same fields as MoRef."""
    pass


class ResourceGroup(MoRef):
    """Alias for clarity; same fields as MoRef."""
    pass


class SharedWithResource(MoRef):
    """Alias for clarity; same fields as MoRef."""
    pass


class Organization(BaseModel):
    # Basic identification
    Moid: str
    Name: str
    Description: Optional[str] = None

    # Organizational metadata
    ClassId: Optional[str] = None
    ObjectType: Optional[str] = None

    # Time info
    CreateTime: Optional[str] = None
    ModTime: Optional[str] = None

    # Account ownership
    Account: Optional[MoRef] = None
    AccountMoid: Optional[str] = None
    DomainGroupMoid: Optional[str] = None
    Owners: Optional[List[str]] = None

    # Hierarchy
    Ancestors: Optional[List[MoRef]] = None

    # Permissions & Tags
    PermissionResources: Optional[List[PermissionResource]] = None
    Tags: Optional[List[Tag]] = None

    # Resource Groups
    ResourceGroups: Optional[List[ResourceGroup]] = None

    # Sharing info
    SharedScope: Optional[str] = None
    SharedWithResources: Optional[List[SharedWithResource]] = None

    # Version Context (can be nested dict)
    VersionContext: Optional[Any] = None
