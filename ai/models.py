from dataclasses import dataclass


@dataclass
class AIIncidentAnalysis:
    incident_id: str
    classification: str
    confidence: float
    explanation: str
    indicators: list[str]
    recommended_action: str