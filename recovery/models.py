from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RecoveryAction:
    """
    Represents one controlled recovery action performed
    against the ORBIT-X spacecraft digital twin.
    """

    action_type: str
    target: str
    status: str
    description: str


@dataclass
class RecoveryResult:
    """
    Result of a controlled spacecraft recovery operation.
    """

    status: str
    mission_continuity: str
    spacecraft_mode_before: str
    spacecraft_mode_after: str
    actions: list[RecoveryAction] = field(default_factory=list)
    recovered_subsystems: list[str] = field(default_factory=list)
    recovery_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )