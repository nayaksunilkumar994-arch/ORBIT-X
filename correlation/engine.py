from datetime import datetime, timezone

from correlation.models import SecurityIncident
from detection.models import DetectionEvent


class CorrelationEngine:
    """
    Correlates individual detection events into a single
    ORBIT-X security incident.

    The correlation layer distinguishes between:

    - single-subsystem incidents
    - multi-subsystem incidents
    - ML-only spacecraft anomalies

    ML anomaly detection is treated as supporting evidence
    rather than as a physical spacecraft subsystem.
    """

    def correlate(
        self,
        detections: list[DetectionEvent],
        spacecraft_id: str,
        mission_id: str,
    ) -> SecurityIncident | None:

        if not detections:
            return None

        incident_type = self._determine_incident_type(
            detections
        )

        severity = self._determine_severity(
            detections
        )

        return SecurityIncident(
            incident_id=SecurityIncident.generate_id(),
            incident_type=incident_type,
            severity=severity,
            status="OPEN",
            spacecraft_id=spacecraft_id,
            mission_id=mission_id,
            detections=detections,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _determine_incident_type(
        detections: list[DetectionEvent],
    ) -> str:
        """
        Determine incident type from affected spacecraft
        subsystems.

        ML telemetry anomaly is supporting evidence and
        does not count as a physical subsystem.
        """

        event_types = {
            detection.event_type
            for detection in detections
        }

        affected_subsystems: set[str] = set()

        # --------------------------------------------------
        # Communication subsystem
        # --------------------------------------------------

        if (
            "COMMUNICATION_ANOMALY"
            in event_types
            or "PACKET_LOSS_ANOMALY"
            in event_types
        ):
            affected_subsystems.add(
                "COMMUNICATION"
            )

        # --------------------------------------------------
        # Thermal subsystem
        # --------------------------------------------------

        if "THERMAL_ANOMALY" in event_types:
            affected_subsystems.add(
                "THERMAL"
            )

        # --------------------------------------------------
        # Flight computer subsystem
        # --------------------------------------------------

        if "CPU_ANOMALY" in event_types:
            affected_subsystems.add(
                "FLIGHT_COMPUTER"
            )

        # --------------------------------------------------
        # Multi-subsystem classification
        # --------------------------------------------------

        if len(affected_subsystems) >= 2:
            return "MULTI_SUBSYSTEM_INCIDENT"

        # --------------------------------------------------
        # Single-subsystem classification
        # --------------------------------------------------

        if "COMMUNICATION" in affected_subsystems:
            return "COMMUNICATION_INCIDENT"

        if "THERMAL" in affected_subsystems:
            return "THERMAL_INCIDENT"

        if "FLIGHT_COMPUTER" in affected_subsystems:
            return "FLIGHT_COMPUTER_INCIDENT"

        # --------------------------------------------------
        # ML-only anomaly
        # --------------------------------------------------

        if "ML_TELEMETRY_ANOMALY" in event_types:
            return "ML_DETECTED_SPACECRAFT_ANOMALY"

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        return "SPACECRAFT_ANOMALY"

    @staticmethod
    def _determine_severity(
        detections: list[DetectionEvent],
    ) -> str:

        severity_priority = {
            "INFO": 1,
            "WARNING": 2,
            "CRITICAL": 3,
        }

        highest = max(
            detections,
            key=lambda detection:
            severity_priority[
                detection.severity.value
            ],
        )

        return highest.severity.value