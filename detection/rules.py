from dataclasses import dataclass

from telemetry.models import TelemetryRecord


@dataclass(frozen=True)
class DetectionRule:
    """
    Defines a deterministic telemetry detection rule.
    """

    rule_id: str
    event_type: str
    metric: str
    threshold: float
    operator: str
    severity: str
    message: str


DETECTION_RULES = [
    DetectionRule(
        rule_id="COMM-LINK-001",
        event_type="COMMUNICATION_ANOMALY",
        metric="link_quality",
        threshold=80.0,
        operator="lt",
        severity="WARNING",
        message="Communication link quality is below the nominal simulation threshold.",
    ),
    DetectionRule(
        rule_id="COMM-LOSS-001",
        event_type="PACKET_LOSS_ANOMALY",
        metric="packet_loss",
        threshold=5.0,
        operator="gt",
        severity="WARNING",
        message="Communication packet loss is above the nominal simulation threshold.",
    ),
    DetectionRule(
        rule_id="CPU-001",
        event_type="CPU_ANOMALY",
        metric="cpu_usage",
        threshold=85.0,
        operator="gt",
        severity="WARNING",
        message="Flight computer CPU usage is above the nominal simulation threshold.",
    ),
    DetectionRule(
        rule_id="THERMAL-001",
        event_type="THERMAL_ANOMALY",
        metric="temperature",
        threshold=60.0,
        operator="gt",
        severity="CRITICAL",
        message="Spacecraft temperature is above the critical simulation threshold.",
    ),
]


def get_telemetry_value(
    telemetry: TelemetryRecord,
    metric: str,
) -> float:
    """
    Retrieve a numeric telemetry value by metric name.
    """

    value = getattr(telemetry, metric, None)

    if value is None:
        raise ValueError(f"Unknown telemetry metric: {metric}")

    if not isinstance(value, (int, float)):
        raise ValueError(f"Telemetry metric is not numeric: {metric}")

    return float(value)