# Acceptance Scenarios (Sprint 4: Milestone 1)

These scenarios define the acceptance criteria for Milestone 1. They bypass the physical microphone and test the cognitive language pipeline (Language -> Intent -> Plan -> Response).

## Scenario 001: Greeting
- **Input text:** "Hello Chitti" (Injected via Dev Console)
- **Expected Intent:** `Greeting`
- **Expected Response Text:** "Hello! How can I help you today?"
- **Success Criteria:** Speaker outputs synthesized text, Dev Console shows successful workflow completion.

## Scenario 002: Identity
- **Input text:** "Who are you?"
- **Expected Intent:** `Identity`
- **Expected Response Text:** "I am Chitti, your AI Companion."

## Scenario 003: Gratitude
- **Input text:** "Thank you"
- **Expected Intent:** `Gratitude`
- **Expected Response Text:** "You're very welcome!"

## Scenario 004: Farewell
- **Input text:** "Goodbye"
- **Expected Intent:** `Farewell`
- **Expected Response Text:** "Goodbye! Have a great day."

## Scenario 005: Ignore / Noise
- **Input text:** "noise" or "   "
- **Expected Intent:** `Ignore`
- **Expected Response Text:** None. The pipeline should halt at Intent parsing and emit `Intent.Ignored`.

## Scenario 006: Replay
- **Input text:** N/A (Click "Replay History" in Dev Console)
- **Expected Intent:** Replays whatever events were stored in `EventRecorder` sequentially.
- **Success Criteria:** System reacts exactly as if the events were generated organically in real-time.
