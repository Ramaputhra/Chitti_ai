# Risks and Mitigation

## Scope Creep
**Risk:** Project direction changing mid-build, potentially doubling or tripling project duration.
**Mitigation:** Strict phase-gated workflow. A phase cannot start until the previous phase is frozen and approved. No exceptions.

## Hardware Delays
**Risk:** Hardware integration blocking software progress.
**Mitigation:** Hardware deployment (Phase 11) only starts after the desktop MVP is stable. Implement simulation modes first (ESP32 simulation).
