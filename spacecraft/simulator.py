from dataclasses import asdict
from datetime import datetime, timezone

from .models import SpacecraftState
from .states import SpacecraftMode


class SpacecraftSimulator:
    """
    Controlled digital-twin simulator for ORBIT-X.

    The simulator updates spacecraft telemetry in a deterministic,
    controlled manner. It does not interact with any real spacecraft
    or external systems.
    """

    def __init__(self) -> None:
        self.state = SpacecraftState()

    def tick(self, seconds: int = 1) -> SpacecraftState:
        """
        Advance the spacecraft simulation by a controlled time step.
        """

        if seconds <= 0:
            raise ValueError("seconds must be greater than zero")

        self.state.flight_computer.uptime_seconds += seconds

        # Controlled nominal telemetry evolution
        self.state.power.battery_level = min(
            100.0,
            self.state.power.battery_level + 0.02 * seconds,
        )

        self.state.power.power_load = 41.0

        self.state.thermal.temperature = 24.8
        self.state.thermal.thermal_state = "NOMINAL"

        self.state.communication.link_quality = 98.0
        self.state.communication.packet_loss = 0.8

        self.state.flight_computer.cpu_usage = 42.0
        self.state.flight_computer.memory_usage = 38.0
        self.state.flight_computer.status = "OPERATIONAL"

        self.state.payload.status = "ACTIVE"
        self.state.payload.activity_level = 64.0

        self.state.mode = SpacecraftMode.NOMINAL

        self.state.last_updated = datetime.now(timezone.utc)

        return self.state

    def simulate_communication_anomaly(self) -> SpacecraftState:
        """
        Simulate a controlled communication degradation event.

        This changes only the digital-twin state. It does not interact
        with any real communication system.
        """

        self.state.communication.link_quality = 55.0
        self.state.communication.signal_strength = -82.0
        self.state.communication.packet_loss = 12.0

        self.state.mode = SpacecraftMode.DEGRADED

        self.state.last_updated = datetime.now(timezone.utc)

        return self.state

    def recover_from_anomaly(self) -> SpacecraftState:
        """
        Restore the spacecraft communication subsystem to nominal
        simulated conditions.
        """

        self.state.communication.link_quality = 98.0
        self.state.communication.signal_strength = -62.0
        self.state.communication.packet_loss = 0.8

        self.state.mode = SpacecraftMode.NOMINAL

        self.state.last_updated = datetime.now(timezone.utc)

        return self.state

    def set_mode(self, mode: SpacecraftMode) -> SpacecraftState:
        """
        Change the simulated spacecraft operational mode.
        """

        self.state.mode = mode
        self.state.last_updated = datetime.now(timezone.utc)

        return self.state

    def snapshot(self) -> dict:
        """
        Return the current spacecraft state as a dictionary.
        """

        return asdict(self.state)


if __name__ == "__main__":
    simulator = SpacecraftSimulator()

    print("ORBIT-X Spacecraft Simulator")
    print("=" * 32)

    # 1. Nominal state
    state = simulator.tick()

    print("\n[1] NOMINAL")
    print(f"Mode       : {state.mode.value}")
    print(f"Link       : {state.communication.link_quality:.1f}%")
    print(f"Packet Loss: {state.communication.packet_loss:.1f}%")

    # 2. Controlled communication anomaly
    state = simulator.simulate_communication_anomaly()

    print("\n[2] COMMUNICATION ANOMALY")
    print(f"Mode       : {state.mode.value}")
    print(f"Link       : {state.communication.link_quality:.1f}%")
    print(f"Packet Loss: {state.communication.packet_loss:.1f}%")

    # 3. Recovery
    state = simulator.recover_from_anomaly()

    print("\n[3] RECOVERY")
    print(f"Mode       : {state.mode.value}")
    print(f"Link       : {state.communication.link_quality:.1f}%")
    print(f"Packet Loss: {state.communication.packet_loss:.1f}%")