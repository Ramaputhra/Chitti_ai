# Desktop Automation Technology Evaluation

## 1. Project Health & Dependency Analysis

| Library | Last Update | Python 3.13 | Dependencies | Native/Binary |
|---------|-------------|-------------|--------------|---------------|
| `uiautomation` | Aug 2025 | Yes (via comtypes) | `comtypes` | Wraps MS UIAutomationCore.dll |
| `pywinauto` | Jan 2025 | Issues Reported | `comtypes`, `six`, `pywin32` | None (wraps APIs) |
| `pywin32` | Highly Active | Yes | None | Native C extensions |
| `PyAutoGUI` | May 2023 | Issues Reported | `Pillow`, `pyscreeze`, `mouseinfo`, `PyGetWindow`, etc. | None (pure python + ctypes) |
| `pywinctl` | Sep 2024 | Yes | `pywin32` (on Windows) | None |
| `keyboard` / `mouse` | Stagnant | Yes | None | C hook wrappers |
| `psutil` | Highly Active | Yes | None | Native C extensions |

## 2. Capability Coverage

| Capability | `uiautomation` | `pywinauto` | `pywin32` | `PyAutoGUI` | `pywinctl` |
|------------|----------------|-------------|-----------|-------------|------------|
| Read UI Tree | ✅ Excellent | ⚠️ Slow | ❌ No | ❌ No | ❌ No |
| Button/Text | ✅ Yes | ✅ Yes | ⚠️ Hard | ❌ Blind | ❌ No |
| Background Click | ✅ Yes (Patterns) | ✅ Yes | ✅ Yes (SendMessage) | ❌ No | ❌ No |
| Multi-monitor | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Buggy | ✅ Yes |
| UWP/Electron | ✅ Yes | ⚠️ Partial | ❌ No | ❌ Blind | ❌ No |
| Process ID | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ❌ No |

## 3. Dependency Replacement Analysis (The Elimination Round)

The core objective is to identify libraries that supersede others to minimize the dependency footprint.

### `pywinauto` vs `uiautomation`
- **Overlap:** Nearly 100%. Both attempt to wrap MS UIAutomation (and legacy Win32).
- **Winner:** `uiautomation`. It is significantly faster at parsing large UI trees (like browsers or complex Electron apps), has fewer transitive dependencies, and receives more frequent maintenance. 
- **Decision:** Reject `pywinauto` to avoid overlapping scopes.

### `keyboard` & `mouse` vs `pywin32` & `uiautomation`
- **Overlap:** Simulating keystrokes and mouse clicks.
- **Winner:** `uiautomation` and `pywin32`. `uiautomation` uses control patterns (e.g., `InvokePattern`) which often don't even require stealing the physical mouse cursor. For raw input, `pywin32` can utilize `SendInput`. The `keyboard`/`mouse` libraries by boppreh rely on global OS hooks which frequently trigger antivirus flags or require administrative privileges.
- **Decision:** Reject `keyboard` and `mouse`.

### `pywinctl` vs `pywin32`
- **Overlap:** Window geometry, finding monitors, minimizing/maximizing.
- **Winner:** `pywin32`. `pywinctl` is excellent for cross-platform apps, but CHITTI is strictly a Windows desktop companion. Adding a cross-platform abstraction layer that ultimately just calls `pywin32` under the hood is unnecessary bloat.
- **Decision:** Reject `pywinctl`.

### `PyAutoGUI`
- **Overlap:** Mouse/Keyboard automation.
- **Analysis:** PyAutoGUI is entirely "blind." It cannot read window titles or text boxes; it can only click on coordinate X/Y or search for template image matches via OpenCV/Pillow.
- **Decision:** Keep as a strict **Fallback**. It should only be invoked if a target application has completely disabled accessibility frameworks (e.g., legacy Java apps without Access Bridge, or full-screen DirectX games).

## 4. Prototype Validation (Isolated Findings)

In our scratch environments, we attempted to launch Notepad, type text, click menus, and close.

1. **`uiautomation`**: 
   - *Result*: 100% Success. 
   - *Notes*: Easily located the Notepad "Text Editor" control, injected text without using the clipboard, and cleanly navigated the "File -> Exit" menu tree. Extremely fast.
2. **`pywin32`**:
   - *Result*: 100% Success.
   - *Notes*: Requires manually querying HWNDs and sending `WM_SETTEXT` messages. Highly reliable but very verbose. Best reserved for window management rather than deep UI interaction.
3. **`psutil`**:
   - *Result*: 100% Success.
   - *Notes*: Perfectly complimented OS launch commands by providing exact PIDs and process lifecycles.
4. **`PyAutoGUI`**:
   - *Result*: Partial Success.
   - *Notes*: Requires hardcoding coordinates or taking screenshots of the Notepad UI. Broke instantly when the OS theme was switched to Dark Mode. Confirms it must only be a fallback.
