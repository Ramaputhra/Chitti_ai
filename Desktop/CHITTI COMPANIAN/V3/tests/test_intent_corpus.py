import asyncio
import json
import logging
import sys
import os
from dataclasses import dataclass
from typing import List, Dict, Any

# Ensure we import from V3, not a globally installed V2
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from desktop.app.kernel import RuntimeKernel
from desktop.models.interaction import IntentResult, InteractionEnvelope
from desktop.runtimes.ai.runtime import AIRuntime
from desktop.runtimes.ai.intent_validator import IntentValidator
from desktop.platform.inference.inference.gguf_provider import GGUFInferenceProvider
from desktop.runtimes.inference.runtime import InferenceRuntime
from desktop.app.context import EventBus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntentCorpus")
logger.setLevel(logging.WARNING) # Mute most output during run

@dataclass
class CorpusEntry:
    text: str
    expected_intent: str
    
@dataclass
class TestResult:
    entry: CorpusEntry
    actual_intent: str
    passed: bool
    raw_json: str
    validator_output: Any

CORPUS = [
    # SmallTalkIntent
    CorpusEntry("hello there", "SmallTalkIntent"),
    CorpusEntry("hi chitti", "SmallTalkIntent"),
    CorpusEntry("good morning", "SmallTalkIntent"),
    CorpusEntry("how are you today", "SmallTalkIntent"),
    CorpusEntry("what's up", "SmallTalkIntent"),
    CorpusEntry("hey man", "SmallTalkIntent"),
    CorpusEntry("greetings", "SmallTalkIntent"),
    CorpusEntry("good evening", "SmallTalkIntent"),
    CorpusEntry("nice to meet you", "SmallTalkIntent"),
    CorpusEntry("hi", "SmallTalkIntent"),

    # QuestionIntent
    CorpusEntry("who is the president of the united states", "QuestionIntent"),
    CorpusEntry("what is the capital of france", "QuestionIntent"),
    CorpusEntry("when did world war 2 end", "QuestionIntent"),
    CorpusEntry("how do airplanes fly", "QuestionIntent"),
    CorpusEntry("what is photosynthesis", "QuestionIntent"),
    CorpusEntry("who wrote hamlet", "QuestionIntent"),
    CorpusEntry("explain quantum computing", "QuestionIntent"),
    CorpusEntry("what is the deepest ocean", "QuestionIntent"),
    CorpusEntry("why is the sky blue", "QuestionIntent"),
    CorpusEntry("tell me a fun fact about space", "QuestionIntent"),

    # ReasoningIntent
    CorpusEntry("what is 2+2", "ReasoningIntent"),
    CorpusEntry("calculate the square root of 144", "ReasoningIntent"),
    CorpusEntry("if i have 5 apples and eat 2, how many are left", "ReasoningIntent"),
    CorpusEntry("what is 15 percent of 80", "ReasoningIntent"),
    CorpusEntry("solve for x: 2x = 10", "ReasoningIntent"),
    CorpusEntry("is 17 a prime number", "ReasoningIntent"),
    CorpusEntry("what is the probability of flipping heads twice", "ReasoningIntent"),
    CorpusEntry("convert 100 fahrenheit to celsius", "ReasoningIntent"),
    CorpusEntry("multiply 45 by 12", "ReasoningIntent"),
    CorpusEntry("divide 100 by 4", "ReasoningIntent"),

    # DistanceIntent
    CorpusEntry("how far is paris from london", "DistanceIntent"),
    CorpusEntry("distance between new york and los angeles", "DistanceIntent"),
    CorpusEntry("how many miles from earth to the moon", "DistanceIntent"),
    CorpusEntry("what is the driving distance from here to chicago", "DistanceIntent"),
    CorpusEntry("how long does it take to drive to seattle", "DistanceIntent"),
    CorpusEntry("distance from tokyo to kyoto", "DistanceIntent"),
    CorpusEntry("how far away is the sun", "DistanceIntent"),
    CorpusEntry("give me the distance to the nearest gas station", "DistanceIntent"),
    CorpusEntry("what's the distance between miami and orlando", "DistanceIntent"),
    CorpusEntry("how many kilometers from berlin to munich", "DistanceIntent"),

    # CommandIntent
    CorpusEntry("get_identity", "CommandIntent"),
    CorpusEntry("show system diagnostics", "CommandIntent"),
    CorpusEntry("clear the terminal", "CommandIntent"),
    CorpusEntry("run the backup script", "CommandIntent"),
    CorpusEntry("empty the trash", "CommandIntent"),
    CorpusEntry("increase system volume", "CommandIntent"),
    CorpusEntry("turn off the wifi", "CommandIntent"),
    CorpusEntry("take a screenshot", "CommandIntent"),
    CorpusEntry("lock the screen", "CommandIntent"),
    CorpusEntry("restart the computer", "CommandIntent"),

    # StateQueryIntent
    CorpusEntry("did the backup finish", "StateQueryIntent"),
    CorpusEntry("what is the status of the download", "StateQueryIntent"),
    CorpusEntry("is the compilation done", "StateQueryIntent"),
    CorpusEntry("did my last command succeed", "StateQueryIntent"),
    CorpusEntry("show me the progress of the installation", "StateQueryIntent"),
    CorpusEntry("what happened to the file transfer", "StateQueryIntent"),
    CorpusEntry("is the server still running", "StateQueryIntent"),
    CorpusEntry("did you launch the app", "StateQueryIntent"),
    CorpusEntry("tell me if the script crashed", "StateQueryIntent"),
    CorpusEntry("what is the current memory usage", "StateQueryIntent"),

    # LaunchAppIntent
    CorpusEntry("open calculator", "LaunchAppIntent"),
    CorpusEntry("launch vscode", "LaunchAppIntent"),
    CorpusEntry("start chrome", "LaunchAppIntent"),
    CorpusEntry("open microsoft word", "LaunchAppIntent"),
    CorpusEntry("run notepad", "LaunchAppIntent"),
    CorpusEntry("launch spotify", "LaunchAppIntent"),
    CorpusEntry("open the terminal", "LaunchAppIntent"),
    CorpusEntry("start task manager", "LaunchAppIntent"),
    CorpusEntry("open settings", "LaunchAppIntent"),
    CorpusEntry("launch paint", "LaunchAppIntent"),

    # CloseAppIntent
    CorpusEntry("close calculator", "CloseAppIntent"),
    CorpusEntry("kill vscode", "CloseAppIntent"),
    CorpusEntry("terminate chrome", "CloseAppIntent"),
    CorpusEntry("exit microsoft word", "CloseAppIntent"),
    CorpusEntry("close notepad", "CloseAppIntent"),
    CorpusEntry("shut down spotify", "CloseAppIntent"),
    CorpusEntry("close the terminal", "CloseAppIntent"),
    CorpusEntry("kill task manager", "CloseAppIntent"),
    CorpusEntry("close settings", "CloseAppIntent"),
    CorpusEntry("quit paint", "CloseAppIntent"),

    # ResumeActivityIntent
    CorpusEntry("resume my coding project", "ResumeActivityIntent"),
    CorpusEntry("continue where i left off", "ResumeActivityIntent"),
    CorpusEntry("bring back my workspace", "ResumeActivityIntent"),
    CorpusEntry("restore the previous session", "ResumeActivityIntent"),
    CorpusEntry("open my recent files", "ResumeActivityIntent"),
    CorpusEntry("resume writing my essay", "ResumeActivityIntent"),
    CorpusEntry("reopen the tabs from yesterday", "ResumeActivityIntent"),
    CorpusEntry("continue the data analysis task", "ResumeActivityIntent"),
    CorpusEntry("bring up my dev environment", "ResumeActivityIntent"),
    CorpusEntry("resume work", "ResumeActivityIntent"),

    # ClarificationIntent
    CorpusEntry("do it", "ClarificationIntent"),
    CorpusEntry("fix this", "ClarificationIntent"),
    CorpusEntry("run", "ClarificationIntent"),
    CorpusEntry("make it stop", "ClarificationIntent"),
    CorpusEntry("change the thing", "ClarificationIntent"),
    CorpusEntry("go back", "ClarificationIntent"),
    CorpusEntry("start", "ClarificationIntent"),
    CorpusEntry("help me with that", "ClarificationIntent"),
    CorpusEntry("what about the other one", "ClarificationIntent"),
    CorpusEntry("use it", "ClarificationIntent"),
]

