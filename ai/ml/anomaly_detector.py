from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest

from telemetry.models import TelemetryRecord


@dataclass
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    prediction: int
    threshold: float


class TelemetryAnomalyDetector:
    """
    Isolation Forest anomaly detector for controlled
    ORBIT-X spacecraft telemetry.

    The detector is trained only on nominal telemetry.
    A separate nominal calibration set is used to
    establish the operational anomaly threshold.
    """

    FEATURES = [
        "battery_level",
        "power_load",
        "temperature",
        "link_quality",
        "signal_strength",
        "packet_loss",
        "cpu_usage",
        "memory_usage",
        "payload_activity_level",
    ]

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> None:

        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=200,
        )

        self.threshold: float | None = None
        self._fitted = False

    def fit(
        self,
        training_records: list[TelemetryRecord],
        calibration_records: list[TelemetryRecord],
    ) -> None:

        if not training_records:
            raise ValueError(
                "Training telemetry records are required."
            )

        if not calibration_records:
            raise ValueError(
                "Calibration telemetry records are required."
            )

        training_features = self._records_to_matrix(
            training_records
        )

        calibration_features = self._records_to_matrix(
            calibration_records
        )

        # Train only on nominal telemetry.
        self.model.fit(training_features)

        # Evaluate a separate nominal calibration dataset.
        calibration_scores = self.model.decision_function(
            calibration_features
        )

        # Use the lower 5th percentile of nominal
        # calibration scores as the ORBIT-X threshold.
        self.threshold = float(
            np.percentile(
                calibration_scores,
                5,
            )
        )

        self._fitted = True

    def predict(
        self,
        telemetry: TelemetryRecord,
    ) -> AnomalyResult:

        if not self._fitted:
            raise RuntimeError(
                "The anomaly detector must be fitted before prediction."
            )

        if self.threshold is None:
            raise RuntimeError(
                "The anomaly threshold has not been calibrated."
            )

        features = self._records_to_matrix(
            [telemetry]
        )

        anomaly_score = float(
            self.model.decision_function(
                features
            )[0]
        )

        is_anomaly = (
            anomaly_score < self.threshold
        )

        prediction = (
            -1 if is_anomaly else 1
        )

        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            prediction=prediction,
            threshold=self.threshold,
        )

    @classmethod
    def _records_to_matrix(
        cls,
        telemetry_records: list[TelemetryRecord],
    ) -> np.ndarray:

        return np.array(
            [
                [
                    float(
                        getattr(
                            record,
                            feature,
                        )
                    )
                    for feature in cls.FEATURES
                ]
                for record in telemetry_records
            ],
            dtype=float,
        )