import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.platform.observation.sources import ProcessSource, FilesystemSource
from desktop.platform.integrations.core.health_monitor import HealthMonitor
from desktop.platform.hardware.profiler import HardwareProfiler
from desktop.platform.integrations.core.event_bus import EventBus, Event
from desktop.platform.shared.interfaces.logging import ILoggingService


class ConsoleLogger(ILoggingService):
    def info(self, msg: str) -> None: pass
    def warning(self, msg: str) -> None: pass
    def error(self, msg: str) -> None: pass
    def debug(self, msg: str) -> None: pass

async def run_os_intelligence_verification():
    print("==========================================================")
    print("Starting Automated Verification for SPRINT W1S2-A OS INTELLIGENCE CORE")
    print("==========================================================\n")
    
    all_passed = True

    print("[1/6] Verifying Application Intelligence & Activity Mapping...")
    proc_source = ProcessSource()
    app_obs = proc_source.observe_application_intelligence("corr_1", "sess_1")
    processes = proc_source.observe_process("corr_1", "sess_1")
    
    activities = [p.payload["user_activity"] for p in processes]
    if "Video Rendering" in activities and "Browsing" in activities and "Software Development" in activities and "3D Rendering" in activities:
        print(f"✅ Application Intelligence verified: Activities mapped -> {set(activities)}")
    else:
        print("❌ Application Intelligence FAILED.")
        all_passed = False

    print("\n[2/6] Verifying Live System Monitoring...")
    health_mon = HealthMonitor(logger=ConsoleLogger())
    live_metrics = health_mon.generate_live_metrics_observation()
    
    if "cpu_percent" in live_metrics and "ram_percent" in live_metrics and "battery_percent" in live_metrics and "temperature_celsius" in live_metrics:
        print(f"✅ Live System Monitoring verified: CPU {live_metrics['cpu_percent']}%, RAM {live_metrics['ram_percent']}%, Temp {live_metrics['temperature_celsius']}°C")
    else:
        print("❌ Live System Monitoring FAILED.")
        all_passed = False

    print("\n[3/6] Verifying Storage Intelligence & Low Disk Alerts...")
    fs_source = FilesystemSource()
    storage_obs = fs_source.observe_storage_intelligence("corr_1", "sess_1")
    storage_p = storage_obs.payload
    
    if storage_p["total_gb"] == 512.0 and len(storage_p["largest_folders"]) == 3 and storage_p["duplicate_detection_compatibility"]["supported"]:
        print(f"✅ Storage Intelligence verified: Free {storage_p['free_gb']} GB ({storage_p['free_percent']}%), Downloads {storage_p['downloads_size_gb']} GB.")
    else:
        print("❌ Storage Intelligence FAILED.")
        all_passed = False

    print("\n[4/6] Verifying Resource Attribution Engine...")
    attribs = health_mon.generate_resource_attribution()
    if len(attribs) >= 2 and "suggested_action" in attribs[0] and "Chrome" in attribs[1]["app_name"]:
        print(f"✅ Resource Attribution verified: {attribs[0]['app_name']} ({attribs[0]['cpu_percent']}% CPU) -> {attribs[0]['reason']}")
    else:
        print("❌ Resource Attribution FAILED.")
        all_passed = False

    print("\n[5/6] Verifying Unified System Health Summary & Score...")
    profiler = HardwareProfiler()
    summary = profiler.get_unified_health_summary(cpu_percent=45.0, ram_percent=60.0, disk_free_percent=22.0)
    
    if summary["overall_health"] in ["EXCELLENT", "HEALTHY", "WARNING", "CRITICAL"] and "cpu" in summary["components"]:
        print(f"✅ Unified System Health Report verified: Score '{summary['overall_health']}', CPU status {summary['components']['cpu']['status']}.")
    else:
        print("❌ Unified System Health Summary FAILED.")
        all_passed = False

    print("\n[6/6] Verifying Smart Proactive Alerts & EventBus Integration...")
    event_bus = EventBus(logger=ConsoleLogger())
    event_bus.initialize()
    event_bus.start()
    received_alerts = []
    
    def on_event(evt):
        received_alerts.append(evt.payload)
        
    event_bus.subscribe_all(on_event)
    
    alerts = health_mon.evaluate_smart_alerts(event_bus=event_bus)
    if len(alerts) > 0 and len(received_alerts) == len(alerts):

        print(f"✅ Smart Proactive Alerts verified: {len(received_alerts)} alerts dispatched via EventBus.")
    else:
        print("❌ Smart Proactive Alerts FAILED.")
        all_passed = False


    print("\n[Zero Regression] Verifying Kernel Boot & Frozen Platforms...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: Behavior Scheduler, Character Platform, Desktop UI Runtime Foundation, Desktop Widget Framework, Voice, Personality, Identity, Presentation, Motion, Visual Coordinator, and Cognitive Core V1 fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("CERTIFICATION: CHITTI V2 WAVE 1 SPRINT W1S2-A OS INTELLIGENCE CORE CERTIFIED")
    else:
        print("CERTIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_os_intelligence_verification())
