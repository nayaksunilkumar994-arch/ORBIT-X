from spacecraft.simulator import SpacecraftSimulator
from spacecraft.states import SpacecraftMode


class RecoveryValidator:
    """
    Validates that the ORBIT-X spacecraft digital twin has returned
    to a nominal operational state after recovery.
    """

    def validate(self, simulator: SpacecraftSimulator) -> dict:
        """
        Validate spacecraft telemetry and operational state.

        Returns a structured validation report instead of assuming
        that recovery succeeded.
        """

        state = simulator.state

        checks = {
            "spacecraft_mode": state.mode == SpacecraftMode.NOMINAL,
            "communication_link": state.communication.link_quality >= 95.0,
            "packet_loss": state.communication.packet_loss <= 2.0,
            "flight_computer_cpu": state.flight_computer.cpu_usage <= 60.0,
            "flight_computer_memory": state.flight_computer.memory_usage <= 60.0,
            "flight_computer_status": (
                state.flight_computer.status == "OPERATIONAL"
            ),
            "thermal_temperature": state.thermal.temperature <= 40.0,
            "thermal_state": state.thermal.thermal_state == "NOMINAL",
            "power_load": state.power.power_load <= 60.0,
            "payload_status": state.payload.status == "ACTIVE",
        }

        passed_checks = sum(checks.values())
        total_checks = len(checks)

        recovery_valid = passed_checks == total_checks

        return {
            "recovery_valid": recovery_valid,
            "status": (
                "VALIDATED"
                if recovery_valid
                else "VALIDATION_FAILED"
            ),
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "checks": checks,
        }