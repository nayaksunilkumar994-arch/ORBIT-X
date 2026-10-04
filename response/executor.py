from spacecraft.models import SpacecraftState
from spacecraft.simulator import SpacecraftSimulator
from spacecraft.states import SpacecraftMode
from response.models import ResponseAction, ResponsePlan


class ResponseExecutor:
    """
    Executes safe response actions against the ORBIT-X
    spacecraft digital twin.

    This executor only modifies the local simulated state.
    It does not interact with real spacecraft or external systems.
    """

    def execute(
        self,
        plan: ResponsePlan,
        simulator: SpacecraftSimulator,
    ) -> SpacecraftState:
        """
        Execute every response action in the response plan
        against the digital twin.
        """

        for action in plan.actions:
            self._execute_action(action, simulator)

        return simulator.state

    @staticmethod
    def _execute_action(
        action: ResponseAction,
        simulator: SpacecraftSimulator,
    ) -> None:
        """
        Execute one safe simulated response action.
        """

        if action.action_type == "SIMULATED_CONTAINMENT":
            simulator.set_mode(SpacecraftMode.DEGRADED)

        elif action.action_type == "SIMULATED_RECOVERY":
            simulator.recover_from_anomaly()

        elif action.action_type == "SIMULATED_SAFE_MODE":
            simulator.set_mode(SpacecraftMode.SAFE_MODE)

        elif action.action_type in {
            "SIMULATED_MONITORING",
            "SIMULATED_LOGGING",
        }:
            return

        else:
            raise ValueError(
                f"Unsupported response action: {action.action_type}"
            )