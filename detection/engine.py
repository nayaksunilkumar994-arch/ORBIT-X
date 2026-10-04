from detection.models import DetectionEvent, DetectionSeverity
from detection.rules import (
    DETECTION_RULES,
    get_telemetry_value,
)
from telemetry.models import TelemetryRecord

from ai.ml.anomaly_detector import (
    TelemetryAnomalyDetector,
)


class DetectionEngine:
    def __init__(
        self,
        anomaly_detector: TelemetryAnomalyDetector | None = None,
    ) -> None:
        self.anomaly_detector = anomaly_detector

    def detect(
        self,
        telemetry: TelemetryRecord,
    ) -> list[DetectionEvent]:

        detections: list[DetectionEvent] = []

        # --------------------------------------------------
        # 1. Rule-based detection
        # --------------------------------------------------

        for rule in DETECTION_RULES:

            observed_value = get_telemetry_value(
                telemetry,
                rule.metric,
            )

            triggered = self._evaluate_rule(
                observed_value=observed_value,
                operator=rule.operator,
                threshold=rule.threshold,
            )

            if not triggered:
                continue

            severity = DetectionSeverity(
                rule.severity
            )

            detections.append(
                DetectionEvent(
                    rule_id=rule.rule_id,
                    event_type=rule.event_type,
                    severity=severity,
                    message=rule.message,
                    metric=rule.metric,
                    observed_value=observed_value,
                    threshold=rule.threshold,
                )
            )

        # --------------------------------------------------
        # 2. ML-based anomaly detection
        # --------------------------------------------------

        if self.anomaly_detector is not None:

            ml_result = self.anomaly_detector.predict(
                telemetry
            )

            if ml_result.is_anomaly:

                detections.append(
                    DetectionEvent(
                        rule_id="ML-ANOMALY-001",
                        event_type="ML_TELEMETRY_ANOMALY",
                        severity=DetectionSeverity.WARNING,
                        message=(
                            "Isolation Forest detected "
                            "statistically anomalous "
                            "spacecraft telemetry."
                        ),
                        metric="ml_anomaly_score",
                        observed_value=(
                            ml_result.anomaly_score
                        ),
                        threshold=(
                            ml_result.threshold
                        ),
                    )
                )

        return detections

    @staticmethod
    def _evaluate_rule(
        observed_value: float,
        operator: str,
        threshold: float,
    ) -> bool:

        if operator == "lt":
            return observed_value < threshold

        if operator == "gt":
            return observed_value > threshold

        raise ValueError(
            f"Unsupported detection operator: {operator}"
        )