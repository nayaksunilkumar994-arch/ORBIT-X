from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from detection.models import DetectionEvent


@dataclass
class SecurityIncident:
    """
    Represents a correlated security incident generated from
    one or more detection events.
    """

    incident_id: str
    incident_type: str
    severity: str
    status: str

    spacecraft_id: str
    mission_id: str

    detections: list[DetectionEvent] = field(default_factory=list)

    created_at: datetime | None = None

    @staticmethod
    def generate_id() -> str:
        """
        Generate a unique incident identifier.
        """

        return f"INC-{uuid4().hex[:8].upper()}"