import os
import json

base_path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\Expressions"

states = [
    ("Offline", {"id": "offline", "fps": 24, "loop": False}),
    ("Starting", {"id": "starting", "fps": 24, "loop": True}),
    ("Error", {"id": "error", "fps": 24, "loop": True}),
    ("Listening", {"id": "listening", "fps": 24, "loop": True}),
    ("Talking", {"id": "talking", "fps": 24, "loop": True}),
    ("Failure", {"id": "failure", "fps": 24, "loop": False}),
    ("Understanding", {"id": "understanding", "fps": 24, "loop": True}),
    ("Thinking", {"id": "thinking", "fps": 24, "loop": True}),
    ("Working", {"id": "working", "fps": 24, "loop": True}),
    ("Reading", {"id": "reading", "fps": 24, "loop": True}),
    ("Writing", {"id": "writing", "fps": 24, "loop": True}),
    ("Success", {"id": "success", "fps": 24, "loop": False}),
    ("Monitoring", {"id": "monitoring", "fps": 24, "loop": True}),
    ("Ready", {"id": "ready", "fps": 24, "loop": True}),
    ("Idle", {"id": "idle", "fps": 24, "loop": True}),
    ("Waiting", {"id": "waiting", "fps": 24, "loop": True}),
    ("Exercising", {"id": "exercising", "fps": 24, "loop": True}),
    ("Sleeping", {"id": "sleeping", "fps": 24, "loop": True}),
    ("Goodbye", {"id": "goodbye", "fps": 24, "loop": False}),
]

if not os.path.exists(base_path):
    os.makedirs(base_path)

for name, manifest in states:
    folder = os.path.join(base_path, name)
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # Write manifest
    manifest_path = os.path.join(folder, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)
        
    # Write a dummy png to ensure folder isn't empty, if it's completely empty
    dummy_png = os.path.join(folder, "placeholder.png")
    if len(os.listdir(folder)) == 1: # Only manifest exists
        # Create a tiny 1x1 black png
        with open(dummy_png, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

print("Created all mock folders successfully.")
