from dataclasses import dataclass
from datetime import datetime


@dataclass
class ForensicEvidence:
    """
    Represents an auditable forensic record for an ORBIT-X
    simulated security incident.
    """

    evidence_id: str
    incident_id: str

    spacecraft_id: str
    mission_id: str

    captured_at: datetime

    incident_type: str
    risk_level: str
    risk_score: float

    detection_summary: list[str]
    response_summary: list[str]

    spacecraft_mode_before: str
    spacecraft_mode_after: str

    evidence_hash: str = ""