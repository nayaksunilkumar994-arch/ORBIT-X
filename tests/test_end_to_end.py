from ai.analyzer import AIIncidentAnalyzer
from ai.ml.anomaly_detector import TelemetryAnomalyDetector

from correlation.engine import CorrelationEngine
from detection.engine import DetectionEngine

from forensics.collector import ForensicCollector

from response.engine import ResponseEngine
from response.executor import ResponseExecutor

from risk.engine import RiskEngine

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


def create_controlled_incident(
    simulator: SpacecraftSimulator,
):
    """
    Create a controlled synthetic spacecraft anomaly.

    The anomaly intentionally combines several abnormal
    telemetry characteristics so that both the rule-based
    detector and Isolation Forest can identify the same
    telemetry record as anomalous.

    This modifies only the local digital twin.
    """

    simulator.simulate_communication_anomaly()

    # Communication degradation.
    simulator.state.communication.link_quality = 35.0
    simulator.state.communication.signal_strength = -95.0
    simulator.state.communication.packet_loss = 35.0

    # Flight-computer anomaly.
    simulator.state.flight_computer.cpu_usage = 97.0
    simulator.state.flight_computer.memory_usage = 94.0

    # Thermal anomaly.
    simulator.state.thermal.temperature = 72.0

    # Power-load anomaly.
    simulator.state.power.power_load = 88.0

    return simulator.state


