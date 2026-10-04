from ai.ml.anomaly_detector import (
    TelemetryAnomalyDetector,
)

from detection.engine import DetectionEngine
from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector


def build_normal_dataset(count: int = 200):
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
    simulator = SpacecraftSimulator()
    collector = TelemetryCollector()

    simulator.tick()

    # Controlled synthetic spacecraft anomaly.
    simulator.state.communication.link_quality = 35.0
    simulator.state.communication.signal_strength = -95.0
    simulator.state.communication.packet_loss = 35.0

    simulator.state.flight_computer.cpu_usage = 97.0
    simulator.state.flight_computer.memory_usage = 94.0

    simulator.state.thermal.temperature = 72.0
    simulator.state.power.power_load = 88.0

    return collector.collect(
        simulator.state
    )


def test_ml_detection_engine_integration() -> None:
    """
    Verify that the Isolation Forest anomaly detector is
    correctly integrated into the Detection Engine.

    Expected behavior:

    Nominal telemetry
        -> 0 detections

    Controlled anomalous telemetry
        -> rule-based detections
        -> ML-ANOMALY-001
    """

    # ==================================================
    # 1. Build nominal training/calibration data
    # ==================================================

    normal_records = build_normal_dataset()

    assert len(normal_records) == 200

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    assert len(training_records) == 150
    assert len(calibration_records) == 50

    # ==================================================
    # 2. Train Isolation Forest
    # ==================================================

    anomaly_detector = TelemetryAnomalyDetector()

    anomaly_detector.fit(
        training_records,
        calibration_records,
    )

    assert anomaly_detector.threshold is not None

    # ==================================================
    # 3. Create Detection Engine with ML detector
    # ==================================================

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    # ==================================================
    # 4. Test normal telemetry
    # ==================================================

    normal_telemetry = calibration_records[-1]

    normal_detections = detection_engine.detect(
        normal_telemetry
    )

    assert len(normal_detections) == 0

    # ==================================================
    # 5. Test controlled anomalous telemetry
    # ==================================================

    anomalous_telemetry = (
        build_anomalous_record()
    )

    anomaly_detections = detection_engine.detect(
        anomalous_telemetry
    )

    # The controlled anomaly should trigger the
    # communication, packet-loss, CPU, and thermal
    # rule-based detections plus ML evidence.
    assert len(anomaly_detections) == 5

    # ==================================================
    # 6. Verify ML anomaly event
    # ==================================================

    ml_events = [
        detection
        for detection in anomaly_detections
        if detection.rule_id == "ML-ANOMALY-001"
    ]

    assert len(ml_events) == 1

    ml_event = ml_events[0]

    assert (
        ml_event.event_type
        == "ML_TELEMETRY_ANOMALY"
    )

    assert ml_event.metric == "ml_anomaly_score"

    assert (
        ml_event.observed_value
        < ml_event.threshold
    )

    # ==================================================
    # 7. Verify rule-based detections
    # ==================================================

    rule_ids = {
        detection.rule_id
        for detection in anomaly_detections
    }

    assert "COMM-LINK-001" in rule_ids
    assert "COMM-LOSS-001" in rule_ids
    assert "CPU-001" in rule_ids
    assert "THERMAL-001" in rule_ids
    assert "ML-ANOMALY-001" in rule_ids