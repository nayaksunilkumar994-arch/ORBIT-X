from spacecraft.simulator import SpacecraftSimulator
from spacecraft.states import SpacecraftMode


def test_mission_recovery() -> None:
    """
    Verify the complete controlled spacecraft recovery flow.

    Flow:
        NOMINAL
            ↓
        COMMUNICATION ANOMALY
            ↓
        DEGRADED
            ↓
        SAFE_MODE
            ↓
        CONTROLLED RECOVERY
            ↓
        NOMINAL
    """

    # ==================================================
    # 1. Initialize spacecraft
    # ==================================================

    simulator = SpacecraftSimulator()

    initial_state = simulator.state

    assert initial_state.mode == SpacecraftMode.NOMINAL

    # ==================================================
    # 2. Create controlled communication anomaly
    # ==================================================

    simulator.simulate_communication_anomaly()

    # Capture the values immediately because the
    # spacecraft state object is mutable.

    assert simulator.state.mode == SpacecraftMode.DEGRADED

    assert (
        simulator.state.communication.link_quality
        < 80.0
    )

    assert (
        simulator.state.communication.packet_loss
        > 5.0
    )

    assert (
        simulator.state.communication.signal_strength
        == -82.0
    )

    # ==================================================
    # 3. Simulated containment
    # ==================================================

    simulator.set_mode(
        SpacecraftMode.SAFE_MODE
    )

    assert (
        simulator.state.mode
        == SpacecraftMode.SAFE_MODE
    )

    # ==================================================
    # 4. Controlled subsystem recovery
    # ==================================================

    simulator.recover_from_anomaly()

    recovered_state = simulator.state

    # ==================================================
    # 5. Verify communication recovery
    # ==================================================

    assert (
        recovered_state.communication.link_quality
        == 98.0
    )

    assert (
        recovered_state.communication.signal_strength
        == -62.0
    )

    assert (
        recovered_state.communication.packet_loss
        == 0.8
    )

    # ==================================================
    # 6. Verify spacecraft returned to NOMINAL
    # ==================================================

    assert (
        recovered_state.mode
        == SpacecraftMode.NOMINAL
    )

    # ==================================================
    # 7. Mission continuity
    # ==================================================

    mission_continuity = (
        recovered_state.mode
        == SpacecraftMode.NOMINAL
        and recovered_state.communication.link_quality
        == 98.0
        and recovered_state.communication.signal_strength
        == -62.0
        and recovered_state.communication.packet_loss
        == 0.8
    )

    assert mission_continuity