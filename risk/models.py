from dataclasses import dataclass
from datetime import datetime


@dataclass
class RiskAssessment:
    """
    Represents the mission risk assessment for a correlated
    ORBIT-X security incident.

    The score is a simulation metric used by ORBIT-X and is
    not a real spacecraft safety rating.
    """

    incident_id: str
    risk_score: float
    risk_level: str

    mission_impact: str
    rationale: str

    assessed_at: datetime