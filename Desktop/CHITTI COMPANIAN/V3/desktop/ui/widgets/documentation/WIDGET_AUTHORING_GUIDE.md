# CHITTI V2 — WIDGET AUTHORING GUIDE

## 1. Step-by-Step Widget Authoring
1. Inherit from `BaseWidget` (`desktop/ui/widgets/sdk/widget.py`).
2. Define a JSON manifest in `desktop/ui/widgets/manifests/<widget_type>.json`.
3. Implement the Widget Contract (`initialize`, `bind_session`, `update`, `render`).
4. Bind widget to a `WidgetSession` instance.
5. Use `WindowAttachment` API for positioning.

*Rule:* Never write provider-specific widgets. Always design generic widgets that consume normalized `WidgetSession` data.
