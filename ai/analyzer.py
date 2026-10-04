from correlation.models import SecurityIncident
from risk.models import RiskAssessment
from response.models import ResponsePlan

from ai.models import AIIncidentAnalysis


class AIIncidentAnalyzer:
    """
    Local incident-intelligence layer for ORBIT-X.

    Combines rule-based detection evidence, ML anomaly
    evidence, risk assessment, and response planning.

    This component operates only on controlled,
    simulated spacecraft telemetry.
    """

    def analyze(
        self,
        incident: SecurityIncident,
        risk: RiskAssessment,
        response_plan: ResponsePlan,
    ) -> AIIncidentAnalysis:

        indicators: list[str] = []

        ml_detected = False
        ml_score: float | None = None
        ml_threshold: float | None = None

        # --------------------------------------------------
        # Analyze detection evidence
        # --------------------------------------------------

        for detection in incident.detections:

            if detection.rule_id == (
                "ML-ANOMALY-001"
            ):
                ml_detected = True

                ml_score = (
                    detection.observed_value
                )

                ml_threshold = (
                    detection.threshold
                )

                indicators.append(
                    "ML anomaly detected: "
                    f"score={ml_score:.6f}, "
                    f"threshold={ml_threshold:.6f}"
                )

            else:
                indicators.append(
                    f"{detection.rule_id}: "
                    f"{detection.metric}="
                    f"{detection.observed_value:.1f}, "
                    f"threshold="
                    f"{detection.threshold:.1f}"
                )

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        classification = (
            self._classify_incident(
                incident
            )
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self._calculate_confidence(
                incident=incident,
                risk=risk,
                ml_detected=ml_detected,
            )
        )

        # --------------------------------------------------
        # Explanation
        # --------------------------------------------------

        explanation = (
            self._build_explanation(
                incident=incident,
                risk=risk,
                ml_detected=ml_detected,
                ml_score=ml_score,
                ml_threshold=ml_threshold,
            )
        )

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        recommended_action = (
            self._recommend_action(
                risk=risk,
                response_plan=response_plan,
            )
        )

        return AIIncidentAnalysis(
            incident_id=incident.incident_id,
            classification=classification,
            confidence=confidence,
            explanation=explanation,
            indicators=indicators,
            recommended_action=recommended_action,
        )

    @staticmethod
    def _classify_incident(
        incident: SecurityIncident,
    ) -> str:

        if incident.incident_type == (
            "MULTI_SUBSYSTEM_INCIDENT"
        ):
            return (
                "POTENTIAL_MULTI_SUBSYSTEM_SECURITY_EVENT"
            )

        if incident.incident_type == (
            "COMMUNICATION_INCIDENT"
        ):
            return (
                "POTENTIAL_COMMUNICATION_SECURITY_EVENT"
            )

        if incident.incident_type == (
            "THERMAL_INCIDENT"
        ):
            return (
                "POTENTIAL_THERMAL_SECURITY_EVENT"
            )

        if incident.incident_type == (
            "FLIGHT_COMPUTER_INCIDENT"
        ):
            return (
                "POTENTIAL_FLIGHT_COMPUTER_SECURITY_EVENT"
            )

        if incident.incident_type == (
            "ML_DETECTED_SPACECRAFT_ANOMALY"
        ):
            return (
                "ML_DETECTED_SPACECRAFT_SECURITY_EVENT"
            )

        return (
            "POTENTIAL_SPACECRAFT_SECURITY_EVENT"
        )

    @staticmethod
    def _calculate_confidence(
        incident: SecurityIncident,
        risk: RiskAssessment,
        ml_detected: bool,
    ) -> float:

        confidence = 0.60

        # Multiple detections increase confidence.
        if len(incident.detections) >= 2:
            confidence += 0.15

        # Multi-subsystem correlation provides stronger
        # structural evidence.
        if incident.incident_type == (
            "MULTI_SUBSYSTEM_INCIDENT"
        ):
            confidence += 0.05

        # High or critical risk provides additional
        # analytical confidence.
        if risk.risk_level in {
            "HIGH",
            "CRITICAL",
        }:
            confidence += 0.10

        # ML agreement provides another evidence source.
        if ml_detected:
            confidence += 0.05

        if incident.status == "OPEN":
            confidence += 0.05

        return min(
            confidence,
            0.95,
        )

    @staticmethod
    def _build_explanation(
        incident: SecurityIncident,
        risk: RiskAssessment,
        ml_detected: bool,
        ml_score: float | None,
        ml_threshold: float | None,
    ) -> str:

        detection_count = len(
            incident.detections
        )

        if incident.incident_type == (
            "MULTI_SUBSYSTEM_INCIDENT"
        ):
            explanation = (
                f"The analyzer correlated "
                f"{detection_count} detection event(s) "
                f"across multiple simulated spacecraft "
                f"subsystems. The assessed simulated "
                f"risk is {risk.risk_score:.1f}/100 "
                f"with a {risk.risk_level} risk level. "
                f"The affected mission area is "
                f"{risk.mission_impact}."
            )
        else:
            explanation = (
                f"The analyzer correlated "
                f"{detection_count} detection event(s) "
                f"into a {incident.incident_type}. "
                f"The assessed simulated risk is "
                f"{risk.risk_score:.1f}/100 with a "
                f"{risk.risk_level} risk level. "
                f"The affected mission area is "
                f"{risk.mission_impact}."
            )

        if (
            ml_detected
            and ml_score is not None
            and ml_threshold is not None
        ):
            explanation += (
                f" Isolation Forest also identified "
                f"the telemetry as anomalous because "
                f"the ML score ({ml_score:.6f}) was "
                f"below the calibrated ORBIT-X "
                f"threshold ({ml_threshold:.6f})."
            )

        return explanation

    @staticmethod
    def _recommend_action(
        risk: RiskAssessment,
        response_plan: ResponsePlan,
    ) -> str:

        if risk.risk_level == "CRITICAL":

            if risk.mission_impact == (
                "MULTI_SUBSYSTEM"
            ):
                return (
                    "Maintain simulated safe mode and "
                    "multi-subsystem containment, "
                    "preserve forensic evidence, and "
                    "validate affected subsystems before "
                    "controlled recovery."
                )

            return (
                "Maintain simulated safe mode and "
                "containment, preserve forensic evidence, "
                "and validate affected subsystems before "
                "returning to nominal operations."
            )

        if risk.risk_level == "HIGH":
            return (
                "Maintain simulated containment, "
                "perform controlled recovery, and "
                "continue enhanced monitoring."
            )

        if risk.risk_level == "MEDIUM":
            return (
                "Continue enhanced monitoring and "
                "investigate the affected mission subsystem."
            )

        return (
            "Record the event and continue nominal "
            "mission operations."
        )