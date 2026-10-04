from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector

from ai.ml.anomaly_detector import TelemetryAnomalyDetector


def build_normal_dataset(
    count: int = 200,
):
    simulator = SpacecraftSimulator()
    collector = TelemetryCollector()

    records = []

    for index in range(count):
        simulator.tick()

        # Deterministic nominal variation.
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
            55.0 + (index % 15) * 1.0
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


def test_isolation_forest_anomaly_detection() -> None:
    """
    Verify that Isolation Forest distinguishes nominal
    spacecraft telemetry from a controlled synthetic anomaly.
    """

    # ==================================================
    # 1. Generate nominal telemetry
    # ==================================================

    normal_records = build_normal_dataset(
        count=200
    )

    assert len(normal_records) == 200

    # ==================================================
    # 2. Split nominal data
    # ==================================================

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    assert len(training_records) == 150
    assert len(calibration_records) == 50

    # ==================================================
    # 3. Train detector
    # ==================================================

    detector = TelemetryAnomalyDetector()

    detector.fit(
        training_records,
        calibration_records,
    )

    assert detector.threshold is not None

    # ==================================================
    # 4. Test nominal telemetry
    # ==================================================

    normal_result = detector.predict(
        calibration_records[-1]
    )

    assert normal_result.is_anomaly is False
    assert normal_result.prediction == 1

    # ==================================================
    # 5. Test controlled anomaly
    # ==================================================

    anomalous_record = (
        build_anomalous_record()
    )

    anomaly_result = detector.predict(
        anomalous_record
    )

    assert anomaly_result.is_anomaly is True
    assert anomaly_result.prediction == -1

    # ==================================================
    # 6. Verify anomaly score separation
    # ==================================================

    score_separation = (
        normal_result.anomaly_score
        - anomaly_result.anomaly_score
    )

    assert (
        anomaly_result.anomaly_score
        < normal_result.anomaly_score
    )

    assert score_separation > 0.0

    # ==================================================
    # 7. Verify calibrated threshold behavior
    # ==================================================

    assert (
        normal_result.anomaly_score
        >= normal_result.threshold
    )

    assert (
        anomaly_result.anomaly_score
        < anomaly_result.threshold
    )