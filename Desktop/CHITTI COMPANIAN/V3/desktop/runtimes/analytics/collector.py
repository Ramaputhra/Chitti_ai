import time
import json
import uuid
from typing import Any, Optional
from desktop.models.analytics import AnalyticsRecord

class AnalyticsCollector:
    """
    S32A: Internal telemetry collector stage composed inside AnalyticsRuntime.
    Normalizes heterogenous system events into standard AnalyticsRecord domain models.
    """

    def normalize_event(self, event: Any) -> Optional[AnalyticsRecord]:
        """
        Translates raw EventBus events into canonical AnalyticsRecord model.
        """
        if not event:
            return None

        record_id = f"rec_{uuid.uuid4().hex[:12]}"
        event_name = event.__class__.__name__
        timestamp = getattr(event, "timestamp", time.time())
        if isinstance(timestamp, (int, float)):
            ts_val = float(timestamp)
        else:
            ts_val = time.time()

        session_id = getattr(event, "session_id", "global") or "global"
        
        # 1. ExecutionCompletedEvent
        if event_name == "ExecutionCompletedEvent":
            trace = getattr(event, "trace", None)
            result = getattr(event, "verification_result", None)
            meta = getattr(event, "metadata", {}) or {}

            duration = getattr(trace, "total_duration_ms", meta.get("duration_ms", 0.0)) if trace else meta.get("duration_ms", 0.0)
            status_str = "SUCCESS"
            if result and hasattr(result, "status"):
                status_str = "SUCCESS" if "SUCCESS" in str(result.status) else "FAILURE"
            elif trace and hasattr(trace, "overall_status"):
                status_str = "SUCCESS" if "SUCCESS" in str(trace.overall_status) else "FAILURE"
            elif "status" in meta:
                status_str = str(meta["status"])

            payload = {
                "trace_id": getattr(trace, "trace_id", meta.get("trace_id", "")) if trace else meta.get("trace_id", ""),
                "correlation_id": getattr(event, "correlation_id", ""),
                "verification_status": str(getattr(result, "status", status_str)) if result else status_str
            }

            return AnalyticsRecord(
                record_id=record_id,
                event_type="EXECUTION_COMPLETED",
                source_subsystem="VerificationRuntime",
                session_id=session_id,
                timestamp=ts_val,
                duration_ms=duration,
                status=status_str,
                payload_json=json.dumps(payload)
            )

        # 2. CapabilityExecutedEvent / ExecutionStep
        elif "Capability" in event_name or hasattr(event, "capability_name"):
            cap_name = getattr(event, "capability_name", "unknown_capability")
            duration = getattr(event, "duration_ms", 0.0)
            status_str = getattr(event, "status", "SUCCESS")
            
            payload = {
                "capability_name": cap_name,
                "parameters": getattr(event, "parameters", {})
            }

            return AnalyticsRecord(
                record_id=record_id,
                event_type="CAPABILITY_EXECUTED",
                source_subsystem="ExecutionRuntime",
                session_id=session_id,
                timestamp=ts_val,
                duration_ms=duration,
                status=str(status_str),
                payload_json=json.dumps(payload)
            )

        # 3. UserActivityEvent (S32B)
        elif event_name == "UserActivityEvent":
            app_name = getattr(event, "app_name", "Desktop")
            window_title = getattr(event, "window_title", "")
            duration = getattr(event, "duration_ms", 0.0)

            payload = {
                "app_name": app_name,
                "window_title": window_title
            }

            return AnalyticsRecord(
                record_id=record_id,
                event_type="USER_ACTIVITY",
                source_subsystem="DesktopActivityRuntime",
                session_id=session_id,
                timestamp=ts_val,
                duration_ms=duration,
                status="INFO",
                payload_json=json.dumps(payload)
            )

        # 4. Generic Event Fallback
        else:
            payload = {"event_class": event_name}
            return AnalyticsRecord(
                record_id=record_id,
                event_type=event_name.upper(),
                source_subsystem="EventBus",
                session_id=session_id,
                timestamp=ts_val,
                duration_ms=0.0,
                status="INFO",
                payload_json=json.dumps(payload)
            )
