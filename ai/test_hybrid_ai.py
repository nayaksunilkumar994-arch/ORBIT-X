from ai.analyzer import AIIncidentAnalyzer
from ai.ml.anomaly_detector import (
    TelemetryAnomalyDetector,
)

from correlation.engine import CorrelationEngine
from detection.engine import DetectionEngine
from response.engine import ResponseEngine
from risk.engine import RiskEngine
from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector


def build_normal_dataset(
    count: int = 200,
):
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


def main():

    print(
        "=== ORBIT-X AI + ML INTEGRATION TEST ==="
    )

    # --------------------------------------------------
    # 1. Build nominal telemetry
    # --------------------------------------------------

    normal_records = build_normal_dataset()

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    # --------------------------------------------------
    # 2. Train Isolation Forest
    # --------------------------------------------------

    anomaly_detector = (
        TelemetryAnomalyDetector()
    )

    anomaly_detector.fit(
        training_records,
        calibration_records,
    )

    print(
        "Isolation Forest: FITTED"
    )

    print(
        "ML threshold:",
        f"{anomaly_detector.threshold:.6f}",
    )

    # --------------------------------------------------
    # 3. Detection Engine
    # --------------------------------------------------

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    # --------------------------------------------------
    # 4. Generate anomaly
    # --------------------------------------------------

    anomalous_telemetry = (
        build_anomalous_record()
    )

    # --------------------------------------------------
    # 5. Detection
    # --------------------------------------------------

    detections = detection_engine.detect(
        anomalous_telemetry
    )

    print(
        "\n[1] DETECTION"
    )

    for detection in detections:
        print(
            "-",
            detection.rule_id,
            "|",
            detection.event_type,
        )

    print(
        "Detection count:",
        len(detections),
    )

    # --------------------------------------------------
    # 6. Correlation
    # --------------------------------------------------

    correlation_engine = (
        CorrelationEngine()
    )

    incident = correlation_engine.correlate(
        detections=detections,
        spacecraft_id="ORBIT-X-SAT-01",
        mission_id="ORBIT-X-01",
    )

    if incident is None:
        print(
            "FAIL: No security incident created."
        )
        return

    print(
        "\n[2] INCIDENT"
    )

    print(
        "Incident ID:",
        incident.incident_id,
    )

    print(
        "Incident Type:",
        incident.incident_type,
    )

    print(
        "Severity:",
        incident.severity,
    )

    print(
        "Detection count:",
        len(incident.detections),
    )

    # --------------------------------------------------
    # 7. Risk
    # --------------------------------------------------

    risk_engine = RiskEngine()

    risk = risk_engine.assess(
        incident
    )

    print(
        "\n[3] RISK"
    )

    print(
        "Risk score:",
        risk.risk_score,
    )

    print(
        "Risk level:",
        risk.risk_level,
    )

    print(
        "Mission impact:",
        risk.mission_impact,
    )

    # --------------------------------------------------
    # 8. Response plan
    # --------------------------------------------------

    response_engine = (
        ResponseEngine()
    )

    response_plan = (
        response_engine.create_plan(
            risk
        )
    )

    print(
        "\n[4] RESPONSE PLAN"
    )

    for action in response_plan.actions:
        print(
            "-",
            action.action_type,
            "|",
            action.target,
        )

    # --------------------------------------------------
    # 9. AI analysis
    # --------------------------------------------------

    analyzer = AIIncidentAnalyzer()

    analysis = analyzer.analyze(
        incident=incident,
        risk=risk,
        response_plan=response_plan,
    )

    print(
        "\n[5] AI INCIDENT ANALYSIS"
    )

    print(
        "Classification:",
        analysis.classification,
    )

    print(
        "Confidence:",
        analysis.confidence,
    )

    print(
        "Explanation:",
        analysis.explanation,
    )

    print(
        "Indicators:"
    )

    for indicator in analysis.indicators:
        print(
            "-",
            indicator,
        )

    print(
        "Recommended action:",
        analysis.recommended_action,
    )

    # --------------------------------------------------
    # 10. Verification
    # --------------------------------------------------

    ml_events = [
        detection
        for detection in detections
        if detection.rule_id
        == "ML-ANOMALY-001"
    ]

    print(
        "\n=== TEST RESULT ==="
    )

    if (
        len(ml_events) == 1
        and analysis.confidence >= 0.90
        and "Isolation Forest" in analysis.explanation
        and len(analysis.indicators) == 5
    ):
        print(
            "PASS: AI analyzer successfully "
            "incorporated ML anomaly evidence."
        )
    else:
        print(
            "FAIL: AI + ML integration did not "
            "produce the expected result."
        )


if __name__ == "__main__":
    main()