import os
import sys
import json
import wave
import struct
from PIL import Image, ImageDraw, ImageFont

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

STUDIO_ROOT = os.path.join(v3_root, "desktop", "character", "studio")
SOURCE_ROOT = os.path.join(STUDIO_ROOT, "assets", "source")
RUNTIME_ROOT = os.path.join(STUDIO_ROOT, "assets", "runtime")
DOCS_ROOT = os.path.join(STUDIO_ROOT, "documentation")

def create_placeholder_wav(filepath, duration_sec=0.5):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    sample_rate = 8000
    n_samples = int(sample_rate * duration_sec)
    
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        # Generate low volume silent/click tone
        data = bytearray()
        for i in range(n_samples):
            val = int(500 * (i % 20 < 10))
            data.extend(struct.pack('<h', val))
        wav_file.writeframes(data)

def create_placeholder_svg(filepath, label_text):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#1e293b" rx="20"/>
  <rect x="20" y="20" width="360" height="360" fill="none" stroke="#6366f1" stroke-width="4" stroke-dasharray="8 8" rx="10"/>
  <text x="200" y="190" fill="#f8fafc" font-family="sans-serif" font-size="20" font-weight="bold" text-anchor="middle">{label_text}</text>
  <text x="200" y="230" fill="#94a3b8" font-family="sans-serif" font-size="14" text-anchor="middle">SOURCE ASSET PLACEHOLDER</text>
</svg>'''
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_content)

def create_frame_png(filepath, behavior_id, behavior_name, frame_num, total_frames=14):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    width, height = 300, 300
    img = Image.new("RGBA", (width, height), (30, 41, 59, 230))
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([10, 10, width - 10, height - 10], outline=(99, 102, 241, 255), width=3)
    
    # Try default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # Text overlays
    draw.text((20, 30), f"ID: {behavior_id}", fill=(248, 250, 252, 255), font=font)
    draw.text((20, 60), f"Name: {behavior_name}", fill=(226, 232, 240, 255), font=font)
    draw.text((20, 90), f"Frame: {frame_num:02d} / {total_frames:02d}", fill=(56, 189, 248, 255), font=font)
    
    # Visual indicator of frame progress
    box_w = (width - 40) / total_frames
    for f in range(total_frames):
        color = (99, 102, 241, 255) if f < frame_num else (71, 85, 105, 255)
        draw.rectangle([20 + f * box_w, 140, 20 + (f + 1) * box_w - 2, 160], fill=color)
        
    draw.text((20, 220), "Replace with production artwork", fill=(244, 63, 94, 255), font=font)
    draw.text((20, 250), "CHITTI Character Studio V1.0", fill=(148, 163, 184, 255), font=font)
    
    img.save(filepath, "PNG")

def create_behavior_clip(category, behavior_dir_name, behavior_id, behavior_name, is_loop=False, priority="NORMAL", duration=1.0, tags=None):
    clip_dir = os.path.join(RUNTIME_ROOT, "behaviors", category, behavior_dir_name)
    os.makedirs(clip_dir, exist_ok=True)
    
    total_frames = 14
    for f in range(1, total_frames + 1):
        frame_name = f"Frame{f:02d}.png"
        create_frame_png(os.path.join(clip_dir, frame_name), behavior_id, behavior_name, f, total_frames)
        
    wav_path = os.path.join(clip_dir, "sound.wav")
    create_placeholder_wav(wav_path, duration_sec=duration)
    
    metadata = {
        "behavior_id": behavior_id,
        "behavior_name": behavior_name,
        "category": category,
        "fps": 14,
        "total_frames": total_frames,
        "duration_seconds": duration,
        "loop": is_loop,
        "priority": priority,
        "interruptible": True,
        "transition_in": f"CHR_TRANS_WAKE2IDLE_001" if category != "transitions" else None,
        "transition_out": f"CHR_TRANS_IDLE2TALK_001" if category != "transitions" else None,
        "blend_mode": "OVERLAY",
        "recommended_next_behaviors": ["CHR_IDLE_001"],
        "tags": tags or [category, behavior_name.lower()],
        "sound_file": "sound.wav"
    }
    
    with open(os.path.join(clip_dir, "behavior.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

print("Builder helper library ready.")
