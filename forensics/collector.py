import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from correlation.models import SecurityIncident
from forensics.models import ForensicEvidence
from response.models import ResponsePlan
from risk.models import RiskAssessment


class ForensicCollector:
    """
    Creates an auditable forensic evidence record for an ORBIT-X
    simulated security incident.
    """

    def collect(
        self,
        incident: SecurityIncident,
        risk: RiskAssessment,
        response_plan: ResponsePlan,
        spacecraft_mode_before: str,
        spacecraft_mode_after: str,
    ) -> ForensicEvidence:
        """
        Build a forensic evidence record and calculate its
        SHA-256 integrity hash.
        """

        detection_summary = [
            detection.rule_id
            for detection in incident.detections
        ]

        response_summary = [
            action.action_type
            for action in response_plan.actions
        ]

        evidence = ForensicEvidence(
            evidence_id=f"EVD-{uuid4().hex[:8].upper()}",
            incident_id=incident.incident_id,
            spacecraft_id=incident.spacecraft_id,
            mission_id=incident.mission_id,
            captured_at=datetime.now(timezone.utc),
            incident_type=incident.incident_type,
            risk_level=risk.risk_level,
            risk_score=risk.risk_score,
            detection_summary=detection_summary,
            response_summary=response_summary,
            spacecraft_mode_before=spacecraft_mode_before,
            spacecraft_mode_after=spacecraft_mode_after,
        )

        evidence.evidence_hash = self._calculate_hash(evidence)

        return evidence

    @staticmethod
    def _calculate_hash(
        evidence: ForensicEvidence,
    ) -> str:
        """
        Calculate a SHA-256 hash from the forensic evidence
        content, excluding the hash field itself.
        """

        evidence_data = {
            "evidence_id": evidence.evidence_id,
            "incident_id": evidence.incident_id,
            "spacecraft_id": evidence.spacecraft_id,
            "mission_id": evidence.mission_id,
            "captured_at": evidence.captured_at.isoformat(),
            "incident_type": evidence.incident_type,
            "risk_level": evidence.risk_level,
            "risk_score": evidence.risk_score,
            "detection_summary": evidence.detection_summary,
            "response_summary": evidence.response_summary,
            "spacecraft_mode_before": evidence.spacecraft_mode_before,
            "spacecraft_mode_after": evidence.spacecraft_mode_after,
        }

        canonical_data = json.dumps(
            evidence_data,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

        return hashlib.sha256(canonical_data).hexdigest()