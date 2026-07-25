# Experience Test: Open Notepad

**Goal**: The user can voice command Vizzu to open Notepad, and it reliably opens with a natural voice confirmation.

## Acceptance Criteria

- [ ] Vizzu wakes upon hearing "Hey Vizzu".
- [ ] User says "Open Notepad".
- [ ] Vizzu acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `os.startfile('notepad.exe')`.
- [ ] Execution success event is published to Event Bus.
- [ ] Vizzu responds with "Done" or "Notepad is ready".
- [ ] Notepad is visible on the desktop.
