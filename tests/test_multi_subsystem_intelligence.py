from ai.analyzer import AIIncidentAnalyzer
from ai.ml.anomaly_detector import TelemetryAnomalyDetector
from correlation.engine import CorrelationEngine
from detection.engine import DetectionEngine
from response.engine import ResponseEngine
from risk.engine import RiskEngine
from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector


def build_normal_dataset(
    count: int = 200,
):
    """
    Build controlled nominal telemetry for
    ML training and calibration.
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


def build_multi_subsystem_anomaly():
    """
    Build a controlled synthetic anomaly affecting
    communication, flight computer, thermal, and power.
    """

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


def test_multi_subsystem_intelligence() -> None:
    """
    Verify downstream intelligence across:

        Telemetry
            ↓
        ML + Rules
            ↓
        Correlation
            ↓
        Risk
            ↓
        Response Plan
            ↓
        AI Analysis

    The AI layer must correctly understand that
    the incident affects multiple simulated spacecraft
    subsystems.
    """

    # ---------------------------------------------------------
    # 1. Build nominal telemetry
    # ---------------------------------------------------------

    normal_records = build_normal_dataset()

    assert len(normal_records) == 200

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    assert len(training_records) == 150
    assert len(calibration_records) == 50

    # ---------------------------------------------------------
    # 2. Train ML anomaly detector
    # ---------------------------------------------------------

    anomaly_detector = TelemetryAnomalyDetector()

    anomaly_detector.fit(
        training_records,
        calibration_records,
    )

    assert anomaly_detector.threshold is not None

    # ---------------------------------------------------------
    # 3. Run hybrid detection
    # ---------------------------------------------------------

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    anomalous_telemetry = (
        build_multi_subsystem_anomaly()
    )

    detections = detection_engine.detect(
        anomalous_telemetry
    )

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

    # ---------------------------------------------------------
    # 4. Correlate detections
    # ---------------------------------------------------------

    correlation_engine = CorrelationEngine()

    incident = correlation_engine.correlate(
        detections=detections,
        spacecraft_id="ORBIT-X-SAT-01",
        mission_id="ORBIT-X-01",
    )

    assert incident is not None

    assert (
        incident.incident_type
        == "MULTI_SUBSYSTEM_INCIDENT"
    )

    assert incident.severity == "CRITICAL"
    assert incident.status == "OPEN"
    assert len(incident.detections) == 5

    # ---------------------------------------------------------
    # 5. Calculate risk
    # ---------------------------------------------------------

    risk_engine = RiskEngine()

    risk = risk_engine.assess(
        incident
    )

    assert risk.risk_score == 100.0
    assert risk.risk_level == "CRITICAL"
    assert risk.mission_impact == "MULTI_SUBSYSTEM"

    # ---------------------------------------------------------
    # 6. Build autonomous response plan
    # ---------------------------------------------------------

    response_engine = ResponseEngine()

    response_plan = response_engine.create_plan(
        risk
    )

    assert response_plan is not None
    assert response_plan.risk_level == "CRITICAL"
    assert len(response_plan.actions) >= 1

    # ---------------------------------------------------------
    # 7. Run AI incident analysis
    # ---------------------------------------------------------

    analyzer = AIIncidentAnalyzer()

    analysis = analyzer.analyze(
        incident=incident,
        risk=risk,
        response_plan=response_plan,
    )

    # ---------------------------------------------------------
    # 8. Validate AI analysis structure
    # ---------------------------------------------------------

    assert analysis.incident_id == incident.incident_id

    assert isinstance(
        analysis.classification,
        str,
    )

    assert isinstance(
        analysis.confidence,
        float,
    )

    assert isinstance(
        analysis.explanation,
        str,
    )

    assert isinstance(
        analysis.indicators,
        list,
    )

    assert isinstance(
        analysis.recommended_action,
        str,
    )

    # ---------------------------------------------------------
    # 9. Validate classification
    # ---------------------------------------------------------

    assert (
        analysis.classification
        == "POTENTIAL_MULTI_SUBSYSTEM_SECURITY_EVENT"
    )

    # ---------------------------------------------------------
    # 10. Validate high-confidence reasoning
    # ---------------------------------------------------------

    assert analysis.confidence >= 0.90
    assert analysis.confidence <= 1.0

    assert (
        "multiple simulated spacecraft subsystems"
        in analysis.explanation.lower()
    )

    # ---------------------------------------------------------
    # 11. Validate ML evidence consumption
    # ---------------------------------------------------------

    ml_indicators = [
        indicator
        for indicator in analysis.indicators
        if indicator.startswith(
            "ML anomaly detected:"
        )
    ]

    assert len(ml_indicators) == 1

    ml_indicator = ml_indicators[0]

    assert "score=" in ml_indicator
    assert "threshold=" in ml_indicator

    # ---------------------------------------------------------
    # 12. Validate all detection evidence reaches AI
    # ---------------------------------------------------------

    indicator_text = " ".join(
        analysis.indicators
    )

    assert "COMM-LINK-001" in indicator_text
    assert "COMM-LOSS-001" in indicator_text
    assert "CPU-001" in indicator_text
    assert "THERMAL-001" in indicator_text
    assert "ML anomaly detected:" in indicator_text

    # ---------------------------------------------------------
    # 13. Validate mission impact through RiskAssessment
    # ---------------------------------------------------------

    assert (
        risk.mission_impact
        == "MULTI_SUBSYSTEM"
    )

    # ---------------------------------------------------------
    # 14. Validate critical response recommendation
    # ---------------------------------------------------------

    recommendation = (
        analysis.recommended_action.lower()
    )

    assert "safe mode" in recommendation
    assert "containment" in recommendation
    assert "forensic evidence" in recommendation

    # ---------------------------------------------------------
    # 15. Validate response plan consistency
    # ---------------------------------------------------------

    action_types = {
        action.action_type
        for action in response_plan.actions
    }

    assert (
        "SIMULATED_SAFE_MODE"
        in action_types
    )

    assert (
        "SIMULATED_CONTAINMENT"
        in action_types
    )