from .models import TelemetryRecord
from spacecraft.models import SpacecraftState


class TelemetryCollector:
    """
    Converts the current spacecraft digital-twin state into
    a structured telemetry record.
    """

    def collect(self, state: SpacecraftState) -> TelemetryRecord:
        """
        Create a telemetry record from the current spacecraft state.
        """

        return TelemetryRecord(
            timestamp=state.last_updated,
            spacecraft_id=state.spacecraft_id,
            mission_id=state.mission_id,
            mode=state.mode.value,

            battery_level=state.power.battery_level,
            solar_generation=state.power.solar_generation,
            power_load=state.power.power_load,

            temperature=state.thermal.temperature,
            thermal_state=state.thermal.thermal_state,

            link_quality=state.communication.link_quality,
            signal_strength=state.communication.signal_strength,
            packet_loss=state.communication.packet_loss,

            cpu_usage=state.flight_computer.cpu_usage,
            memory_usage=state.flight_computer.memory_usage,
            flight_computer_status=state.flight_computer.status,

            payload_status=state.payload.status,
            payload_activity_level=state.payload.activity_level,

            position_x=state.navigation.position_x,
            position_y=state.navigation.position_y,
            position_z=state.navigation.position_z,

            velocity=state.navigation.velocity,

            attitude_pitch=state.navigation.attitude_pitch,
            attitude_roll=state.navigation.attitude_roll,
            attitude_yaw=state.navigation.attitude_yaw,
        )