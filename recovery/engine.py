from recovery.models import RecoveryAction, RecoveryResult
from spacecraft.simulator import SpacecraftSimulator
from spacecraft.states import SpacecraftMode


class RecoveryEngine:
    """
    Controlled recovery engine for the ORBIT-X spacecraft digital twin.

    This engine performs simulated recovery only. It does not interact
    with real spacecraft, communication systems, or external infrastructure.
    """

    def recover(self, simulator: SpacecraftSimulator) -> RecoveryResult:
        """
        Restore the simulated spacecraft from a degraded or safe state
        to nominal mission conditions.
        """

        spacecraft_mode_before = simulator.state.mode.value

        actions: list[RecoveryAction] = []

        # --------------------------------------------------
        # 1. Restore communication subsystem
        # --------------------------------------------------

        simulator.state.communication.link_quality = 98.0
        simulator.state.communication.signal_strength = -62.0
        simulator.state.communication.packet_loss = 0.8

        actions.append(
            RecoveryAction(
                action_type="COMMUNICATION_RESTORE",
                target="COMMUNICATION",
                status="EXECUTED",
                description=(
                    "Restored simulated communication link quality, "
                    "signal strength, and packet-loss levels."
                ),
            )
        )

        # --------------------------------------------------
        # 2. Restore flight computer
        # --------------------------------------------------

        simulator.state.flight_computer.cpu_usage = 42.0
        simulator.state.flight_computer.memory_usage = 38.0
        simulator.state.flight_computer.status = "OPERATIONAL"

        actions.append(
            RecoveryAction(
                action_type="FLIGHT_COMPUTER_RESTORE",
                target="FLIGHT_COMPUTER",
                status="EXECUTED",
                description=(
                    "Restored simulated flight-computer CPU, memory, "
                    "and operational status."
                ),
            )
        )

        # --------------------------------------------------
        # 3. Restore thermal subsystem
        # --------------------------------------------------

        simulator.state.thermal.temperature = 24.8
        simulator.state.thermal.thermal_state = "NOMINAL"

        actions.append(
            RecoveryAction(
                action_type="THERMAL_RESTORE",
                target="THERMAL",
                status="EXECUTED",
                description=(
                    "Restored simulated thermal conditions to nominal."
                ),
            )
        )

        # --------------------------------------------------
        # 4. Restore power subsystem
        # --------------------------------------------------

        simulator.state.power.power_load = 41.0

        actions.append(
            RecoveryAction(
                action_type="POWER_RESTORE",
                target="POWER",
                status="EXECUTED",
                description=(
                    "Restored simulated spacecraft power load "
                    "to nominal operating conditions."
                ),
            )
        )

        # --------------------------------------------------
        # 5. Restore payload
        # --------------------------------------------------

        simulator.state.payload.status = "ACTIVE"
        simulator.state.payload.activity_level = 64.0

        actions.append(
            RecoveryAction(
                action_type="PAYLOAD_RESTORE",
                target="PAYLOAD",
                status="EXECUTED",
                description=(
                    "Restored simulated payload operation."
                ),
            )
        )

        # --------------------------------------------------
        # 6. Restore spacecraft operational mode
        # --------------------------------------------------

        simulator.state.mode = SpacecraftMode.NOMINAL

        actions.append(
            RecoveryAction(
                action_type="MISSION_STATE_RESTORE",
                target="SPACECRAFT",
                status="EXECUTED",
                description=(
                    "Returned the simulated spacecraft to nominal "
                    "mission-operational mode."
                ),
            )
        )

        # --------------------------------------------------
        # 7. Build recovery result
        # --------------------------------------------------

        spacecraft_mode_after = simulator.state.mode.value

        return RecoveryResult(
            status="RECOVERY_COMPLETED",
            mission_continuity="MAINTAINED",
            spacecraft_mode_before=spacecraft_mode_before,
            spacecraft_mode_after=spacecraft_mode_after,
            actions=actions,
            recovered_subsystems=[
                "COMMUNICATION",
                "FLIGHT_COMPUTER",
                "THERMAL",
                "POWER",
                "PAYLOAD",
            ],
        )