def main():
    print(
        "=================================================="
    )
    print(
        "ORBIT-X FULL END-TO-END MISSION DEFENSE TEST"
    )
    print(
        "=================================================="
    )

    # ==================================================
    # 1. Initialize spacecraft digital twin
    # ==================================================

    simulator = SpacecraftSimulator()
    telemetry_collector = TelemetryCollector()

    print("\n[1] SPACECRAFT DIGITAL TWIN")
    print(
        "Spacecraft:",
        simulator.state.spacecraft_id,
    )
    print(
        "Mission:",
        simulator.state.mission_id,
    )
    print(
        "Initial mode:",
        simulator.state.mode.value,
    )

    # ==================================================
    # 2. Nominal mission telemetry
    # ==================================================

    simulator.tick()

    nominal_telemetry = (
        telemetry_collector.collect(
            simulator.state
        )
    )

    print("\n[2] NOMINAL MISSION")
    print(
        "Mode:",
        nominal_telemetry.mode,
    )
    print(
        "Link quality:",
        nominal_telemetry.link_quality,
    )
    print(
        "Packet loss:",
        nominal_telemetry.packet_loss,
    )
    print(
        "CPU:",
        nominal_telemetry.cpu_usage,
    )
    print(
        "Temperature:",
        nominal_telemetry.temperature,
    )

    # ==================================================
    # 3. Train ML detector
    # ==================================================

    normal_records = build_nominal_dataset()

    training_records = normal_records[:150]
    calibration_records = normal_records[150:]

    anomaly_detector = (
        TelemetryAnomalyDetector()
    )

    anomaly_detector.fit(
        training_records,
        calibration_records,
    )

    print("\n[3] ML ANOMALY DETECTOR")
    print("Status: FITTED")
    print(
        "Calibrated threshold:",
        f"{anomaly_detector.threshold:.6f}",
    )

    # ==================================================
    # 4. Controlled cyber incident
    # ==================================================

    spacecraft_mode_before = (
        simulator.state.mode.value
    )

    create_controlled_incident(
        simulator
    )

    incident_telemetry = (
        telemetry_collector.collect(
            simulator.state
        )
    )

    print("\n[4] CONTROLLED INCIDENT")
    print(
        "Mode:",
        incident_telemetry.mode,
    )
    print(
        "Link quality:",
        incident_telemetry.link_quality,
    )
    print(
        "Packet loss:",
        incident_telemetry.packet_loss,
    )
    print(
        "Signal strength:",
        incident_telemetry.signal_strength,
    )
    print(
        "CPU:",
        incident_telemetry.cpu_usage,
    )
    print(
        "Memory:",
        incident_telemetry.memory_usage,
    )
    print(
        "Temperature:",
        incident_telemetry.temperature,
    )
    print(
        "Power load:",
        incident_telemetry.power_load,
    )

    # ==================================================
    # 5. Hybrid detection
    # ==================================================

    detection_engine = DetectionEngine(
        anomaly_detector=anomaly_detector
    )

    detections = detection_engine.detect(
        incident_telemetry
    )

    print("\n[5] HYBRID DETECTION")

    for detection in detections:
        print(
            "-",
            detection.rule_id,
            "|",
            detection.event_type,
            "|",
            detection.severity.value,
        )

    print(
        "Total detections:",
        len(detections),
    )

    # ==================================================
    # 6. Incident correlation
    # ==================================================

    correlation_engine = (
        CorrelationEngine()
    )

    incident = correlation_engine.correlate(
        detections=detections,
        spacecraft_id=incident_telemetry.spacecraft_id,
        mission_id=incident_telemetry.mission_id,
    )

    if incident is None:
        raise RuntimeError(
            "Expected a security incident, "
            "but no incident was created."
        )

    print("\n[6] INCIDENT CORRELATION")
    print(
        "Incident ID:",
        incident.incident_id,
    )
    print(
        "Incident type:",
        incident.incident_type,
    )
    print(
        "Severity:",
        incident.severity,
    )
    print(
        "Status:",
        incident.status,
    )
    print(
        "Detection count:",
        len(incident.detections),
    )

    # ==================================================
    # 7. Risk assessment
    # ==================================================

    risk_engine = RiskEngine()

    risk = risk_engine.assess(
        incident
    )

    print("\n[7] RISK ASSESSMENT")
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

    # ==================================================
    # 8. AI incident analysis
    # ==================================================

    response_engine = ResponseEngine()

    response_plan = (
        response_engine.create_plan(
            risk
        )
    )

    ai_analyzer = AIIncidentAnalyzer()

    ai_analysis = ai_analyzer.analyze(
        incident=incident,
        risk=risk,
        response_plan=response_plan,
    )

    print("\n[8] AI INCIDENT ANALYSIS")
    print(
        "Classification:",
        ai_analysis.classification,
    )
    print(
        "Confidence:",
        ai_analysis.confidence,
    )
    print(
        "Indicators:",
        len(ai_analysis.indicators),
    )

    ml_evidence_detected = any(
        "ML anomaly detected" in indicator
        for indicator in ai_analysis.indicators
    )

    print(
        "ML evidence:",
        ml_evidence_detected,
    )

    # ==================================================
    # 9. Autonomous response
    # ==================================================

    print("\n[9] AUTONOMOUS RESPONSE")

    for action in response_plan.actions:
        print(
            "-",
            action.action_type,
            "|",
            action.target,
            "|",
            action.status,
        )

    response_executor = ResponseExecutor()

    response_executor.execute(
        plan=response_plan,
        simulator=simulator,
    )

    spacecraft_mode_after = (
        simulator.state.mode.value
    )

    print(
        "Mode after response:",
        spacecraft_mode_after,
    )

    # ==================================================
    # 10. Digital forensics
    # ==================================================

    forensic_collector = (
        ForensicCollector()
    )

    evidence = forensic_collector.collect(
        incident=incident,
        risk=risk,
        response_plan=response_plan,
        spacecraft_mode_before=(
            spacecraft_mode_before
        ),
        spacecraft_mode_after=(
            spacecraft_mode_after
        ),
    )

    print("\n[10] DIGITAL FORENSICS")
    print(
        "Evidence ID:",
        evidence.evidence_id,
    )
    print(
        "Incident ID:",
        evidence.incident_id,
    )
    print(
        "Detection evidence:",
        evidence.detection_summary,
    )
    print(
        "Response evidence:",
        evidence.response_summary,
    )
    print(
        "Mode transition:",
        f"{evidence.spacecraft_mode_before}"
        f" -> "
        f"{evidence.spacecraft_mode_after}",
    )
    print(
        "SHA-256:",
        evidence.evidence_hash,
    )

    # ==================================================
    # 11. Mission continuity
    # ==================================================

    print("\n[11] MISSION CONTINUITY")

    print(
        "Mission continuity:",
        response_plan.mission_continuity,
    )

    # ==================================================
    # 12. Final verification
    # ==================================================

    ml_events = [
        detection
        for detection in detections
        if detection.rule_id
        == "ML-ANOMALY-001"
    ]

    sha256_valid = (
        len(evidence.evidence_hash) == 64
    )

    response_executed = all(
        action.status == "EXECUTED"
        for action in response_plan.actions
    )

    print("\n==================================================")
    print("FINAL ORBIT-X VERIFICATION")
    print("==================================================")

    checks = {
        "Nominal telemetry collected": (
            nominal_telemetry.mode == "NOMINAL"
        ),
        "Hybrid detection generated events": (
            len(detections) >= 4
        ),
        "ML anomaly detected": (
            len(ml_events) == 1
        ),
        "Incident correlated": (
            incident.status == "OPEN"
        ),
        "Risk assessment completed": (
            risk.risk_score >= 0.0
        ),
        "AI analysis completed": (
            ai_analysis.confidence > 0.0
        ),
        "ML evidence consumed by AI": (
            ml_evidence_detected
        ),
        "Response actions executed": (
            response_executed
        ),
        "Forensic evidence captured": (
            evidence.evidence_id.startswith("EVD-")
        ),
        "SHA-256 evidence hash generated": (
            sha256_valid
        ),
        "Mission continuity maintained": (
            response_plan.mission_continuity
            == "MAINTAINED"
        ),
    }

    for name, passed in checks.items():
        print(
            f"[{'PASS' if passed else 'FAIL'}] {name}"
        )

    all_passed = all(
        checks.values()
    )

    print("\n==================================================")

    if all_passed:
        print(
            "PASS: ORBIT-X full end-to-end "
            "mission defense pipeline verified."
        )
    else:
        print(
            "FAIL: One or more end-to-end "
            "verification checks failed."
        )

    print("==================================================")


if __name__ == "__main__":
    main()