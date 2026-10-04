from datetime import datetime, timezone

from correlation.models import SecurityIncident
from risk.models import RiskAssessment


class RiskEngine:
    """
    ORBIT-X simulated mission-risk assessment engine.

    Converts correlated security incidents into a
    normalized risk score, risk level, and mission impact.

    The engine operates only on controlled simulation data.
    """

    def assess(
        self,
        incident: SecurityIncident,
    ) -> RiskAssessment:

        score = 0.0

        severity_scores = {
            "INFO": 15.0,
            "WARNING": 35.0,
            "CRITICAL": 60.0,
        }

        # --------------------------------------------------
        # Base severity
        # --------------------------------------------------

        score += severity_scores.get(
            incident.severity,
            25.0,
        )

        # --------------------------------------------------
        # Detection-specific contributions
        # --------------------------------------------------

        for detection in incident.detections:

            if detection.event_type == (
                "COMMUNICATION_ANOMALY"
            ):
                score += 10.0

            elif detection.event_type == (
                "PACKET_LOSS_ANOMALY"
            ):
                score += 10.0

            elif detection.event_type == (
                "CPU_ANOMALY"
            ):
                score += 15.0

            elif detection.event_type == (
                "THERMAL_ANOMALY"
            ):
                score += 20.0

            elif detection.event_type == (
                "ML_TELEMETRY_ANOMALY"
            ):
                # ML is supporting evidence. It contributes
                # to confidence/risk without representing
                # another physical subsystem.
                score += 5.0

        # --------------------------------------------------
        # Multi-subsystem escalation
        # --------------------------------------------------

        if incident.incident_type == (
            "MULTI_SUBSYSTEM_INCIDENT"
        ):
            score += 20.0

        # --------------------------------------------------
        # Normalize score
        # --------------------------------------------------

        score = min(
            score,
            100.0,
        )

        # --------------------------------------------------
        # Risk level
        # --------------------------------------------------

        risk_level = self._determine_risk_level(
            score
        )

        # --------------------------------------------------
        # Mission impact
        # --------------------------------------------------

        mission_impact = (
            self._determine_mission_impact(
                incident.incident_type
            )
        )

        # --------------------------------------------------
        # Explanation
        # --------------------------------------------------

        rationale = self._build_rationale(
            incident=incident,
            score=score,
            risk_level=risk_level,
        )

        return RiskAssessment(
            incident_id=incident.incident_id,
            risk_score=score,
            risk_level=risk_level,
            mission_impact=mission_impact,
            rationale=rationale,
            assessed_at=datetime.now(
                timezone.utc
            ),
        )

    @staticmethod
    def _determine_risk_level(
        score: float,
    ) -> str:

        if score >= 75.0:
            return "CRITICAL"

        if score >= 50.0:
            return "HIGH"

        if score >= 25.0:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _determine_mission_impact(
        incident_type: str,
    ) -> str:

        impact_map = {
            "COMMUNICATION_INCIDENT":
                "COMMUNICATION",

            "THERMAL_INCIDENT":
                "THERMAL",

            "FLIGHT_COMPUTER_INCIDENT":
                "FLIGHT_COMPUTER",

            "MULTI_SUBSYSTEM_INCIDENT":
                "MULTI_SUBSYSTEM",

            "ML_DETECTED_SPACECRAFT_ANOMALY":
                "GENERAL_SPACECRAFT",

            "SPACECRAFT_ANOMALY":
                "GENERAL_SPACECRAFT",
        }

        return impact_map.get(
            incident_type,
            "GENERAL_SPACECRAFT",
        )

    @staticmethod
    def _build_rationale(
        incident: SecurityIncident,
        score: float,
        risk_level: str,
    ) -> str:

        detection_count = len(
            incident.detections
        )

        if incident.incident_type == (
            "MULTI_SUBSYSTEM_INCIDENT"
        ):
            return (
                f"{incident.incident_type} contains "
                f"{detection_count} correlated detection "
                f"event(s) affecting multiple simulated "
                f"spacecraft subsystems. "
                f"The simulated risk score is "
                f"{score:.1f}/100, resulting in a "
                f"{risk_level} risk level."
            )

        return (
            f"{incident.incident_type} contains "
            f"{detection_count} correlated detection "
            f"event(s). The simulated risk score is "
            f"{score:.1f}/100, resulting in a "
            f"{risk_level} risk level."
        )