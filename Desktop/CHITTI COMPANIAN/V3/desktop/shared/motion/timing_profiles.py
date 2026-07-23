from desktop.shared.motion.motion_tokens import TimingToken

class TimingProfiles:
    """
    S36E: Canonical Timing Profiles mapping interaction types to timing tokens.
    """
    FAST_MS = TimingToken.FAST.value          # 120 ms
    NORMAL_MS = TimingToken.NORMAL.value      # 180 ms
    MEDIUM_MS = TimingToken.MEDIUM.value      # 240 ms
    SLOW_MS = TimingToken.SLOW.value          # 320 ms
    LONG_MS = TimingToken.LONG.value          # 450 ms
    BREATH_MS = TimingToken.BREATH.value      # 3000 ms
    IDLE_MS = TimingToken.IDLE.value          # 5000 ms
    SLEEP_MS = TimingToken.SLEEP.value        # 8000 ms
