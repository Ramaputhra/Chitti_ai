# CHITTI V2 — CHARACTER BEHAVIOR CATALOG

## 1. Overview
This catalog documents every behavior clip registered in `Character Studio` (`desktop/character/studio/assets/runtime/behaviors/`).

---

## 2. System Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| Boot | `CHR_BOOT_001` | system | False | 1.0 | HIGH | True | System startup boot animation |
| Wake | `CHR_WAKE_001` | system | False | 1.0 | HIGH | True | Waking from sleep or idle state |
| SlideInLeft | `CHR_TRANS_SLIDE_IN_L_001` | system | False | 0.8 | NORMAL | True | Desktop entry transition from left |
| SlideInRight | `CHR_TRANS_SLIDE_IN_R_001` | system | False | 0.8 | NORMAL | True | Desktop entry transition from right |
| SlideOutLeft | `CHR_TRANS_SLIDE_OUT_L_001` | system | False | 0.8 | NORMAL | True | Desktop exit transition to left |
| SlideOutRight | `CHR_TRANS_SLIDE_OUT_R_001` | system | False | 0.8 | NORMAL | True | Desktop exit transition to right |
| GreetingMorning | `CHR_GREET_MORNING_001` | system | False | 1.0 | NORMAL | True | Morning greeting |
| GreetingAfternoon | `CHR_GREET_AFTERNOON_001` | system | False | 1.0 | NORMAL | True | Afternoon greeting |
| GreetingEvening | `CHR_GREET_EVENING_001` | system | False | 1.0 | NORMAL | True | Evening greeting |
| WelcomeBack | `CHR_GREET_WELCOME_001` | system | False | 1.0 | NORMAL | True | User return detection |
| Goodbye | `CHR_GOODBYE_001` | system | False | 1.0 | NORMAL | True | System shutdown / exit |
| Idle | `CHR_IDLE_001` | system | True | 2.0 | LOW | True | Default resting state |
| IdleBlink | `CHR_IDLE_BLINK_001` | system | False | 0.5 | LOW | True | Periodic eye blink micro-animation |
| IdleBreathing | `CHR_IDLE_BREATH_001` | system | True | 2.0 | LOW | True | Subtly breathing idle state |
| IdleLookAround | `CHR_IDLE_LOOK_001` | system | False | 1.5 | LOW | True | Looking around desktop |
| Stretch | `CHR_IDLE_STRETCH_001` | system | False | 1.5 | LOW | True | Long idle stretch gesture |
| Sleepy | `CHR_SLEEP_001` | system | True | 2.0 | LOW | True | Inactive sleepy state |
| Yawn | `CHR_SLEEP_YAWN_001` | system | False | 1.5 | LOW | True | Transition to sleepy state |
| BecomeEdgeDot | `CHR_MODE_DOT_001` | system | False | 1.0 | HIGH | True | Minimizing to screen edge dot |
| RestoreFromDot | `CHR_MODE_RESTORE_001` | system | False | 1.0 | HIGH | True | Restoring from screen edge dot |

---

## 3. Listening Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| Listening | `CHR_LISTEN_001` | listening | True | 1.0 | HIGH | True | Voice capture active |
| ListeningFocused | `CHR_LISTEN_FOCUSED_001` | listening | True | 1.0 | HIGH | True | High-fidelity voice attention |
| ListeningCurious | `CHR_LISTEN_CURIOUS_001` | listening | True | 1.0 | HIGH | True | Ambiguous user query listening |
| Waiting | `CHR_LISTEN_WAITING_001` | listening | True | 1.5 | NORMAL | True | Awaiting user input |
| InterruptListening | `CHR_LISTEN_INTERRUPT_001` | listening | False | 0.5 | HIGH | True | User barge-in speech detection |

---

## 4. Thinking Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| Thinking | `CHR_THINK_001` | thinking | True | 1.0 | HIGH | True | Cognitive planning active |
| ThinkingDeep | `CHR_THINK_DEEP_001` | thinking | True | 1.5 | HIGH | True | Complex reasoning workflow |
| SearchingMemory | `CHR_SEARCH_MEM_001` | thinking | True | 1.2 | NORMAL | True | Episodic memory query |
| SearchingInternet | `CHR_SEARCH_NET_001` | thinking | True | 1.2 | NORMAL | True | Web search runtime active |
| Reading | `CHR_READ_001` | thinking | True | 1.5 | NORMAL | True | Document / screen OCR parsing |
| Calculating | `CHR_CALC_001` | thinking | True | 1.2 | NORMAL | True | Math / telemetry computation |
| Analyzing | `CHR_ANALYZE_001` | thinking | True | 1.2 | NORMAL | True | Analytics pattern extraction |
| Confused | `CHR_CONFUSED_001` | thinking | False | 1.0 | HIGH | True | Ambiguous workflow resolution |

---

## 5. Speaking Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| TalkingNeutral | `CHR_TALK_NEUTRAL_001` | speaking | True | 1.0 | HIGH | True | General TTS speech response |
| TalkingHappy | `CHR_TALK_HAPPY_001` | speaking | True | 1.0 | HIGH | True | Positive outcome speech |
| TalkingProfessional | `CHR_TALK_PRO_001` | speaking | True | 1.0 | HIGH | True | Executive / formal speech |
| TalkingExplain | `CHR_TALK_EXPLAIN_001` | speaking | True | 1.2 | HIGH | True | Multi-step explanation speech |
| TalkingStory | `CHR_TALK_STORY_001` | speaking | True | 1.2 | HIGH | True | Narrative narration |
| TalkingQuestion | `CHR_TALK_QUESTION_001` | speaking | True | 1.0 | HIGH | True | Asking user confirmation |
| TalkingReminder | `CHR_TALK_REMINDER_001` | speaking | True | 1.0 | HIGH | True | Reminder notification speech |
| TalkingPresentation | `CHR_TALK_PRES_001` | speaking | True | 1.2 | HIGH | True | Presentation dashboard narration |
| TalkingNavigation | `CHR_TALK_NAV_001` | speaking | True | 1.0 | HIGH | True | Navigation guidance speech |
| TalkingBrowser | `CHR_TALK_BROWSER_001` | speaking | True | 1.0 | HIGH | True | Browser workflow speech |
| TalkingVision | `CHR_TALK_VISION_001` | speaking | True | 1.0 | HIGH | True | Visual analysis speech |
| TalkingProductivity | `CHR_TALK_PROD_001` | speaking | True | 1.0 | HIGH | True | Telemetry summary speech |
| TalkingWarning | `CHR_TALK_WARN_001` | speaking | True | 1.0 | HIGH | True | Error / alert notification |

