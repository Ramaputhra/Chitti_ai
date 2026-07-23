# Experience Test: Open URL

**Goal**: The user can voice command CHITTI to open a website, and it reliably opens in the default browser with a natural voice confirmation.

## Acceptance Criteria

- [ ] CHITTI wakes upon hearing "Hey Chitti".
- [ ] User says "Open github.com".
- [ ] CHITTI acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `webbrowser.open(url)`.
- [ ] Execution success event is published to Event Bus.
- [ ] CHITTI responds with "Done" or "Website is open".
- [ ] The default browser launches and navigates to the requested URL.
