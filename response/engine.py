from datetime import datetime, timezone

from response.models import ResponseAction, ResponsePlan
from risk.models import RiskAssessment


class ResponseEngine:
    """
    Generates and executes safe, simulated defensive actions
    based on the ORBIT-X risk assessment.

    No real spacecraft, network, or external system is modified.
    """

    def create_plan(
        self,
        risk: RiskAssessment,
    ) -> ResponsePlan:
        """
        Generate a simulated defensive response plan.
        """

        actions: list[ResponseAction] = []

        if risk.risk_level == "CRITICAL":
            actions.append(
                self._create_action(
                    action_type="SIMULATED_SAFE_MODE",
                    target="SPACECRAFT",
                    reason="Critical simulated risk requires spacecraft safe mode.",
                )
            )

            actions.append(
                self._create_action(
                    action_type="SIMULATED_CONTAINMENT",
                    target=risk.mission_impact,
                    reason="Contain the affected simulated subsystem.",
                )
            )

        elif risk.risk_level == "HIGH":
            actions.append(
                self._create_action(
                    action_type="SIMULATED_CONTAINMENT",
                    target=risk.mission_impact,
                    reason="High simulated risk requires containment of the affected subsystem.",
                )
            )

            actions.append(
                self._create_action(
                    action_type="SIMULATED_RECOVERY",
                    target=risk.mission_impact,
                    reason="Attempt controlled recovery of the affected simulated subsystem.",
                )
            )

        elif risk.risk_level == "MEDIUM":
            actions.append(
                self._create_action(
                    action_type="SIMULATED_MONITORING",
                    target=risk.mission_impact,
                    reason="Continue enhanced monitoring of the affected subsystem.",
                )
            )

        else:
            actions.append(
                self._create_action(
                    action_type="SIMULATED_LOGGING",
                    target="SECURITY_MONITOR",
                    reason="Record the low-risk event for investigation.",
                )
            )

        return ResponsePlan(
            incident_id=risk.incident_id,
            risk_level=risk.risk_level,
            actions=actions,
            mission_continuity="MAINTAINED",
        )

    @staticmethod
    def _create_action(
        action_type: str,
        target: str,
        reason: str,
    ) -> ResponseAction:
        """
        Create a simulated response action.
        """

        timestamp = datetime.now(timezone.utc)

        return ResponseAction(
            action_id=f"ACT-{timestamp.strftime('%Y%m%d%H%M%S%f')}",
            action_type=action_type,
            target=target,
            reason=reason,
            status="EXECUTED",
            executed_at=timestamp,
        )