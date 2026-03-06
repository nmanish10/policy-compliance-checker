from pydantic import BaseModel
from typing import Optional


class PolicySections(BaseModel):

    data_protection: Optional[str] = None
    access_control: Optional[str] = None
    retention: Optional[str] = None
    incident_reporting: Optional[str] = None