---

## 6. Working Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| TypingLaptop | `CHR_WORK_TYPING_001` | working | True | 1.2 | NORMAL | True | Automated typing activity |
| WritingNotes | `CHR_WORK_NOTES_001` | working | True | 1.2 | NORMAL | True | Note logging |
| SearchingFiles | `CHR_WORK_SEARCH_FILES_001` | working | True | 1.2 | NORMAL | True | Local file search |
| SearchingFolders | `CHR_WORK_SEARCH_FOLDERS_001` | working | True | 1.2 | NORMAL | True | Directory scanning |
| OrganizingFiles | `CHR_WORK_ORG_FILES_001` | working | True | 1.2 | NORMAL | True | File sorting workflow |
| CopyingFiles | `CHR_WORK_COPY_FILES_001` | working | True | 1.0 | NORMAL | True | File copy operation |
| MovingFiles | `CHR_WORK_MOVE_FILES_001` | working | True | 1.0 | NORMAL | True | File move operation |
| DeletingFiles | `CHR_WORK_DEL_FILES_001` | working | False | 1.0 | NORMAL | True | File cleanup operation |
| Printing | `CHR_WORK_PRINT_001` | working | True | 1.2 | NORMAL | True | Print job dispatch |
| WatchingPrinter | `CHR_WORK_WATCH_PRINT_001` | working | True | 1.2 | NORMAL | True | Awaiting print completion |
| Scanning | `CHR_WORK_SCAN_001` | working | True | 1.2 | NORMAL | True | Document scan operation |
| Uploading | `CHR_WORK_UPLOAD_001` | working | True | 1.0 | NORMAL | True | Network upload task |
| Downloading | `CHR_WORK_DOWNLOAD_001` | working | True | 1.0 | NORMAL | True | Network download task |
| Installing | `CHR_WORK_INSTALL_001` | working | True | 1.2 | NORMAL | True | Package installation |
| Compiling | `CHR_WORK_COMPILE_001` | working | True | 1.5 | NORMAL | True | Build compilation task |
| Coding | `CHR_WORK_CODING_001` | working | True | 1.5 | NORMAL | True | Code editing activity |

---

## 7. Presentation Gestures

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| PointLeft | `CHR_GEST_POINT_L_001` | presentation_gestures | False | 0.8 | NORMAL | True | Pointing to left UI panel |
| PointRight | `CHR_GEST_POINT_R_001` | presentation_gestures | False | 0.8 | NORMAL | True | Pointing to right UI panel |
| PointScreen | `CHR_GEST_POINT_SCR_001` | presentation_gestures | False | 0.8 | NORMAL | True | Pointing to screen center |
| PointTimeline | `CHR_GEST_POINT_TL_001` | presentation_gestures | False | 0.8 | NORMAL | True | Pointing to activity timeline |
| PointChart | `CHR_GEST_POINT_CHART_001` | presentation_gestures | False | 0.8 | NORMAL | True | Pointing to stat chart |
| PresentDashboard | `CHR_GEST_PRES_DASH_001` | presentation_gestures | False | 1.0 | NORMAL | True | Executive dashboard gesture |
| PresentMap | `CHR_GEST_PRES_MAP_001` | presentation_gestures | False | 1.0 | NORMAL | True | Navigation map gesture |
| PresentImage | `CHR_GEST_PRES_IMG_001` | presentation_gestures | False | 1.0 | NORMAL | True | Vision image gesture |

---

## 8. Success & Warning Behaviors

| Behavior Name | Behavior ID | Category | Loopable | Duration (s) | Priority | Interruptible | Typical Usage |
|---|---|---|---|---|---|---|---|
| ThumbsUp | `CHR_SUCC_THUMBSUP_001` | success | False | 1.0 | HIGH | True | Approval / confirmation |
| Celebrate | `CHR_SUCC_CELEBRATE_001` | success | False | 1.5 | HIGH | True | Goal completed celebration |
| HappyJump | `CHR_SUCC_JUMP_001` | success | False | 1.0 | HIGH | True | Enthusiastic success |
| Smile | `CHR_SUCC_SMILE_001` | success | False | 1.0 | NORMAL | True | Subtle success expression |
| Satisfied | `CHR_SUCC_SATISFIED_001` | success | False | 1.0 | NORMAL | True | Workflow success state |
| Warning | `CHR_WARN_001` | warning | False | 1.0 | HIGH | True | Caution alert gesture |
| Oops | `CHR_WARN_OOPS_001` | warning | False | 0.8 | HIGH | True | Minor mistake gesture |
| Retry | `CHR_WARN_RETRY_001` | warning | False | 1.0 | HIGH | True | Action retry gesture |
| Concern | `CHR_WARN_CONCERN_001` | warning | False | 1.0 | HIGH | True | Warning concern state |
| Error | `CHR_WARN_ERR_001` | warning | False | 1.2 | HIGH | True | Critical error state |
