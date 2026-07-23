# CHITTI V2 — MASTER CAPABILITY OWNERSHIP & FEATURE MAPPING AUDIT
**(Canonical Architectural Ownership Map & Future Feature Boundary Rules)**

======================================================================
## 1. EXECUTIVE SUMMARY & PERMANENT OWNERSHIP RULE
======================================================================

A comprehensive, non-destructive audit of the CHITTI V2 repository (`c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3`) was conducted to establish the **permanent canonical capability hierarchy**.

### Permanent Architectural Rule:
```
######################################################################
                  CANONICAL OWNERSHIP INVARIANT

   "ALL future features SHALL extend existing canonical capability packages.

   Creating new top-level capability packages is STRICTLY PROHIBITED 
   unless the feature represents an entirely new physical domain."
######################################################################
```

---

======================================================================
## 2. CANONICAL CAPABILITY TREE (EXISTING ARCHITECTURE)
======================================================================

```text
desktop/capabilities/
├── desktop/                      [Desktop Operations Platform]
│   ├── app_launcher.py           (Application Launch & Process Focus)
│   ├── clipboard.py              (Win32 Clipboard Read/Write/Clear)
│   ├── media_control.py          (Multimedia Play/Pause/Volume Key Control)
│   ├── automation/               (Win32 Mouse Click & Key Input Automation)
│   └── filesystem/               (File Search, Find File, Organize Downloads)
│
├── browser/                      [Browser Intelligence Platform]
│   ├── search_capability.py      (Web Search Engine Querying)
│   ├── browser_capability.py     (Playwright Browser Session & Navigation)
│   ├── webpage_capability.py     (Web Page Markdown Content Extraction)
│   └── research_capability.py    (Multi-Query Deep Research Synthesis)
│
├── screen_understanding/          [Vision & Visual Intelligence Platform]
│   ├── capability.py             (OCR Screen Layout Parsing & Bounding Boxes)
│   ├── episode_detector.py       (Visual Transition Detection)
│   └── fusion.py                 (Visual-Semantic Snapshot Fusion)
│
├── utilities/                    [System Utilities & Computation Platform]
│   ├── calculator.py             (Mathematical Expression Evaluator)
│   ├── time_cap.py               (Timezone Conversion & World Clock)
│   ├── weather_capability.py     (Weather Forecast Schema & API Bridge)
│   └── distance_nav/             (Geographic Distance & Route Steps)
│
├── communications/               [Communication & Productivity Adapters]
│   ├── gmail_provider.py         (Email Schema & SMTP/OAuth Bridge)
│   └── calendar_provider.py      (Calendar Event Lookup & Scheduling)
│
└── work_continuity/              [Workspace Continuity & Session Restore]
    ├── capability.py             (Workspace Restore Plan & Activity Reconstruction)
    └── policy.py                 (Context Restoration Policy Evaluator)
```

---

======================================================================
## 3. FUTURE FEATURE MAPPING (50+ UPCOMING FEATURES)
======================================================================

Below is the permanent engineering mapping for all future user features into existing canonical capability packages:

