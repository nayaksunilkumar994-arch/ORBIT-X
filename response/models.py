from dataclasses import dataclass
from datetime import datetime


@dataclass
class ResponseAction:
    """
    Represents a simulated defensive action performed by ORBIT-X.
    """

    action_id: str
    action_type: str
    target: str
    reason: str
    status: str
    executed_at: datetime


@dataclass
class ResponsePlan:
    """
    Represents the autonomous response plan generated for
    a simulated security incident.
    """

    incident_id: str
    risk_level: str
    actions: list[ResponseAction]
    mission_continuity: str