from enum import Enum


class SpacecraftMode(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    ALERT = "ALERT"
    SAFE_MODE = "SAFE_MODE"
    COMPROMISED = "COMPROMISED"