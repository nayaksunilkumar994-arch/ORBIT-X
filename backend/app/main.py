from dataclasses import asdict
from typing import Any

from fastapi import FastAPI
from sqlalchemy import text

from .database import engine
from .orbitx_service import orbitx_service


app = FastAPI(
    title="ORBIT-X",
    description=(
        "Autonomous Cyber Defense & Digital Twin "
        "for Space Systems"
    ),
    version="0.1.0",
)


# ==========================================================
# SYSTEM
# ==========================================================


@app.get("/")
def root() -> dict[str, str]:
    return {
        "project": "ORBIT-X",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "healthy",
    }


@app.get("/health/database")
def database_health() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "database": "connected",
        "status": "healthy",
    }


# ==========================================================
# SPACECRAFT DIGITAL TWIN
# ==========================================================


@app.get("/api/spacecraft/state")
def spacecraft_state() -> dict[str, Any]:
    """
    Return the current ORBIT-X spacecraft digital-twin state.
    """

    return orbitx_service.get_spacecraft_state()


# ==========================================================
# TELEMETRY
# ==========================================================


@app.get("/api/telemetry/current")
def current_telemetry() -> dict[str, Any]:
    """
    Collect and return current spacecraft telemetry.
    """

    telemetry = orbitx_service.collect_telemetry()

    return asdict(telemetry)


# ==========================================================
# CONTROLLED INCIDENT SIMULATION
# ==========================================================


@app.post("/api/simulation/incident")
def simulate_incident() -> dict[str, Any]:
    """
    Trigger a controlled synthetic cybersecurity incident
    inside the ORBIT-X digital twin.

    This endpoint does not interact with any real spacecraft
    or external system.
    """

    spacecraft_state = (
        orbitx_service.simulate_controlled_incident()
    )

    return {
        "status": "SIMULATED_INCIDENT_CREATED",
        "message": (
            "Controlled synthetic spacecraft incident "
            "created successfully."
        ),
        "spacecraft": spacecraft_state,
    }


# ==========================================================
# THREAT DETECTION
# ==========================================================


@app.post("/api/detection/run")
def run_detection() -> dict[str, Any]:
    """
    Run rule-based and ML-based detection against the
    current spacecraft telemetry.
    """

    detections = (
        orbitx_service.detect_current_telemetry()
    )

    return {
        "status": "DETECTION_COMPLETED",
        "detection_count": len(detections),
        "detections": [
            asdict(detection)
            for detection in detections
        ],
    }


# ==========================================================
# INCIDENT CORRELATION
# ==========================================================


@app.post("/api/incident/correlate")
def correlate_incident() -> dict[str, Any]:
    """
    Correlate the latest spacecraft detections into a
    single security incident.
    """

    detections = orbitx_service.detect_current_telemetry()

    if not detections:
        return {
            "status": "NO_INCIDENT",
            "message": (
                "No security detections were found in the "
                "current spacecraft telemetry."
            ),
            "incident": None,
        }

    incident = orbitx_service.correlation_engine.correlate(
        detections=detections,
        spacecraft_id=(
            orbitx_service.simulator.state.spacecraft_id
        ),
        mission_id=(
            orbitx_service.simulator.state.mission_id
        ),
    )

    orbitx_service.latest_incident = incident

    return {
        "status": "INCIDENT_CORRELATED",
        "incident": asdict(incident),
    }


# ==========================================================
# RISK ASSESSMENT
# ==========================================================


@app.post("/api/risk/assess")
def assess_risk() -> dict[str, Any]:
    """
    Assess mission risk for the latest correlated
    spacecraft security incident.
    """

    incident = orbitx_service.latest_incident

    if incident is None:
        return {
            "status": "NO_INCIDENT",
            "message": (
                "No correlated security incident exists. "
                "Run incident correlation first."
            ),
            "risk": None,
        }

    risk = orbitx_service.risk_engine.assess(incident)

    orbitx_service.latest_risk = risk

    return {
        "status": "RISK_ASSESSMENT_COMPLETED",
        "risk": asdict(risk),
    }


# ==========================================================
# AI INCIDENT ANALYSIS
# ==========================================================


@app.post("/api/ai/analyze")
def analyze_incident() -> dict[str, Any]:
    """
    Analyze the latest correlated security incident
    using the ORBIT-X AI incident analyzer.
    """

    incident = orbitx_service.latest_incident
    risk = orbitx_service.latest_risk

    if incident is None:
        return {
            "status": "NO_INCIDENT",
            "message": (
                "No correlated security incident exists. "
                "Run incident correlation first."
            ),
            "analysis": None,
        }

    if risk is None:
        return {
            "status": "NO_RISK_ASSESSMENT",
            "message": (
                "No risk assessment exists. "
                "Run risk assessment first."
            ),
            "analysis": None,
        }

    response_plan = (
        orbitx_service.response_engine.create_plan(
            risk
        )
    )

    analysis = orbitx_service.ai_analyzer.analyze(
        incident=incident,
        risk=risk,
        response_plan=response_plan,
    )

    orbitx_service.latest_ai_analysis = analysis

    return {
        "status": "AI_ANALYSIS_COMPLETED",
        "analysis": asdict(analysis),
    }


# ==========================================================
# AUTONOMOUS RESPONSE — PLAN
# ==========================================================


@app.post("/api/response/plan")
def create_response_plan() -> dict[str, Any]:
    """
    Generate a safe simulated defensive response plan
    from the latest risk assessment.

    No response action is executed by this endpoint.
    """

    risk = orbitx_service.latest_risk

    if risk is None:
        return {
            "status": "NO_RISK_ASSESSMENT",
            "message": (
                "No risk assessment exists. "
                "Run risk assessment first."
            ),
            "response_plan": None,
        }

    response_plan = (
        orbitx_service.response_engine.create_plan(
            risk
        )
    )

    orbitx_service.latest_response_plan = response_plan

    return {
        "status": "RESPONSE_PLAN_CREATED",
        "response_plan": asdict(response_plan),
    }


# ==========================================================
# AUTONOMOUS RESPONSE — EXECUTE
# ==========================================================


@app.post("/api/response/execute")
def execute_response() -> dict[str, Any]:
    """
    Execute the latest safe simulated response plan
    against the ORBIT-X spacecraft digital twin.

    This endpoint only affects the local simulated
    spacecraft state. It does not interact with any
    real spacecraft or external system.
    """

    response_plan = orbitx_service.latest_response_plan

    if response_plan is None:
        return {
            "status": "NO_RESPONSE_PLAN",
            "message": (
                "No response plan exists. "
                "Create a response plan first."
            ),
            "response": None,
        }

    spacecraft_mode_before = (
        orbitx_service.simulator.state.mode.value
    )

    response_result = orbitx_service.response_executor.execute(
        plan=response_plan,
        simulator=orbitx_service.simulator,
    )

    spacecraft_mode_after = (
        orbitx_service.simulator.state.mode.value
    )

    return {
        "status": "RESPONSE_EXECUTED",
        "spacecraft_mode_before": spacecraft_mode_before,
        "spacecraft_mode_after": spacecraft_mode_after,
        "response": asdict(response_result),
        "spacecraft": orbitx_service.get_spacecraft_state(),
    }


# ==========================================================
# COMPLETE CYBER-DEFENSE PIPELINE
# ==========================================================


@app.post("/api/pipeline/run")
def run_complete_pipeline() -> dict[str, Any]:
    """
    Run the complete ORBIT-X cyber-defense pipeline.

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
        response
            ↓
        forensic evidence

    This endpoint executes only against the local,
    controlled ORBIT-X digital twin.
    """

    result = orbitx_service.run_detection_pipeline()

    return result


# ==========================================================
# DIGITAL FORENSICS — LATEST EVIDENCE
# ==========================================================


@app.get("/api/forensics/latest")
def latest_forensic_evidence() -> dict[str, Any]:
    """
    Return the latest forensic evidence captured by ORBIT-X.

    The evidence is generated by the complete ORBIT-X
    service pipeline and includes a SHA-256 integrity hash.

    This endpoint only retrieves previously captured evidence.
    It does not create or modify forensic records.
    """

    evidence = orbitx_service.latest_evidence

    if evidence is None:
        return {
            "status": "NO_FORENSIC_EVIDENCE",
            "message": (
                "No forensic evidence has been captured yet."
            ),
            "forensic_evidence": None,
        }

    return {
        "status": "FORENSIC_EVIDENCE_AVAILABLE",
        "forensic_evidence": asdict(evidence),
    }