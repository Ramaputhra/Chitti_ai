# Experience Test: Open Folder

**Goal**: The user can voice command CHITTI to open a specific folder, and it reliably opens with a natural voice confirmation.

## Acceptance Criteria

- [ ] CHITTI wakes upon hearing "Hey Chitti".
- [ ] User says "Open my Documents folder".
- [ ] CHITTI acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `os.startfile(folder_path)`.
- [ ] Execution success event is published to Event Bus.
- [ ] CHITTI responds with "Done" or "Folder is open".
- [ ] The correct folder is visible in Windows File Explorer.
