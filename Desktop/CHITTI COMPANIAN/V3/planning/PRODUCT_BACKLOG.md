# CHITTI Product Backlog

*This is the single living document driving CHITTI's product evolution. Every change from this point onward comes from this backlog—not from inventing new architectural layers.*

## P0 (Critical)
*Focus: Operational Confidence. Collect telemetry and fix friction before adding features.*
- [ ] Measure and optimize Startup Time
- [ ] Measure and optimize Wake-word Latency
- [ ] Measure and optimize STT & TTS Latency
- [ ] Measure and optimize LLM & Tool Execution Latency
- [ ] Monitor Memory Growth over long sessions
- [ ] Track Crash frequency and recoverability
- [ ] Track Failed tool invocations and API limits
- [ ] Implement feedback loop for User corrections ("No, I meant...")

## P1 (Core Product)
*Focus: Establishing Version 0.1 & 0.2 (Personal Assistant & Desktop Operator)*
- [ ] Email: Reliable unread parsing, smart reply drafting, spam filtering
- [ ] Calendar: Reliable schedule ingestion, conflict detection, reminders
- [ ] Browser: Headless search, page extraction, summarization
- [ ] Notes: Seamless capture, semantic linking, search
- [ ] Files: Semantic search, automated cleanup, moving downloads

## P2 (User Experience)
*Focus: Establishing Version 0.3 (Creative Assistant & Polish)*
- [ ] Better conversations: Interruptibility, tone matching, emotional memory
- [ ] Better voice: Expression-syncing, localized low-latency TTS
- [ ] UI polish: Smooth animations, system tray integration, unobtrusive overlays
- [ ] Notifications: Non-intrusive semantic alerts ("You have a meeting in 10")
- [ ] Screenplay & Writing workflows

## P3 (Future)
*Focus: Establishing Version 0.4+ and Hardware Embodiment*
- [ ] Autonomous Agent: Scheduled tasks, folder watching, proactive briefings
- [ ] Robot: ESP32 integration, Servo mapping, LED matrices
- [ ] Vision enhancements: Always-on screen context, real-world camera context
- [ ] IoT: Smart home integration
- [ ] Mobile: Companion app for on-the-go syncing
