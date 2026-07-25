# Experience Test: Open Folder

**Goal**: The user can voice command Vizzu to open a specific folder, and it reliably opens with a natural voice confirmation.

## Acceptance Criteria

- [ ] Vizzu wakes upon hearing "Hey Vizzu".
- [ ] User says "Open my Documents folder".
- [ ] Vizzu acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `os.startfile(folder_path)`.
- [ ] Execution success event is published to Event Bus.
- [ ] Vizzu responds with "Done" or "Folder is open".
- [ ] The correct folder is visible in Windows File Explorer.