| # | Proposed Future Feature | Target Canonical Capability Package | Repository Folder | Target Owner Runtime | Architectural Justification |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **ZIP Compression / Extract** | `FilesystemCapability` | `desktop/capabilities/desktop/filesystem/` | `CapabilityRuntime` | Native file operation belonging to file management. |
| **2** | **PDF Text Extraction** | `VisionCapability` / `OCR` | `desktop/capabilities/screen_understanding/` | `VerificationRuntime` | Visual/text parsing of document layouts. |
| **3** | **PDF Form Filling** | `DesktopAutomationCapability` | `desktop/capabilities/desktop/automation/` | `ExecutionSpine` | Form element focus and typing automation. |
| **4** | **Markdown Export** | `FilesystemCapability` | `desktop/capabilities/desktop/filesystem/` | `CapabilityRuntime` | File generation and formatting. |
| **5** | **DOCX Report Exporter** | `FilesystemCapability` | `desktop/capabilities/desktop/filesystem/` | `CapabilityRuntime` | Office document file generation. |
| **6** | **Excel CSV Data Analyzer** | `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | Structured data calculation & analysis. |
| **7** | **Spotify Playlist Control**| `MediaControlCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Extends media playback controls. |
| **8** | **YouTube Audio Stream** | `BrowserCapability` | `desktop/capabilities/browser/` | `BrowserRuntime` | Browser-based audio/video session. |
| **9** | **Volume Master Slider** | `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | System Win32 audio output control. |
| **10**| **Display Brightness** | `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Win32 display management. |
| **11**| **Wi-Fi & Bluetooth Toggle**| `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | OS hardware adapter toggles. |
| **12**| **Power Sleep / Hibernate** | `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | OS power state management. |
| **13**| **Task Manager Kill App** | `AppLauncherCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Process lifecycle management. |
| **14**| **Todo & Task List Manager**| `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | User productivity data structures. |
| **15**| **Quick Scratchpad Notes** | `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | Lightweight productivity storage. |
| **16**| **Slack / Teams Messenger** | `CommunicationsCapability` | `desktop/capabilities/communications/` | `CapabilityRuntime` | Instant messaging channel integration. |
| **17**| **VS Code Workspace Bridge**| `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Developer editor process automation. |
| **18**| **Git Commit & Status** | `DesktopAutomationCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Developer CLI automation. |
| **19**| **Screen Video Recording** | `ScreenUnderstandingCapability` | `desktop/capabilities/screen_understanding/` | `VerificationRuntime` | Visual capture & video frame encoding. |
| **20**| **Screenshot Annotator** | `ScreenUnderstandingCapability` | `desktop/capabilities/screen_understanding/` | `VerificationRuntime` | Image modification & bounding boxes. |
| **21**| **Clipboard History Manager**| `ClipboardCapability` | `desktop/capabilities/desktop/` | `CapabilityRuntime` | Extends system clipboard tracking. |
| **22**| **Batch Image Converter** | `FilesystemCapability` | `desktop/capabilities/desktop/filesystem/` | `CapabilityRuntime` | Bulk file transformation. |
| **23**| **File Duplicate Finder** | `FilesystemCapability` | `desktop/capabilities/desktop/filesystem/` | `CapabilityRuntime` | Disk scanning and hash matching. |
| **24**| **Remote Companion QR Pair**| `CommunicationsCapability` | `desktop/capabilities/communications/` | `CapabilityRuntime` | Channel router client pairing. |
| **25**| **Mobile Chat Handoff** | `CommunicationsCapability` | `desktop/capabilities/communications/` | `CapabilityRuntime` | Channel routing interaction. |
| **26**| **Network Speed Tester** | `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | Connectivity diagnostic. |
| **27**| **Window Grid Snap Manager**| `DesktopAutomationCapability` | `desktop/capabilities/desktop/automation/` | `CapabilityRuntime` | Win32 window positioning. |
| **28**| **Local Password Reader** | `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | Encrypted secret retrieval. |
| **29**| **Currency & Unit Converter**| `CalculatorCapability` | `desktop/capabilities/utilities/calculator.py` | `CapabilityRuntime` | Mathematical evaluation. |
| **30**| **Python Sandbox Executor**| `UtilitiesCapability` | `desktop/capabilities/utilities/` | `CapabilityRuntime` | Isolated code execution. |

---

======================================================================
## 4. ARCHITECTURAL BOUNDARY & OWNERSHIP RULES
======================================================================

1. **Browser Isolation (Rule 59 / Rule 60):** All browser navigation, web scraping, and DOM extraction MUST occur exclusively within `desktop/capabilities/browser/` using Playwright adapters. Capabilities MUST NEVER invoke Playwright directly.
2. **Filesystem Isolation:** All disk operations (create, read, write, copy, move, compress, delete) MUST reside inside `desktop/capabilities/desktop/filesystem/`.
3. **Desktop Automation Isolation:** All native Win32 window positioning, focus, mouse click, and keyboard typing operations MUST reside inside `desktop/capabilities/desktop/automation/`.
4. **Vision & OCR Isolation:** Screen capture, OCR text extraction, layout tree construction, and visual bounding box mapping MUST reside inside `desktop/capabilities/screen_understanding/`.
5. **No Duplicate AI Providers (Rule 37 / Rule 40):** Future LLM or vision model providers MUST extend `InferenceRuntime` (`desktop/platform/ai/`) and MUST NOT instantiate separate AI runtimes.
6. **Remote Companion Channel Routing (Rule 240):** Mobile clients and external endpoints MUST route requests into `ConversationRuntime` through the `ChannelRouter` without directly invoking capabilities.

---

======================================================================
## 5. CAPABILITY EXPANSION GUIDE
======================================================================

### A. Desktop Package (`desktop/capabilities/desktop/`):
- **Allowed Scope:** App launching, process focus/kill, clipboard management, media keys, Win32 window positioning, volume/brightness/power automation, file compression, file manipulation.
- **Forbidden:** Direct Playwright browser automation, direct OCR layout parsing.

### B. Browser Package (`desktop/capabilities/browser/`):
- **Allowed Scope:** Web search, Playwright navigation, web page markdown parsing, deep research, web video playback sessions.
- **Forbidden:** Win32 window manipulation outside browser frames, direct filesystem operations.

### C. Vision Package (`desktop/capabilities/screen_understanding/`):
- **Allowed Scope:** Screenshot capture, OCR layout trees, visual bounding boxes, screen recording clips, screenshot annotation.
- **Forbidden:** Synthesizing speech, executing workflow plans directly.

### D. Utilities Package (`desktop/capabilities/utilities/`):
- **Allowed Scope:** Mathematical calculation, unit conversion, timezone/clock conversion, weather forecasts, route step calculations, todo lists, scratch notes, sandbox execution.
- **Forbidden:** Rendering native desktop windows, managing audio synthesis.

---

======================================================================
## 6. FINAL ENGINEERING DECISION
======================================================================

```
######################################################################
                PERMANENT ARCHITECTURAL DECISION

   "Creating new top-level capability packages is PROHIBITED.

   All future features for EPIC 38 and beyond SHALL be implemented
   by adding submodules to existing canonical packages:
   - desktop/capabilities/desktop/
   - desktop/capabilities/browser/
   - desktop/capabilities/screen_understanding/
   - desktop/capabilities/utilities/
   - desktop/capabilities/communications/
   - desktop/capabilities/work_continuity/"
######################################################################
```
