# Vizzu Desktop Companion v1.0

## Final Project Folder Structure (Frozen)

```text
Vizzu/
│
├── app/
│   ├── main.py
│   ├── bootstrap.py
│   ├── startup.py
│   ├── shutdown.py
│   ├── lifecycle.py
│   └── version.py
│
├── core/
│   ├── assistant/
│   ├── conversation/
│   ├── planner/
│   ├── task_manager/
│   ├── scheduler/
│   ├── context/
│   ├── event_bus/
│   ├── state_machine/
│   ├── permissions/
│   └── capability_manager/
│
├── capabilities/
│   │
│   ├── voice/
│   │   ├── wakeword/
│   │   ├── speech_to_text/
│   │   └── text_to_speech/
│   │
│   ├── local_ai/
│   │   ├── model_manager/
│   │   ├── model_router/
│   │   ├── inference/
│   │   ├── embeddings/
│   │   ├── reranker/
│   │   ├── prompt_manager/
│   │   ├── context_builder/
│   │   ├── token_manager/
│   │   ├── conversation_engine/
│   │   ├── reasoning_engine/
│   │   ├── vision_models/
│   │   ├── speech_models/
│   │   ├── confidence/
│   │   ├── cache/
│   │   └── benchmarks/
│   │
│   ├── automation/
│   ├── browser/
│   ├── files/
│   ├── email/
│   ├── calendar/
│   ├── clipboard/
│   ├── observation/
│   ├── memory/
│   ├── knowledge/
│   ├── reasoning/
│   ├── intent_library/
│   ├── planning/
│   ├── vision/
│   ├── ocr/
│   ├── web/
│   ├── presentation/
│   ├── reminders/
│   ├── notifications/
│   ├── activity_center/
│   ├── undo_center/
│   ├── health_monitor/
│   ├── productivity/
│   ├── habits/
│   ├── focus/
│   ├── workspace/
│   ├── project_intelligence/
│   ├── companion/
│   └── utilities/
│
├── ui/
│   ├── tray/
│   ├── widget/
│   ├── dashboard/
│   ├── onboarding/
│   ├── settings/
│   ├── themes/
│   ├── animations/
│   ├── expressions/
│   └── windows/
│
├── infrastructure/
│   ├── database/
│   ├── storage/
│   ├── configuration/
│   ├── logging/
│   ├── indexing/
│   ├── cache/
│   ├── resources/
│   ├── services/
│   ├── models/
│   └── migrations/
│
├── plugins/
│   ├── sdk/
│   ├── manager/
│   ├── registry/
│   └── builtin/
│
├── assets/
│   ├── expressions/
│   │   ├── listening/
│   │   ├── thinking/
│   │   ├── talking/
│   │   ├── working/
│   │   ├── success/
│   │   ├── failure/
│   │   ├── waiting/
│   │   ├── monitoring/
│   │   ├── planning/
│   │   ├── reading/
│   │   ├── idle/
│   │   ├── exercise/
│   │   ├── sleeping/
│   │   ├── goodbye/
│   │   └── ...
│   │
│   ├── sounds/
│   ├── icons/
│   ├── themes/
│   ├── html/
│   └── prompts/
│
├── data/
│   ├── sqlite/
│   │   ├── memory.db
│   │   ├── observation.db
│   │   ├── projects.db
│   │   ├── intents.db
│   │   ├── reminders.db
│   │   ├── settings.db
│   │   └── knowledge.db
│   │
│   ├── backups/
│   ├── memories/
│   ├── observations/
│   ├── projects/
│   ├── experiences/
│   ├── intents/
│   │
│   └── logs/
│       ├── conversation/
│       ├── observation/
│       ├── automation/
│       ├── performance/
│       ├── learning/
│       ├── plugins/
│       ├── errors/
│       ├── crashes/
│       └── debug/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── experience/
│   ├── performance/
│   └── regression/
│
├── scripts/
│
├── docs/
│
├── .env
├── config.yaml
├── requirements.txt
├── LICENSE
└── README.md
```

---

# Module Responsibilities

