from pydantic import BaseModel
from typing import List, Optional, Any

class PermissionResource(BaseModel):
    Moid: Optional[str]
    ObjectType: Optional[str]

class Tag(BaseModel):
    Key: Optional[str]
    Value: Optional[str]

class Organization(BaseModel):
    Moid: str
    Name: str
    Description: Optional[str] = None
    ClassId: Optional[str] = None
    ObjectType: Optional[str] = None
    CreateTime: Optional[str] = None
    DomainGroupMoid: Optional[str] = None
    Owners: Optional[List[str]] = None
    PermissionResources: Optional[List[PermissionResource]] = None
    Tags: Optional[List[Tag]] = None
    VersionContext: Optional[Any] = None
