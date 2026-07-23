# CHITTI V2 — WIDGET MANIFEST SPECIFICATION

Every desktop widget provides a JSON manifest in `desktop/ui/widgets/manifests/`.

## 1. Schema Fields & Versioning

```json
{
  "manifest_version": "1.0.0",
  "widget_version": "1.0.0",
  "widget_id": "widget_media",
  "display_name": "Media Widget",
  "category": "MEDIA",
  "version": "1.0.0",
  "description": "Canonical CHITTI Media Playback Widget",
  "supported_runtime_sessions": ["Media"],
  "default_attachment": "CHARACTER_ANCHOR",
  "preferred_window_layer": "CHARACTER_WIDGET",
  "render_profile": "WIDGET",
  "theme": "Dark",
  "supports_compact": true,
  "supports_expanded": true,
  "supports_notifications": true,
  "supports_hot_reload": true,
  "icon": "media_icon.svg",
  "accent_color": "#89B4FA",
  "minimum_size": { "w": 280, "h": 160 },
  "preferred_size": { "w": 360, "h": 240 }
}
```

## 2. Versioning Definitions
- `manifest_version`: Version of the manifest schema.
- `widget_version`: Version of the widget implementation.

## 3. Widget Categories
- `MEDIA`: Media playback widgets.
- `COMMUNICATION`: Email, Messaging, Browser widgets.
- `SYSTEM`: Battery, System Monitor widgets.
- `PRODUCTIVITY`: Reminder, Alarm, Productivity widgets.
- `AUTOMATION`: Clipboard, Download, Upload widgets.
- `PRESENTATION`: Presentation, Slide Deck widgets.
- `VISION`: Camera, OCR, Vision widgets.
- `UTILITY`: Timer, Weather, Navigation, Printer widgets.

## 4. Legacy Manifest Migration
If `manifest_version` or `category` is missing in legacy manifests, `WidgetManifestLoader` automatically populates default values (`manifest_version: "1.0.0"`, default category mapping) without raising errors.
