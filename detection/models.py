from dataclasses import dataclass
from enum import Enum


class DetectionSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class DetectionEvent:
    rule_id: str
    event_type: str
    severity: DetectionSeverity
    message: str
    metric: str
    observed_value: float
    threshold: float