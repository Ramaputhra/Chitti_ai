import os
import sys
import json
import wave
import struct
from PIL import Image, ImageDraw, ImageFont

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
STUDIO_ROOT = os.path.join(v3_root, "desktop", "ui", "studio")
ASSETS_ROOT = os.path.join(STUDIO_ROOT, "assets")
DOCS_ROOT = os.path.join(STUDIO_ROOT, "documentation")

def create_placeholder_wav(filepath, duration_sec=0.5):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    sample_rate = 8000
    n_samples = int(sample_rate * duration_sec)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        data = bytearray()
        for i in range(n_samples):
            val = int(400 * (i % 30 < 15))
            data.extend(struct.pack('<h', val))
        wav_file.writeframes(data)

def create_placeholder_svg(filepath, label_text):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <rect width="200" height="200" fill="#0f172a" rx="16"/>
  <rect x="10" y="10" width="180" height="180" fill="none" stroke="#3b82f6" stroke-width="2" rx="12"/>
  <circle cx="100" cy="80" r="30" fill="#3b82f6" opacity="0.8"/>
  <text x="100" y="140" fill="#f8fafc" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle">{label_text}</text>
  <text x="100" y="165" fill="#64748b" font-family="sans-serif" font-size="10" text-anchor="middle">DESKTOP UI ICON</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def create_mock_png(filepath, asset_id, asset_name, category):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    width, height = 320, 180
    img = Image.new("RGBA", (width, height), (15, 23, 42, 240))
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([6, 6, width - 6, height - 6], outline=(59, 130, 246, 255), width=2)
    
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((16, 20), f"UI Category: {category.upper()}", fill=(148, 163, 184, 255), font=font)
    draw.text((16, 45), f"ID: {asset_id}", fill=(248, 250, 252, 255), font=font)
    draw.text((16, 70), f"Name: {asset_name}", fill=(56, 189, 248, 255), font=font)
    
    draw.rectangle([16, 105, width - 16, 125], fill=(30, 41, 59, 255), outline=(51, 65, 85, 255))
    draw.text((24, 110), "Replace with Production Artwork", fill=(244, 63, 94, 255), font=font)
    draw.text((16, 145), "Desktop UI Studio V1.0", fill=(100, 116, 139, 255), font=font)
    
    img.save(filepath, "PNG")

def generate_all_ui_assets():
    print("[1/5] Creating Desktop UI Studio Directories...")
    dirs = [
        "overlays", "dialogs", "notifications", "countdown", "timers",
        "badges", "indicators", "icons", "animations", "sounds",
        "widgets", "transitions", "themes", "mock"
    ]
    for d in dirs:
        os.makedirs(os.path.join(ASSETS_ROOT, d), exist_ok=True)
    os.makedirs(DOCS_ROOT, exist_ok=True)

    print("[2/5] Generating Placeholder SVG Icons...")
    icon_names = [
        "alarm", "bell", "clock", "mail", "printer", "folder", "calendar",
        "cloud", "battery", "wifi", "bluetooth", "microphone", "camera",
        "clipboard", "download", "upload", "shutdown", "restart"
    ]
    for ic in icon_names:
        create_placeholder_svg(os.path.join(ASSETS_ROOT, "icons", f"{ic}.svg"), ic.upper())

    print("[3/5] Generating Category Mock UI Assets (PNG & JSON)...")
    categories = {
        "alarm": ["AlarmSet", "AlarmCountdown", "AlarmFiveMinutes", "AlarmOneMinute", "AlarmRinging", "AlarmDismissed", "AlarmSnoozed"],
        "reminder": ["ReminderCreated", "ReminderPending", "ReminderDue", "ReminderCompleted", "ReminderExpired"],
        "email": ["EmailReceived", "EmailReading", "EmailSending", "EmailSent", "EmailFailed"],
        "shutdown": ["ShutdownScheduled", "ShutdownCountdown", "ShutdownCancelled", "ShutdownNow"],
        "download": ["DownloadStarting", "DownloadProgress", "DownloadPaused", "DownloadCompleted", "DownloadFailed"],
        "upload": ["UploadStarting", "UploadProgress", "UploadCompleted", "UploadFailed"],
        "printer": ["PrinterReady", "Printing", "PaperOut", "PrinterError", "WatchingPrinter"],
        "system_status": ["BatteryCharging", "BatteryLow", "BatteryCritical", "WiFiConnecting", "WiFiConnected", "WiFiDisconnected", "BluetoothConnected", "BluetoothDisconnected"],
        "notifications": ["Info", "Warning", "Success", "Error", "Question"],
        "overlays": ["CornerNotification", "Toast", "FloatingBubble", "EdgeBubble", "SystemBadge", "MiniOverlay"],
        "dialogs": ["ConfirmationDialog", "WarningDialog", "ErrorDialog", "InfoDialog", "ProgressDialog"],
        "countdown": ["FiveMinutes", "OneMinute", "ThirtySeconds", "TenSeconds", "ProgressRing", "ProgressBar"],
        "timers": ["DigitalTimer", "CircularTimer", "MinimalTimer"]
    }

    for cat, items in categories.items():
        cat_dir = os.path.join(ASSETS_ROOT, cat)
        for item in items:
            asset_id = f"UI_{cat.upper()}_{item.upper()}"
            png_file = os.path.join(cat_dir, f"{item}.png")
            json_file = os.path.join(cat_dir, f"{item}.json")
            
            create_mock_png(png_file, asset_id, item, cat)
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump({
                    "asset_id": asset_id,
                    "asset_name": item,
                    "category": cat,
                    "format": "png",
                    "resolution": "320x180",
                    "has_alpha": True
                }, f, indent=2)

    print("[4/5] Generating Placeholder Sound Effects...")
    sound_files = [
        "notification.wav", "alarm.wav", "success.wav", "warning.wav",
        "email.wav", "shutdown.wav", "printer.wav", "download.wav", "upload.wav"
    ]
    for sf in sound_files:
        create_placeholder_wav(os.path.join(ASSETS_ROOT, "sounds", sf), duration_sec=0.4)

    print("[5/5] Generating Placeholder Animations...")
    anim_folders = ["pulse", "blink", "bounce", "slide", "fade", "scale", "rotate", "ring", "glow"]
    for af in anim_folders:
        anim_dir = os.path.join(ASSETS_ROOT, "animations", af)
        os.makedirs(anim_dir, exist_ok=True)
        css_file = os.path.join(anim_dir, f"{af}.css")
        with open(css_file, "w", encoding="utf-8") as f:
            f.write(f"/* Desktop UI Animation: {af} */\n@keyframes {af} {{\n  from {{ opacity: 0; }}\n  to {{ opacity: 1; }}\n}}\n.{af}-anim {{\n  animation: {af} 0.3s ease-in-out;\n}}\n")

    print("Desktop UI Studio setup complete.")

if __name__ == "__main__":
    generate_all_ui_assets()
