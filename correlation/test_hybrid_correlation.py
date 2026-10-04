from ai.ml.anomaly_detector import (
    TelemetryAnomalyDetector,
)

from correlation.engine import CorrelationEngine
from detection.engine import DetectionEngine
from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector


def build_normal_dataset(
    count: int = 200,
):
    """
    Build controlled nominal telemetry for ML training
    and calibration.
    """

    simulator = SpacecraftSimulator()
    collector = TelemetryCollector()

    records = []

    for index in range(count):
        simulator.tick()

        simulator.state.power.battery_level = (
            85.0 + (index % 20) * 0.3
        )

        simulator.state.power.power_load = (
            38.0 + (index % 12) * 0.6
        )

        simulator.state.thermal.temperature = (
            23.0 + (index % 15) * 0.25
        )

        simulator.state.communication.link_quality = (
            94.0 + (index % 12) * 0.5
        )

        simulator.state.communication.signal_strength = (
            -66.0 + (index % 10) * 0.5
        )

        simulator.state.communication.packet_loss = (
            0.3 + (index % 10) * 0.15
        )

        simulator.state.flight_computer.cpu_usage = (
            38.0 + (index % 15) * 0.8
        )

        simulator.state.flight_computer.memory_usage = (
            34.0 + (index % 12) * 0.7
        )

        simulator.state.payload.activity_level = (
            55.0 + (index % 15)
        )

        records.append(
            collector.collect(
                simulator.state
            )
        )

    return records


def build_anomalous_record():
    """
    Build a controlled synthetic anomaly affecting
    multiple simulated spacecraft subsystems.
    """

    simulator = SpacecraftSimulator()
    collector = TelemetryCollector()

    simulator.tick()

    # Communication anomaly.
    simulator.state.communication.link_quality = 35.0
    simulator.state.communication.signal_strength = -95.0
    simulator.state.communication.packet_loss = 35.0

    # Flight computer anomaly.
    simulator.state.flight_computer.cpu_usage = 97.0
    simulator.state.flight_computer.memory_usage = 94.0

    # Thermal anomaly.
    simulator.state.thermal.temperature = 72.0

    # Power anomaly.
    simulator.state.power.power_load = 88.0

    return collector.collect(
        simulator.state
    )


def test_hybrid_correlation() -> None:
    """
    Verify that rule-based and ML detections are
    correlated into a single multi-subsystem incident.
    """

    # ==================================================
    # 1. Build nominal dataset
    # ==================================================

    normal_records = build_normal_dataset()

    assert len(normal_records) == 200

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    assert len(training_records) == 150
    assert len(calibration_records) == 50

    # ==================================================
    # 2. Train ML detector
    # ==================================================

    anomaly_detector = (
        TelemetryAnomalyDetector()
    )

    anomaly_detector.fit(
        training_records,
        calibration_records,
    )

    assert anomaly_detector.threshold is not None

    # ==================================================
    # 3. Create detection engine
    # ==================================================

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    # ==================================================
    # 4. Generate controlled anomaly
    # ==================================================

    anomalous_telemetry = (
        build_anomalous_record()
    )

    # ==================================================
    # 5. Run hybrid detection
    # ==================================================

    detections = detection_engine.detect(
        anomalous_telemetry
    )

    # Expected detection events:
    #
    # COMM-LINK-001
    # COMM-LOSS-001
    # CPU-001
    # THERMAL-001
    # ML-ANOMALY-001

    assert len(detections) == 5

    rule_ids = {
        detection.rule_id
        for detection in detections
    }

    assert "COMM-LINK-001" in rule_ids
    assert "COMM-LOSS-001" in rule_ids
    assert "CPU-001" in rule_ids
    assert "THERMAL-001" in rule_ids
    assert "ML-ANOMALY-001" in rule_ids

    # ==================================================
    # 6. Correlate detections
    # ==================================================

    correlation_engine = (
        CorrelationEngine()
    )

    incident = correlation_engine.correlate(
        detections=detections,
        spacecraft_id="ORBIT-X-SAT-01",
        mission_id="ORBIT-X-01",
    )

    assert incident is not None

    # ==================================================
    # 7. Verify incident identity
    # ==================================================

    assert (
        incident.spacecraft_id
        == "ORBIT-X-SAT-01"
    )

    assert (
        incident.mission_id
        == "ORBIT-X-01"
    )

    assert incident.status == "OPEN"

    # ==================================================
    # 8. Verify multi-subsystem classification
    # ==================================================

    assert (
        incident.incident_type
        == "MULTI_SUBSYSTEM_INCIDENT"
    )

    # ==================================================
    # 9. Verify critical severity
    # ==================================================

    assert incident.severity == "CRITICAL"

    # ==================================================
    # 10. Verify all detections were correlated
    # ==================================================

    assert len(incident.detections) == 5

    incident_rule_ids = {
        detection.rule_id
        for detection in incident.detections
    }

    assert (
        incident_rule_ids
        == rule_ids
    )

    # ==================================================
    # 11. Verify ML evidence is retained
    # ==================================================

    ml_events = [
        detection
        for detection in incident.detections
        if detection.rule_id
        == "ML-ANOMALY-001"
    ]

    assert len(ml_events) == 1

    assert (
        ml_events[0].event_type
        == "ML_TELEMETRY_ANOMALY"
    )