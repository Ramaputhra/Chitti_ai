# CHITTI Desktop Provider Recommendation

Based on the isolated evaluation of capability coverage, reliability, maintenance health, and dependency replacement, the following is the official recommendation for the CHITTI Desktop Automation Provider Stack.

## Final Stack Recommendation

```text
Primary UI Automation:
- uiautomation

Secondary OS/Window Management:
- pywin32

Utilities (Process Verification):
- psutil

Fallback (Blind Execution):
- PyAutoGUI

Rejected (Superseded/Unnecessary):
- pywinauto
- pywinctl
- keyboard
- mouse
- AutoHotkey
- SikuliX
```

## Architectural Justification

### 1. Why `uiautomation` is the Primary
It directly wraps `UIAutomationCore.dll`. It provides the fastest UI tree traversal currently available in Python, fully supports modern UWP and Electron apps (which `pywinauto` struggles with), and requires only `comtypes` as a dependency. It allows CHITTI to "read" the screen semantically rather than blindly clicking coordinates.

### 2. Why `pywin32` is the Secondary Native Layer
While `uiautomation` handles the content *inside* windows, `pywin32` handles the windows themselves. It provides direct access to the Windows API for maximizing, focusing, setting Z-order, and polling for raw HWNDs. It is the de-facto standard for Windows Python environments.

### 3. Why `psutil` is Included
When a Planner step states "Launch application X", the Verification Runtime must prove it launched. `os.startfile` is asynchronous and returns nothing. `psutil` allows the runtime to securely monitor process creation, CPU usage, and memory footprint to confirm the application successfully booted and stabilized.

### 4. Why `PyAutoGUI` is relegated to Fallback
It is purely coordinate and pixel-based. It breaks if the user moves a window, changes DPI, or switches to dark mode. It should be strictly reserved as the lowest-tier execution fallback for applications that intentionally block UIAutomation APIs (e.g., video games, custom DRM software).

## Integration with the Frozen Architecture

This stack integrates perfectly into the v1.0 Frozen Architecture.

The `CapabilityRuntime` will instantiate a `DesktopProvider` interface. 
When the `WorkflowRuntime` requests a capability like `sys.desktop.click_button`, the provider will internally route to:
1. `uiautomation` (to semantically find and click the button).
2. If the button is entirely invisible to the accessibility tree, it will fail over to `PyAutoGUI` (using vision-based coordinates).

This ensures the Planner never needs to know *how* a button is clicked, maintaining the strict separation of concerns required by Rule 26.
