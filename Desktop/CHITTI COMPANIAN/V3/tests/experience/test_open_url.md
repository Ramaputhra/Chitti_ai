# Experience Test: Open URL

**Goal**: The user can voice command Vizzu to open a website, and it reliably opens in the default browser with a natural voice confirmation.

## Acceptance Criteria

- [ ] Vizzu wakes upon hearing "Hey Vizzu".
- [ ] User says "Open github.com".
- [ ] Vizzu acknowledges with "Sure Boss" or similar.
- [ ] OS Automation Capability triggers `webbrowser.open(url)`.
- [ ] Execution success event is published to Event Bus.
- [ ] Vizzu responds with "Done" or "Website is open".
- [ ] The default browser launches and navigates to the requested URL.
