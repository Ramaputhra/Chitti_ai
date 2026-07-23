import os
import sys
import json
import shutil
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
    
    draw.rectangle([10, 10, width - 10, height - 10], outline=(99, 102, 241, 255), width=3)
    
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((20, 30), f"ID: {behavior_id}", fill=(248, 250, 252, 255), font=font)
    draw.text((20, 60), f"Name: {behavior_name}", fill=(226, 232, 240, 255), font=font)
    draw.text((20, 90), f"Frame: {frame_num:02d} / {total_frames:02d}", fill=(56, 189, 248, 255), font=font)
    
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

def generate_all_assets():
    print("[1/5] Creating Source SVG Assets...")
    sources = [
        ("character/body", "body_base.svg", "BODY PLACEHOLDER"),
        ("character/body", "body_torso.svg", "TORSO PLACEHOLDER"),
        ("character/head", "head_base.svg", "HEAD PLACEHOLDER"),
        ("character/face/eyes", "eyes_open.svg", "EYES OPEN"),
        ("character/face/eyes", "eyes_blink.svg", "EYES BLINK"),
        ("character/face/eyebrows", "eyebrows_neutral.svg", "EYEBROWS NEUTRAL"),
        ("character/face/eyebrows", "eyebrows_raised.svg", "EYEBROWS RAISED"),
        ("character/face/nose", "nose.svg", "NOSE PLACEHOLDER"),
        ("character/face/ears", "ears.svg", "EARS PLACEHOLDER"),
        ("character/face/cheeks", "cheeks.svg", "CHEEKS PLACEHOLDER"),
        ("character/face/mouths", "mouth_neutral.svg", "MOUTH NEUTRAL"),
        ("character/face/mouths", "mouth_smile.svg", "MOUTH SMILE"),
        ("character/face/mouths", "mouth_speak.svg", "MOUTH SPEAK"),
        ("character/face/hair", "hair.svg", "HAIR PLACEHOLDER"),
        ("character/hands/left", "left_hand_open.svg", "LEFT HAND PLACEHOLDER"),
        ("character/hands/right", "right_hand_open.svg", "RIGHT HAND PLACEHOLDER"),
        ("character/hands/left", "left_hand_fist.svg", "LEFT HAND FIST"),
        ("character/hands/right", "right_hand_fist.svg", "RIGHT HAND FIST"),
        ("character/accessories", "glasses.svg", "GLASSES PLACEHOLDER"),
        ("character/accessories", "hat.svg", "HAT PLACEHOLDER"),
        ("character/accessories", "headset.svg", "HEADSET PLACEHOLDER"),
    ]
    props = [
        "laptop", "notebook", "magnifier", "printer", "keyboard", "mouse",
        "coffee", "folders", "files", "calendar", "clipboard", "phone",
        "camera", "map", "umbrella", "wrench", "usb", "cloud", "package"
    ]
    for p in props:
        sources.append((f"character/props", f"{p}.svg", f"{p.upper()} PLACEHOLDER"))
        
    for sub, fn, text in sources:
        create_placeholder_svg(os.path.join(SOURCE_ROOT, sub, fn), text)

    print("[2/5] Creating System & Domain Behavior Clips...")
    behaviors = [
        # System
        ("system", "boot", "CHR_BOOT_001", "Boot", False, "HIGH", 1.0),
        ("system", "wake", "CHR_WAKE_001", "Wake", False, "HIGH", 1.0),
        ("system", "slide_in_left", "CHR_TRANS_SLIDE_IN_L_001", "SlideInLeft", False, "NORMAL", 0.8),
        ("system", "slide_in_right", "CHR_TRANS_SLIDE_IN_R_001", "SlideInRight", False, "NORMAL", 0.8),
        ("system", "slide_out_left", "CHR_TRANS_SLIDE_OUT_L_001", "SlideOutLeft", False, "NORMAL", 0.8),
        ("system", "slide_out_right", "CHR_TRANS_SLIDE_OUT_R_001", "SlideOutRight", False, "NORMAL", 0.8),
        ("system", "greeting_morning", "CHR_GREET_MORNING_001", "GreetingMorning", False, "NORMAL", 1.0),
        ("system", "greeting_afternoon", "CHR_GREET_AFTERNOON_001", "GreetingAfternoon", False, "NORMAL", 1.0),
        ("system", "greeting_evening", "CHR_GREET_EVENING_001", "GreetingEvening", False, "NORMAL", 1.0),
        ("system", "welcome_back", "CHR_GREET_WELCOME_001", "WelcomeBack", False, "NORMAL", 1.0),
        ("system", "goodbye", "CHR_GOODBYE_001", "Goodbye", False, "NORMAL", 1.0),
        ("system", "idle", "CHR_IDLE_001", "Idle", True, "LOW", 2.0),
        ("system", "idle_blink", "CHR_IDLE_BLINK_001", "IdleBlink", False, "LOW", 0.5),
        ("system", "idle_breathing", "CHR_IDLE_BREATH_001", "IdleBreathing", True, "LOW", 2.0),
        ("system", "idle_look_around", "CHR_IDLE_LOOK_001", "IdleLookAround", False, "LOW", 1.5),
        ("system", "stretch", "CHR_IDLE_STRETCH_001", "Stretch", False, "LOW", 1.5),
        ("system", "sleepy", "CHR_SLEEP_001", "Sleepy", True, "LOW", 2.0),
        ("system", "yawn", "CHR_SLEEP_YAWN_001", "Yawn", False, "LOW", 1.5),
        ("system", "become_edge_dot", "CHR_MODE_DOT_001", "BecomeEdgeDot", False, "HIGH", 1.0),
        ("system", "restore_from_dot", "CHR_MODE_RESTORE_001", "RestoreFromDot", False, "HIGH", 1.0),

        # Listening
        ("listening", "listening", "CHR_LISTEN_001", "Listening", True, "HIGH", 1.0),
        ("listening", "listening_focused", "CHR_LISTEN_FOCUSED_001", "ListeningFocused", True, "HIGH", 1.0),
        ("listening", "listening_curious", "CHR_LISTEN_CURIOUS_001", "ListeningCurious", True, "HIGH", 1.0),
        ("listening", "waiting", "CHR_LISTEN_WAITING_001", "Waiting", True, "NORMAL", 1.5),
        ("listening", "interrupt_listening", "CHR_LISTEN_INTERRUPT_001", "InterruptListening", False, "HIGH", 0.5),

        # Thinking
        ("thinking", "thinking", "CHR_THINK_001", "Thinking", True, "HIGH", 1.0),
        ("thinking", "thinking_deep", "CHR_THINK_DEEP_001", "ThinkingDeep", True, "HIGH", 1.5),
        ("thinking", "searching_memory", "CHR_SEARCH_MEM_001", "SearchingMemory", True, "NORMAL", 1.2),
        ("thinking", "searching_internet", "CHR_SEARCH_NET_001", "SearchingInternet", True, "NORMAL", 1.2),
        ("thinking", "reading", "CHR_READ_001", "Reading", True, "NORMAL", 1.5),
        ("thinking", "calculating", "CHR_CALC_001", "Calculating", True, "NORMAL", 1.2),
        ("thinking", "analyzing", "CHR_ANALYZE_001", "Analyzing", True, "NORMAL", 1.2),
        ("thinking", "confused", "CHR_CONFUSED_001", "Confused", False, "HIGH", 1.0),

        # Speaking
        ("speaking", "talking_neutral", "CHR_TALK_NEUTRAL_001", "TalkingNeutral", True, "HIGH", 1.0),
        ("speaking", "talking_happy", "CHR_TALK_HAPPY_001", "TalkingHappy", True, "HIGH", 1.0),
        ("speaking", "talking_professional", "CHR_TALK_PRO_001", "TalkingProfessional", True, "HIGH", 1.0),
        ("speaking", "talking_explain", "CHR_TALK_EXPLAIN_001", "TalkingExplain", True, "HIGH", 1.2),
        ("speaking", "talking_story", "CHR_TALK_STORY_001", "TalkingStory", True, "HIGH", 1.2),
        ("speaking", "talking_question", "CHR_TALK_QUESTION_001", "TalkingQuestion", True, "HIGH", 1.0),
        ("speaking", "talking_reminder", "CHR_TALK_REMINDER_001", "TalkingReminder", True, "HIGH", 1.0),
        ("speaking", "talking_presentation", "CHR_TALK_PRES_001", "TalkingPresentation", True, "HIGH", 1.2),
        ("speaking", "talking_navigation", "CHR_TALK_NAV_001", "TalkingNavigation", True, "HIGH", 1.0),
        ("speaking", "talking_browser", "CHR_TALK_BROWSER_001", "TalkingBrowser", True, "HIGH", 1.0),
        ("speaking", "talking_vision", "CHR_TALK_VISION_001", "TalkingVision", True, "HIGH", 1.0),
        ("speaking", "talking_productivity", "CHR_TALK_PROD_001", "TalkingProductivity", True, "HIGH", 1.0),
        ("speaking", "talking_warning", "CHR_TALK_WARN_001", "TalkingWarning", True, "HIGH", 1.0),

        # Working
        ("working", "typing_laptop", "CHR_WORK_TYPING_001", "TypingLaptop", True, "NORMAL", 1.2),
        ("working", "writing_notes", "CHR_WORK_NOTES_001", "WritingNotes", True, "NORMAL", 1.2),
        ("working", "searching_files", "CHR_WORK_SEARCH_FILES_001", "SearchingFiles", True, "NORMAL", 1.2),
        ("working", "searching_folders", "CHR_WORK_SEARCH_FOLDERS_001", "SearchingFolders", True, "NORMAL", 1.2),
        ("working", "organizing_files", "CHR_WORK_ORG_FILES_001", "OrganizingFiles", True, "NORMAL", 1.2),
        ("working", "copying_files", "CHR_WORK_COPY_FILES_001", "CopyingFiles", True, "NORMAL", 1.0),
        ("working", "moving_files", "CHR_WORK_MOVE_FILES_001", "MovingFiles", True, "NORMAL", 1.0),
        ("working", "deleting_files", "CHR_WORK_DEL_FILES_001", "DeletingFiles", False, "NORMAL", 1.0),
        ("working", "printing", "CHR_WORK_PRINT_001", "Printing", True, "NORMAL", 1.2),
        ("working", "watching_printer", "CHR_WORK_WATCH_PRINT_001", "WatchingPrinter", True, "NORMAL", 1.2),
        ("working", "scanning", "CHR_WORK_SCAN_001", "Scanning", True, "NORMAL", 1.2),
        ("working", "uploading", "CHR_WORK_UPLOAD_001", "Uploading", True, "NORMAL", 1.0),
        ("working", "downloading", "CHR_WORK_DOWNLOAD_001", "Downloading", True, "NORMAL", 1.0),
        ("working", "installing", "CHR_WORK_INSTALL_001", "Installing", True, "NORMAL", 1.2),
        ("working", "compiling", "CHR_WORK_COMPILE_001", "Compiling", True, "NORMAL", 1.5),
        ("working", "coding", "CHR_WORK_CODING_001", "Coding", True, "NORMAL", 1.5),

        # Presentation Gestures
        ("presentation_gestures", "point_left", "CHR_GEST_POINT_L_001", "PointLeft", False, "NORMAL", 0.8),
        ("presentation_gestures", "point_right", "CHR_GEST_POINT_R_001", "PointRight", False, "NORMAL", 0.8),
        ("presentation_gestures", "point_screen", "CHR_GEST_POINT_SCR_001", "PointScreen", False, "NORMAL", 0.8),
        ("presentation_gestures", "point_timeline", "CHR_GEST_POINT_TL_001", "PointTimeline", False, "NORMAL", 0.8),
        ("presentation_gestures", "point_chart", "CHR_GEST_POINT_CHART_001", "PointChart", False, "NORMAL", 0.8),
        ("presentation_gestures", "present_dashboard", "CHR_GEST_PRES_DASH_001", "PresentDashboard", False, "NORMAL", 1.0),
        ("presentation_gestures", "present_map", "CHR_GEST_PRES_MAP_001", "PresentMap", False, "NORMAL", 1.0),
        ("presentation_gestures", "present_image", "CHR_GEST_PRES_IMG_001", "PresentImage", False, "NORMAL", 1.0),

        # Vision
        ("vision", "inspect_image", "CHR_VIS_INSPECT_001", "InspectImage", False, "NORMAL", 1.0),
        ("vision", "zoom_image", "CHR_VIS_ZOOM_001", "ZoomImage", False, "NORMAL", 1.0),
        ("vision", "ocr_reading", "CHR_VIS_OCR_001", "OCRReading", True, "NORMAL", 1.2),
        ("vision", "face_detection", "CHR_VIS_FACE_001", "FaceDetection", False, "NORMAL", 1.0),
        ("vision", "object_detection", "CHR_VIS_OBJ_001", "ObjectDetection", False, "NORMAL", 1.0),

        # Navigation
        ("navigation", "walk", "CHR_NAV_WALK_001", "Walk", True, "NORMAL", 1.0),
        ("navigation", "compass", "CHR_NAV_COMPASS_001", "Compass", False, "NORMAL", 1.0),
        ("navigation", "show_route", "CHR_NAV_ROUTE_001", "ShowRoute", False, "NORMAL", 1.0),
        ("navigation", "destination_reached", "CHR_NAV_DEST_001", "DestinationReached", False, "HIGH", 1.0),

        # Reminders
        ("reminders", "write_reminder", "CHR_REM_WRITE_001", "WriteReminder", False, "NORMAL", 1.0),
        ("reminders", "pin_reminder", "CHR_REM_PIN_001", "PinReminder", False, "NORMAL", 0.8),
        ("reminders", "calendar_reminder", "CHR_REM_CAL_001", "CalendarReminder", False, "NORMAL", 1.0),
        ("reminders", "alarm_set", "CHR_REM_ALARM_001", "AlarmSet", False, "NORMAL", 1.0),

        # Success
        ("success", "thumbs_up", "CHR_SUCC_THUMBSUP_001", "ThumbsUp", False, "HIGH", 1.0),
        ("success", "celebrate", "CHR_SUCC_CELEBRATE_001", "Celebrate", False, "HIGH", 1.5),
        ("success", "happy_jump", "CHR_SUCC_JUMP_001", "HappyJump", False, "HIGH", 1.0),
        ("success", "smile", "CHR_SUCC_SMILE_001", "Smile", False, "NORMAL", 1.0),
        ("success", "satisfied", "CHR_SUCC_SATISFIED_001", "Satisfied", False, "NORMAL", 1.0),

        # Warning
        ("warning", "warning", "CHR_WARN_001", "Warning", False, "HIGH", 1.0),
        ("warning", "oops", "CHR_WARN_OOPS_001", "Oops", False, "HIGH", 0.8),
        ("warning", "retry", "CHR_WARN_RETRY_001", "Retry", False, "HIGH", 1.0),
        ("warning", "concern", "CHR_WARN_CONCERN_001", "Concern", False, "HIGH", 1.0),
        ("warning", "error", "CHR_WARN_ERR_001", "Error", False, "HIGH", 1.2),

        # Transitions
        ("transitions", "idle_to_talk", "CHR_TRANS_IDLE2TALK_001", "IdleToTalk", False, "NORMAL", 0.5),
        ("transitions", "talk_to_idle", "CHR_TRANS_TALK2IDLE_001", "TalkToIdle", False, "NORMAL", 0.5),
        ("transitions", "idle_to_thinking", "CHR_TRANS_IDLE2THINK_001", "IdleToThinking", False, "NORMAL", 0.5),
        ("transitions", "thinking_to_talk", "CHR_TRANS_THINK2TALK_001", "ThinkingToTalk", False, "NORMAL", 0.5),
        ("transitions", "working_to_talk", "CHR_TRANS_WORK2TALK_001", "WorkingToTalk", False, "NORMAL", 0.5),
        ("transitions", "listening_to_talk", "CHR_TRANS_LISTEN2TALK_001", "ListeningToTalk", False, "NORMAL", 0.5),
        ("transitions", "success_to_idle", "CHR_TRANS_SUCC2IDLE_001", "SuccessToIdle", False, "NORMAL", 0.5),
        ("transitions", "sleep_to_wake", "CHR_TRANS_SLEEP2WAKE_001", "SleepToWake", False, "NORMAL", 0.5),
        ("transitions", "wake_to_idle", "CHR_TRANS_WAKE2IDLE_001", "WakeToIdle", False, "NORMAL", 0.5),
    ]

    for cat, dir_n, b_id, b_name, loop, prio, dur in behaviors:
        create_behavior_clip(cat, dir_n, b_id, b_name, is_loop=loop, priority=prio, duration=dur)

    print("[3/5] Creating Runtime Prop Assets & Sound Placeholders...")
    for p in props:
        prop_dir = os.path.join(RUNTIME_ROOT, "props", p)
        os.makedirs(prop_dir, exist_ok=True)
        create_frame_png(os.path.join(prop_dir, "prop_preview.png"), f"PROP_{p.upper()}", p.capitalize(), 1, 1)
        with open(os.path.join(prop_dir, "prop.json"), "w") as f:
            json.dump({"prop_id": f"PROP_{p.upper()}", "prop_name": p, "format": "png"}, f, indent=2)

    sound_placeholders = ["boot.wav", "click.wav", "alert.wav", "success.wav", "error.wav"]
    for s in sound_placeholders:
        create_placeholder_wav(os.path.join(RUNTIME_ROOT, "sounds", s), duration_sec=0.3)

    print("[4/5] Legacy Repository Audit & Cleanup...")
    legacy_folders = [
        os.path.join(v3_root, "Expressions"),
        os.path.join(v3_root, "desktop", "assets", "avatar")
    ]
    for lf in legacy_folders:
        if os.path.exists(lf):
            shutil.rmtree(lf, ignore_errors=True)
            print(f"✅ Removed legacy directory: {lf}")
            
    legacy_file = os.path.join(v3_root, "Character sheet.png")
    if os.path.exists(legacy_file):
        os.remove(legacy_file)
        print(f"✅ Removed legacy file: {legacy_file}")

    print("[5/5] Setup Complete.")

if __name__ == "__main__":
    generate_all_assets()
