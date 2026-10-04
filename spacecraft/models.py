from dataclasses import dataclass, field
from datetime import datetime, timezone

from .states import SpacecraftMode


@dataclass
class PowerSystem:
    battery_level: float = 87.0
    solar_generation: float = 72.0
    power_load: float = 41.0


@dataclass
class ThermalSystem:
    temperature: float = 24.8
    thermal_state: str = "NOMINAL"


@dataclass
class CommunicationSystem:
    link_quality: float = 98.0
    signal_strength: float = -62.0
    packet_loss: float = 0.8


@dataclass
class NavigationSystem:
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    velocity: float = 7.6
    attitude_pitch: float = 0.0
    attitude_roll: float = 0.0
    attitude_yaw: float = 0.0


@dataclass
class FlightComputer:
    cpu_usage: float = 42.0
    memory_usage: float = 38.0
    uptime_seconds: int = 0
    status: str = "OPERATIONAL"


@dataclass
class PayloadSystem:
    status: str = "ACTIVE"
    activity_level: float = 64.0


@dataclass
class SpacecraftState:
    spacecraft_id: str = "ORBIT-X-SAT-01"
    mission_id: str = "ORBIT-X-01"

    mode: SpacecraftMode = SpacecraftMode.NOMINAL

    power: PowerSystem = field(default_factory=PowerSystem)
    thermal: ThermalSystem = field(default_factory=ThermalSystem)
    communication: CommunicationSystem = field(
        default_factory=CommunicationSystem
    )
    navigation: NavigationSystem = field(default_factory=NavigationSystem)
    flight_computer: FlightComputer = field(default_factory=FlightComputer)
    payload: PayloadSystem = field(default_factory=PayloadSystem)

    last_updated: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )