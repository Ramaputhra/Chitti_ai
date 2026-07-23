# CHITTI V2 — SESSION BINDING SPECIFICATION

## 1. Runtime Session Decoupling
Widgets bind ONLY to Runtime Sessions (`WidgetSession`), never directly to Capability implementations.

```
Capability -> Runtime Session -> WidgetSession -> Widget -> Desktop UI Runtime
```

- When a runtime session starts, `WidgetManager` creates/binds a corresponding widget.
- When a runtime session completes, the widget automatically detaches and closes.
