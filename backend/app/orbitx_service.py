from dataclasses import asdict
from typing import Any

from ai.analyzer import AIIncidentAnalyzer
from ai.ml.anomaly_detector import TelemetryAnomalyDetector
from correlation.engine import CorrelationEngine
from detection.engine import DetectionEngine
from forensics.collector import ForensicCollector
from recovery.engine import RecoveryEngine
from recovery.validator import RecoveryValidator
from response.engine import ResponseEngine
from response.executor import ResponseExecutor
from risk.engine import RiskEngine
from spacecraft.simulator import SpacecraftSimulator
from telemetry.collector import TelemetryCollector
from telemetry.models import TelemetryRecord


class ORBITXService:
    """
    Application service that connects the ORBIT-X simulation
    and cyber-defense pipeline.

    This service operates exclusively on the controlled
    ORBIT-X spacecraft digital twin.
    """

    def __init__(self) -> None:
        # --------------------------------------------------
        # Spacecraft digital twin
        # --------------------------------------------------

        self.simulator = SpacecraftSimulator()

        # --------------------------------------------------
        # Telemetry
        # --------------------------------------------------

        self.telemetry_collector = TelemetryCollector()

        # --------------------------------------------------
        # ML anomaly detection
        # --------------------------------------------------

        self.anomaly_detector = TelemetryAnomalyDetector()

        self.detection_engine = DetectionEngine(
            anomaly_detector=self.anomaly_detector
        )

        # --------------------------------------------------
        # Cyber-defense pipeline
        # --------------------------------------------------

        self.correlation_engine = CorrelationEngine()
        self.risk_engine = RiskEngine()
        self.ai_analyzer = AIIncidentAnalyzer()

        self.response_engine = ResponseEngine()
        self.response_executor = ResponseExecutor()

        # --------------------------------------------------
        # Mission recovery
        # --------------------------------------------------

        self.recovery_engine = RecoveryEngine()
        self.recovery_validator = RecoveryValidator()

        # --------------------------------------------------
        # Digital forensics
        # --------------------------------------------------

        self.forensic_collector = ForensicCollector()

        # --------------------------------------------------
        # Runtime state
        # --------------------------------------------------

        self.latest_telemetry: TelemetryRecord | None = None
        self.latest_detections: list[Any] = []
        self.latest_incident: Any | None = None
        self.latest_risk: Any | None = None
        self.latest_response_plan: Any | None = None
        self.latest_ai_analysis: Any | None = None

        self.latest_recovery: Any | None = None
        self.latest_recovery_validation: dict[str, Any] | None = None

        self.latest_evidence: Any | None = None

        self.ml_fitted = False

        # --------------------------------------------------
        # Initialize ML detector
        # --------------------------------------------------

        self.initialize_ml_detector()

    # ======================================================
    # ML INITIALIZATION
    # ======================================================

    def build_nominal_dataset(
        self,
        count: int = 200,
    ) -> list[TelemetryRecord]:
        """
        Build controlled nominal telemetry for ML training
        and calibration.

        The dataset is generated entirely from the local
        ORBIT-X spacecraft digital twin.
        """

        simulator = SpacecraftSimulator()
        collector = TelemetryCollector()

        records: list[TelemetryRecord] = []

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

    def initialize_ml_detector(self) -> None:
        """
        Train and calibrate the Isolation Forest detector
        using controlled nominal spacecraft telemetry.
        """

        normal_records = self.build_nominal_dataset(
            count=200
        )

        training_records = normal_records[:150]
        calibration_records = normal_records[150:]

        self.anomaly_detector.fit(
            training_records=training_records,
            calibration_records=calibration_records,
        )

        self.ml_fitted = True

    # ======================================================
    # SPACECRAFT
    # ======================================================

    def get_spacecraft_state(self) -> dict[str, Any]:
        """
        Return the current spacecraft digital-twin state.
        """

        return self.simulator.snapshot()

    # ======================================================
    # TELEMETRY
    # ======================================================

    def collect_telemetry(self) -> TelemetryRecord:
        """
        Collect telemetry from the current digital-twin state.
        """

        telemetry = self.telemetry_collector.collect(
            self.simulator.state
        )

        self.latest_telemetry = telemetry

        return telemetry

    # ======================================================
    # DETECTION
    # ======================================================

    def detect_current_telemetry(self) -> list[Any]:
        """
        Run hybrid rule-based + ML detection against
        the latest telemetry.
        """

        if self.latest_telemetry is None:
            self.collect_telemetry()

        if self.latest_telemetry is None:
            raise RuntimeError(
                "Telemetry collection failed."
            )

        if not self.ml_fitted:
            raise RuntimeError(
                "ML anomaly detector has not been fitted."
            )

        detections = self.detection_engine.detect(
            self.latest_telemetry
        )

        self.latest_detections = detections

        return detections

    # ======================================================
    # CONTROLLED INCIDENT SIMULATION
    # ======================================================

    def simulate_controlled_incident(
        self,
    ) -> dict[str, Any]:
        """
        Create the controlled ORBIT-X demonstration incident.

        The incident affects simulated communication,
        flight-computer, thermal, and power telemetry.
        """

        self.simulator.simulate_communication_anomaly()

        # --------------------------------------------------
        # Controlled synthetic incident values
        # --------------------------------------------------

        self.simulator.state.communication.link_quality = 35.0

        self.simulator.state.communication.signal_strength = (
            -95.0
        )

        self.simulator.state.communication.packet_loss = 35.0

        self.simulator.state.flight_computer.cpu_usage = 97.0

        self.simulator.state.flight_computer.memory_usage = (
            94.0
        )

        self.simulator.state.thermal.temperature = 72.0

        self.simulator.state.power.power_load = 88.0

        self.latest_telemetry = self.collect_telemetry()

        return self.get_spacecraft_state()

    # ======================================================
    # INCIDENT PIPELINE
    # ======================================================

    def run_detection_pipeline(
        self,
    ) -> dict[str, Any]:
        """
        Run the complete ORBIT-X cyber-defense and
        mission-recovery pipeline.

        Flow:

        telemetry
            ↓
        detection
            ↓
        correlation
            ↓
        risk
            ↓
        AI analysis
            ↓
        response planning
            ↓
        response execution
            ↓
        recovery execution
            ↓
        recovery validation
            ↓
        forensics
        """

        # --------------------------------------------------
        # 1. Telemetry
        # --------------------------------------------------

        telemetry = self.collect_telemetry()

        # --------------------------------------------------
        # 2. Detection
        # --------------------------------------------------

        detections = self.detection_engine.detect(
            telemetry
        )

        self.latest_detections = detections

        if not detections:
            return {
                "status": "NO_INCIDENT",
                "telemetry": asdict(telemetry),
                "detections": [],
            }

        # --------------------------------------------------
        # 3. Correlation
        # --------------------------------------------------

        incident = self.correlation_engine.correlate(
            detections=detections,
            spacecraft_id=telemetry.spacecraft_id,
            mission_id=telemetry.mission_id,
        )

        if incident is None:
            return {
                "status": "NO_INCIDENT",
                "telemetry": asdict(telemetry),
                "detections": [
                    asdict(detection)
                    for detection in detections
                ],
            }

        self.latest_incident = incident

        # --------------------------------------------------
        # 4. Risk assessment
        # --------------------------------------------------

        risk = self.risk_engine.assess(
            incident
        )

        self.latest_risk = risk

        # --------------------------------------------------
        # 5. Response planning
        # --------------------------------------------------

        response_plan = self.response_engine.create_plan(
            risk
        )

        self.latest_response_plan = response_plan

        # --------------------------------------------------
        # 6. AI incident analysis
        # --------------------------------------------------

        ai_analysis = self.ai_analyzer.analyze(
            incident=incident,
            risk=risk,
            response_plan=response_plan,
        )

        self.latest_ai_analysis = ai_analysis

        # --------------------------------------------------
        # 7. Capture spacecraft mode before response
        # --------------------------------------------------

        spacecraft_mode_before_response = (
            self.simulator.state.mode.value
        )

        # --------------------------------------------------
        # 8. Execute simulated cyber-defense response
        # --------------------------------------------------

        self.response_executor.execute(
            plan=response_plan,
            simulator=self.simulator,
        )

        spacecraft_mode_after_response = (
            self.simulator.state.mode.value
        )

        # --------------------------------------------------
        # 9. Execute mission recovery
        # --------------------------------------------------

        recovery_result = self.recovery_engine.recover(
            self.simulator
        )

        self.latest_recovery = recovery_result

        # --------------------------------------------------
        # 10. Validate mission recovery
        # --------------------------------------------------

        recovery_validation = (
            self.recovery_validator.validate(
                self.simulator
            )
        )

        self.latest_recovery_validation = (
            recovery_validation
        )

        # --------------------------------------------------
        # 11. Capture final spacecraft mode
        # --------------------------------------------------

        spacecraft_mode_after_recovery = (
            self.simulator.state.mode.value
        )

        # --------------------------------------------------
        # 12. Digital forensic evidence
        # --------------------------------------------------

        evidence = self.forensic_collector.collect(
            incident=incident,
            risk=risk,
            response_plan=response_plan,
            spacecraft_mode_before=(
                spacecraft_mode_before_response
            ),
            spacecraft_mode_after=(
                spacecraft_mode_after_recovery
            ),
        )

        self.latest_evidence = evidence

        # --------------------------------------------------
        # 13. Complete pipeline result
        # --------------------------------------------------

        return {
            "status": "INCIDENT_PROCESSED",

            "telemetry": asdict(telemetry),

            "detections": [
                asdict(detection)
                for detection in detections
            ],

            "incident": asdict(incident),

            "risk": asdict(risk),

            "ai_analysis": asdict(ai_analysis),

            "response_plan": asdict(response_plan),

            "response_state": {
                "spacecraft_mode_before": (
                    spacecraft_mode_before_response
                ),
                "spacecraft_mode_after": (
                    spacecraft_mode_after_response
                ),
            },

            "recovery": asdict(
                recovery_result
            ),

            "recovery_validation": (
                recovery_validation
            ),

            "spacecraft_state_after_recovery": (
                self.get_spacecraft_state()
            ),

            "forensic_evidence": asdict(
                evidence
            ),

            "mission_continuity": (
                recovery_result.mission_continuity
            ),
        }

    # ======================================================
    # COMPLETE SNAPSHOT
    # ======================================================

    def get_latest_snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Return the latest ORBIT-X operational snapshot.
        """

        return {
            "spacecraft": self.get_spacecraft_state(),

            "telemetry": (
                asdict(self.latest_telemetry)
                if self.latest_telemetry is not None
                else None
            ),

            "detections": [
                asdict(detection)
                for detection in self.latest_detections
            ],

            "incident": (
                asdict(self.latest_incident)
                if self.latest_incident is not None
                else None
            ),

            "risk": (
                asdict(self.latest_risk)
                if self.latest_risk is not None
                else None
            ),

            "response_plan": (
                asdict(self.latest_response_plan)
                if self.latest_response_plan is not None
                else None
            ),

            "ai_analysis": (
                asdict(self.latest_ai_analysis)
                if self.latest_ai_analysis is not None
                else None
            ),

            "recovery": (
                asdict(self.latest_recovery)
                if self.latest_recovery is not None
                else None
            ),

            "recovery_validation": (
                self.latest_recovery_validation
                if self.latest_recovery_validation is not None
                else None
            ),

            "forensic_evidence": (
                asdict(self.latest_evidence)
                if self.latest_evidence is not None
                else None
            ),
        }


# ==========================================================
# SINGLE APPLICATION SERVICE INSTANCE
# ==========================================================

orbitx_service = ORBITXService()