| Folder | Responsibility |
|---------|----------------|
| **app** | Application lifecycle and startup/shutdown |
| **core** | Orchestration, planning, task coordination, application state |
| **capabilities** | All user-facing features and intelligence |
| **ui** | User interface, widgets, dashboards, animations |
| **infrastructure** | Database, storage, logging, configuration, shared services |
| **plugins** | Plugin SDK, manager, registry, built-in plugins |
| **assets** | Expressions, sounds, icons, HTML templates, prompts |
| **data** | User data, SQLite databases, backups, logs |
| **tests** | Unit, integration, experience and performance tests |
| **scripts** | Build and development scripts |
| **docs** | Engineering and product documentation |

---

# Frozen Architectural Rules

1. Every new feature belongs inside `capabilities/`.
2. `core/` is responsible only for orchestration and coordination.
3. Capabilities must communicate through well-defined interfaces.
4. `ui/` contains presentation only; no business logic.
5. User-generated data is stored only under `data/`.
6. Static resources belong only under `assets/`.
7. Every AI model interaction must go through `capabilities/local_ai/`.
8. Vizzu remains a standard desktop application that users can install, close, disable, and uninstall without affecting the operating system.
9. New features must fit into this architecture. Redesign the feature—not the architecture.
10. This folder structure is **Version 1.0 Frozen** and should not change unless a critical architectural issue is discovered.



-----------

# Vizzu Desktop Companion
## MVP Project Report v1.0
### (Master Project Specification)

---

# Project Name

**Vizzu – AI Desktop Companion**

Version: MVP v1.0

Status: Product Definition Frozen

---

# Project Goal

Build an **AI-powered Desktop Companion** that naturally understands the user's work, remembers meaningful experiences, automates desktop tasks, and collaborates like a trusted companion.

Vizzu is **NOT**

- A chatbot
- A voice assistant
- An operating system
- A shell replacement

Vizzu **IS**

- A Desktop Companion Application
- Local-first
- Privacy-first
- Event-driven
- AI-powered
- Installable & Uninstallable
- Human-centered

---

# Vision

Create a desktop companion that:

- Understands user intent
- Understands the desktop
- Understands projects
- Understands files
- Understands ongoing work
- Learns experiences
- Assists naturally
- Reduces user effort

The long-term goal is to create an AI companion that eventually powers a physical robot, but Version 1 is **Desktop Only**.

---

# Product Philosophy

> Companion before Automation.

Every feature should make Vizzu feel like a reliable companion rather than an automation script.

---

# MVP Principles

- Local First
- Privacy First
- Human Confirmation for Critical Actions
- Event before Vision
- Learn Execution, not only Knowledge
- Silent Learning
- Explain only when asked
- Companion before Automation
- Zero Friction
- Always Verify Important Actions

---

# Primary Target Users

1. General PC Users
2. Office Professionals
3. Knowledge Workers
4. Students
5. Researchers
6. Content Creators
7. Writers
8. Developers

---

# Product Identity

Category:

AI Desktop Companion

One-line Description:

An AI Desktop Companion that understands your work, remembers your journey and naturally helps you accomplish more.

---

# Core Capabilities

## Conversation

- Natural Conversation
- Voice Interaction
- Wake Word
- Multi-turn Conversation
- Context Awareness
- Follow-up Understanding
- Adaptive Tone
- Adaptive Humor
- Conversation Continuity
- Mobile Local Chat

---

## Observation

- Desktop Observation
- File Activity Tracking
- Application Tracking
- Browser Tracking
- Window Tracking
- Project Detection
- Activity Timeline
- Productivity Tracking
- Long-running Task Monitoring
- Event Monitoring
- Workflow Detection

---

## Memory

- Conversation Memory
- Project Memory
- Work Memory
- Knowledge Memory
- Personal Memory
- Experience Memory
- Timeline Memory
- Schedule Memory
- Silent Learning
- Memory Search
- History Search

---

## Local Intelligence

- Local Intent Library
- Intent Learning Engine
- Local Knowledge Base
- Local-first Execution
- Resource-aware Reasoning

---

## Automation

- Desktop Automation
- Browser Automation
- File Automation
- Email Automation
- Calendar Automation
- Workflow Automation
- Safe Automation
- Retry System
- Parallel Task Execution

---

## Planning

- Schedule Management
- Goal Tracking
- Task Queue
- Daily Planning
- Weekly Review
- Executive Planning

---

## File Intelligence

- Universal File Search
- File Knowledge
- Content Search
- Hands-free File Access
- Project File Grouping

---

## Vision

- OCR
- Screen Understanding
- UI Understanding
- Screenshot Intelligence
- Visual Verification

---

## Web Intelligence

