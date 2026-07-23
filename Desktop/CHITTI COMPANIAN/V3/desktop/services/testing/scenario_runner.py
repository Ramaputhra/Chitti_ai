import os
import time
from typing import Any, Dict, List

import yaml

from desktop.platform.configuration.events import SystemEvents
from desktop.platform.shared.interfaces.event_bus import Event, IEventBus
from desktop.platform.shared.interfaces.event_recorder import IEventRecorder
from desktop.platform.shared.interfaces.language import ILanguageRuntime
from desktop.platform.shared.interfaces.logging import ILoggingService
from desktop.platform.shared.interfaces.scenario_runner import IScenarioRunner
from desktop.platform.shared.interfaces.service import ServiceState


class ScenarioRunner(IScenarioRunner):
    def __init__(
        self,
        event_bus: IEventBus,
        logger: ILoggingService,
        language_runtime: ILanguageRuntime,
        event_recorder: IEventRecorder,
    ) -> None:
        self.event_bus = event_bus
        self.logger = logger
        self.language = language_runtime
        self.recorder = event_recorder
        self._state = ServiceState.STOPPED

    @property
    def name(self) -> str:
        return "ScenarioRunner"

    @property
    def state(self) -> ServiceState:
        return self._state

    def initialize(self) -> None:
        self._state = ServiceState.RUNNING
        self.logger.info(f"{self.name} initialized")

    def shutdown(self) -> None:
        self._state = ServiceState.STOPPED
        self.logger.info(f"{self.name} shutdown")

    def health_check(self) -> Dict[str, Any]:
        return {}

    def run_all(self, directory: str) -> bool:
        scenarios = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".yaml"):
                    scenarios.append(os.path.join(root, file))

        if not scenarios:
            self.logger.warning(f"No scenarios found in {directory}")
            return True

        self.logger.info(f"Found {len(scenarios)} scenarios. Starting test run...")
        
        all_passed = True
        for scenario_file in sorted(scenarios):
            if not self._run_single(scenario_file):
                all_passed = False
                
        if all_passed:
            self.logger.info("ALL SCENARIOS PASSED ✅")
        else:
            self.logger.error("ONE OR MORE SCENARIOS FAILED ❌")
            
        return all_passed

    def _run_single(self, filepath: str) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load scenario {filepath}: {e}")
            return False

        scenario_id = data.get("id", "UNKNOWN")
        name = data.get("name", "Unnamed")
        input_text = data.get("input", {}).get("text", "")
        expected = data.get("expected", {})
        timeout_ms = data.get("timeout", 2000)

        self.logger.info(f"Running Scenario: [{scenario_id}] {name}")
        self.recorder.clear_history()

        start_time = time.time()
        self.language.inject_text(input_text)

        # Wait up to timeout for processing to complete
        timeout_sec = timeout_ms / 1000.0
        end_time = start_time + timeout_sec

        expected_intent = expected.get("intent", {}).get("type")

        # Polling loop
        while time.time() < end_time:
            history = self.recorder.get_history()
            event_ids = [e.event_id for e in history]

            # Determine exit condition based on scenario type
            if expected_intent == "Ignore":
                if SystemEvents.INTENT_IGNORED in event_ids:
                    break
            else:
                if SystemEvents.RESPONSE_GENERATED in event_ids:
                    break

            time.sleep(0.01)

        latency_ms = (time.time() - start_time) * 1000

        # Validate assertions
        history = self.recorder.get_history()
        return self._validate(data, history, latency_ms)

    def _validate(
        self, data: Dict[str, Any], history: List[Event], latency_ms: float
    ) -> bool:
        expected = data.get("expected", {})
        expected_intent = expected.get("intent", {}).get("type")
        expected_response = expected.get("response", {}).get("text")
        expected_events = expected.get("events", [])

        perf = data.get("performance", {})
        max_latency = perf.get("max_latency", 5000)

        event_ids = [e.event_id for e in history]

        # 1. Validate Events Stream
        for ev in expected_events:
            if ev not in event_ids:
                self.logger.error(f"Validation Failed: Expected event '{ev}' not found.")
                return False

        # 2. Validate Intent
        if expected_intent:
            found_intent = False
            for e in history:
                if e.event_id == SystemEvents.INTENT_DETECTED:
                    intent = e.payload.get("intent")
                    if intent and intent.type == expected_intent:
                        found_intent = True
                        break
                elif e.event_id == SystemEvents.INTENT_IGNORED:
                    if expected_intent == "Ignore":
                        found_intent = True
                        break

            if not found_intent:
                self.logger.error(
                    f"Validation Failed: Expected intent '{expected_intent}' not matched."
                )
                return False

        # 3. Validate Response Text
        if expected_response:
            found_response = False
            for e in history:
                if e.event_id == SystemEvents.RESPONSE_GENERATED:
                    text = e.payload.get("text", "")
                    if text == expected_response:
                        found_response = True
                        break
            if not found_response:
                self.logger.error(
                    f"Validation Failed: Expected response '{expected_response}' not matched."
                )
                return False

        # 4. Validate Performance (Latency)
        if latency_ms > max_latency:
            self.logger.error(
                f"Validation Failed: Latency {latency_ms:.1f}ms exceeded max {max_latency}ms"
            )
            return False

        self.logger.info(f"Scenario [{data.get('id')}] PASS ✅ ({latency_ms:.1f}ms)")
        return True
