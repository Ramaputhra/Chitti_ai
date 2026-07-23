# Experience Test: Open Notepad

**Goal**: The user can voice command CHITTI to open Notepad, and it reliably opens with a natural voice confirmation.

## Acceptance Criteria

- [ ] CHITTI wakes upon hearing "Hey Chitti".
- [ ] User says "Open Notepad".
- [ ] CHITTI acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `os.startfile('notepad.exe')`.
- [ ] Execution success event is published to Event Bus.
- [ ] CHITTI responds with "Done" or "Notepad is ready".
- [ ] Notepad is visible on the desktop.