- Intelligent Research
- Source Comparison
- Knowledge Gathering
- Web Summaries

---

## Presentation

- HTML Dashboards
- Cards
- Charts
- Timelines
- Storyboards
- Mind Maps
- Flowcharts
- Kanban Boards

---

## Productivity

- Daily Reports
- Weekly Reports
- Focus Sessions
- Productivity Analytics
- Project Dashboard

---

## Project Intelligence

- Project Detection
- Project Resume
- Context Packages
- Workspace Intelligence
- Project Analytics

---

## Companion

- Companion Presence
- Adaptive Expressions
- Adaptive Humor
- Daily Briefing
- End-of-Day Review
- Smart Silence

---

## Knowledge

- Knowledge Graph
- Decision Assistant
- Learning Mode
- Personal Knowledge

---

## Personalization

- Interest Learning
- Workflow Learning
- Software Preference Learning
- Working Pattern Learning

---

## Notifications

- Intelligent Notifications
- Background Completion
- Progress Updates
- Priority Notifications

---

## Reminder Engine

- Time-based Reminders
- Event-based Reminders
- Context-based Reminders
- Smart Reminder Negotiation
- Reminder History
- Reminder Priorities

---

## Activity Center

- Running Tasks
- Background Tasks
- ETA
- Queue
- Monitoring Status

---

## Notification Center

- Pending Notifications
- Completed Notifications
- Missed Notifications

---

## Undo Center

- Undo Actions
- Action History
- Recovery History

---

## Health Monitor

- AI Status
- Plugin Status
- Resource Usage
- Wake Word Status
- Vision Status
- Self Diagnostics

---

## Plugin System

- Plugin SDK
- Plugin Manager
- Plugin Registry
- Built-in Plugins

---

## Utility Center

- QR Generator
- QR Scanner
- Image Resize
- Image Compression
- PDF Merge
- PDF Split
- OCR
- Clipboard Manager
- Color Picker
- Unit Converter

---

## Focus & Habits

- Pomodoro
- Focus Timer
- Habit Tracker
- Habit Statistics
- Daily Dashboard

---

## Workspace

- Workspace Templates
- Workspace Restore
- Coding Workspace
- Writing Workspace
- Research Workspace

---

# AI Philosophy

Vizzu uses specialized local AI models.

One model should not perform every task.

Different models are used for:

- Conversation
- Planning
- Vision
- OCR
- Speech
- Embeddings
- Reranking

---

# Local Intent Library

Every successfully completed task becomes reusable knowledge.

Unknown Request

↓

LLM

↓

Execution

↓

Verification

↓

Saved as Local Intent

↓

Future executions require no LLM.

---

# Observation Philosophy

Observe:

- Events
- Projects
- Files
- Applications
- Tasks

Do NOT continuously record:

- Screen
- Keyboard
- Mouse
- Audio

Vision activates only when required.

---

# Privacy

- Local First
- SQLite Storage
- No Cloud Dependency
- Sensitive Data Never Stored
- Human Confirmation for Critical Actions
- User Controls Observation

---

# UI Philosophy

Normally:

Vizzu lives in the System Tray.

Wake Word

↓

Animated Widget slides onto the screen.

States include:

- Listening
- Thinking
- Working
- Monitoring
- Talking
- Success
- Failure
- Waiting
- Exercise
- Goodbye

When idle:

Exercises.

After inactivity:

Slides away while continuing background monitoring.

---

# MVP Success Criteria

The MVP is successful when users can naturally:

- Talk to Vizzu
- Open applications
- Search files
- Ask questions about files
- Receive reminders
- Monitor long-running tasks
- Continue previous work
- Get productivity summaries
- Receive HTML presentations
- Use desktop automation naturally

without feeling they are controlling software.

---

# Long-Term Vision

Future versions may add:

- Mobile Companion
- Robot Hardware
- Servo Expressions
- Cloud Synchronization
- Multi-device Support

These are **outside the MVP scope**.

---

# Development Strategy

The MVP will be built through **small, testable user experiences**, not massive feature batches.

Each sprint delivers one complete experience from conversation to execution, ensuring continuous progress, testing, and refinement.

---

# Final Statement

Vizzu is designed to become a trusted desktop companion that quietly understands the user's work, remembers meaningful experiences, and assists naturally while respecting privacy, maintaining user control, and reducing everyday friction.


-------------------------