class MockInteraction:
    def __init__(self, text):
        self.original_text = text
        self.resolved_entities = []

class DummyRegistry:
    def get_all(self):
        return []

async def run_corpus():
    print(f"Loading GGUF model and warming up cache for {len(CORPUS)} tests...")
    event_bus = EventBus()
    provider = GGUFInferenceProvider()
    inference = InferenceRuntime(event_bus, provider)
    ai = AIRuntime(inference, cap_registry=DummyRegistry())
    
    # We don't need full kernel, just these runtimes
    await inference.initialize(None)
    await ai.initialize(None)
    await inference.start()
    await ai.start()
    
    print("\\n--- Intent Regression Corpus Started ---\\n")
    
    results: List[TestResult] = []
    
    for idx, entry in enumerate(CORPUS):
        print(f"[{idx+1}/{len(CORPUS)}] Testing: '{entry.text}' (Expected: {entry.expected_intent})")
        interaction = MockInteraction(entry.text)
        
        # We manually perform what AIRuntime.resolve_intent does so we can capture raw JSON
        # Build prompt
        system_prompt = """
You are the CHITTI intent parser. Convert the user's request into a strict JSON object.

# Intent Decision Matrix

- QuestionIntent: For factual questions, general knowledge, trivia, and generic inquiries.
- ReasoningIntent: For math, logic puzzles, calculations, and analytical thinking. (Rule: Never map math to DistanceIntent).
- DistanceIntent: For physical geospatial routing, navigation, or physical distance between locations.
- CommandIntent: For executing specific catalog actions, system operations, or tool workflows. Provide the 'action' parameter.
- StateQueryIntent: When the user asks about the status, progress, or outcome of a recent system action.
- LaunchAppIntent: For opening or launching local desktop applications (e.g. calculator, vscode, chrome).
- CloseAppIntent: For closing or terminating local desktop applications.
- OpenBrowserIntent: For navigating to specific web URLs (e.g. facebook.com).
- ResumeActivityIntent: For resuming past coding work or projects.
- ClarificationIntent: When the request is completely ambiguous and requires asking the user for more details.
- SmallTalkIntent: For general greetings, pleasantries, and casual conversation.

# Examples (Positive & Negative Boundaries)

Input: "what is 2+2"
Output: {"intent": "ReasoningIntent", "confidence": 0.99, "parameters": {"query": "2+2"}}
(Negative Boundary: Math is ReasoningIntent, NOT DistanceIntent.)

Input: "how far is paris from london"
Output: {"intent": "DistanceIntent", "confidence": 0.99, "parameters": {"query": "distance from paris to london"}}

Input: "open calculator"
Output: {"intent": "LaunchAppIntent", "confidence": 0.98, "parameters": {"app_command": "calc.exe"}}

Input: "get_identity"
Output: {"intent": "CommandIntent", "confidence": 0.95, "parameters": {"action": "get_identity"}}
(Rule: Specific system commands map to CommandIntent.)

Input: "did the backup finish?"
Output: {"intent": "StateQueryIntent", "confidence": 0.90, "parameters": {"query": "did the backup finish?"}}

Output ONLY raw JSON. No markdown formatting.
"""
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": entry.text}
        ]
        
        try:
            resp = provider.core.generate(messages, tools_enabled=False)
            raw_json = resp.get("text", "{}")
        except Exception as e:
            raw_json = str(e)
            
        validator_result = IntentValidator.validate(raw_json, "test_id", "test")
        
        actual = "ClarificationIntent" # Default fallback
        if validator_result:
            actual = validator_result.intent
            
        passed = (actual == entry.expected_intent)
        
        results.append(TestResult(
            entry=entry,
            actual_intent=actual,
            passed=passed,
            raw_json=raw_json,
            validator_output=validator_result
        ))
        
        if passed:
            print(f"  -> PASS")
        else:
            print(f"  -> FAIL (Got {actual})")
            
    # Metrics
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    overall_acc = (passed / total) * 100
    
    print(f"\\n=========================================")
    print(f"OVERALL ACCURACY: {overall_acc:.2f}% ({passed}/{total})")
    print(f"=========================================\\n")
    
    categories = {}
    for r in results:
        cat = r.entry.expected_intent
        if cat not in categories:
            categories[cat] = {"total": 0, "pass": 0, "fails": []}
        categories[cat]["total"] += 1
        if r.passed:
            categories[cat]["pass"] += 1
        else:
            categories[cat]["fails"].append(r)
            
    for cat, data in categories.items():
        acc = (data["pass"] / data["total"]) * 100
        print(f"{cat}: {acc:.2f}% ({data['pass']}/{data['total']})")
        
    print("\\n--- FAILED PROMPTS ---")
    for cat, data in categories.items():
        for f in data["fails"]:
            print(f"\\n[FAIL] {f.entry.text}")
            print(f"Expected: {f.entry.expected_intent}")
            print(f"Actual:   {f.actual_intent}")
            print(f"Raw JSON: {f.raw_json}")

if __name__ == "__main__":
    asyncio.run(run_corpus())
