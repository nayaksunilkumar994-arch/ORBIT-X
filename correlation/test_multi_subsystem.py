from ai.ml.anomaly_detector import (
    TelemetryAnomalyDetector,
)

from correlation.engine import CorrelationEngine

from detection.engine import DetectionEngine

from spacecraft.simulator import SpacecraftSimulator

from telemetry.collector import TelemetryCollector


def build_nominal_dataset(count: int = 200):
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


def create_multi_subsystem_anomaly(
    simulator: SpacecraftSimulator,
):
    """
    Create a controlled anomaly affecting multiple
    simulated spacecraft subsystems.
    """

    # Communication anomaly.
    simulator.simulate_communication_anomaly()

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

    return simulator.state


def test_multi_subsystem_correlation() -> None:
    """
    Verify that ORBIT-X correlates simultaneous anomalies
    across multiple simulated spacecraft subsystems into
    a single critical security incident.
    """

    # ==================================================
    # 1. Build nominal ML dataset
    # ==================================================

    normal_records = build_nominal_dataset()

    assert len(normal_records) == 200

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    assert len(training_records) == 150
    assert len(calibration_records) == 50

    # ==================================================
    # 2. Train ML anomaly detector
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
    # 3. Create multi-subsystem anomaly
    # ==================================================

    simulator = SpacecraftSimulator()

    create_multi_subsystem_anomaly(
        simulator
    )

    collector = TelemetryCollector()

    telemetry = collector.collect(
        simulator.state
    )

    # Verify the controlled anomaly values.
    assert telemetry.link_quality == 35.0
    assert telemetry.packet_loss == 35.0
    assert telemetry.cpu_usage == 97.0
    assert telemetry.temperature == 72.0
    assert telemetry.power_load == 88.0

    # ==================================================
    # 4. Hybrid detection
    # ==================================================

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    detections = detection_engine.detect(
        telemetry
    )

    # Expected:
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
    # 5. Correlation
    # ==================================================

    correlation_engine = (
        CorrelationEngine()
    )

    incident = correlation_engine.correlate(
        detections=detections,
        spacecraft_id=telemetry.spacecraft_id,
        mission_id=telemetry.mission_id,
    )

    assert incident is not None

    # ==================================================
    # 6. Determine affected physical subsystems
    # ==================================================

    event_types = {
        detection.event_type
        for detection in detections
    }

    affected_subsystems = set()

    if (
        "COMMUNICATION_ANOMALY"
        in event_types
        or "PACKET_LOSS_ANOMALY"
        in event_types
    ):
        affected_subsystems.add(
            "COMMUNICATION"
        )

    if "CPU_ANOMALY" in event_types:
        affected_subsystems.add(
            "FLIGHT_COMPUTER"
        )

    if "THERMAL_ANOMALY" in event_types:
        affected_subsystems.add(
            "THERMAL"
        )

    expected_subsystems = {
        "COMMUNICATION",
        "FLIGHT_COMPUTER",
        "THERMAL",
    }

    assert (
        affected_subsystems
        == expected_subsystems
    )

    # ==================================================
    # 7. Verify multi-subsystem classification
    # ==================================================

    assert (
        incident.incident_type
        == "MULTI_SUBSYSTEM_INCIDENT"
    )

    # ==================================================
    # 8. Verify critical severity
    # ==================================================

    assert incident.severity == "CRITICAL"

    # ==================================================
    # 9. Verify incident status
    # ==================================================

    assert incident.status == "OPEN"

    # ==================================================
    # 10. Verify ML supporting evidence
    # ==================================================

    ml_events = [
        detection
        for detection in detections
        if detection.rule_id
        == "ML-ANOMALY-001"
    ]

    assert len(ml_events) == 1

    assert (
        ml_events[0].event_type
        == "ML_TELEMETRY_ANOMALY"
    )