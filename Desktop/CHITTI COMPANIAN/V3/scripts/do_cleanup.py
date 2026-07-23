import os
import shutil
import glob

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V2"

# 1. Delete generated
to_delete = [
    ".venv", "chitti_companion.egg-info", "logs", "scratch", "sessions", "V2.zip", r"desktop\desktop.7z"
]
for d in to_delete:
    path = os.path.join(base_dir, d)
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except:
                pass

for p in glob.glob(os.path.join(base_dir, "**", "__pycache__"), recursive=True):
    shutil.rmtree(p, ignore_errors=True)

# 2. Archive
os.makedirs(os.path.join(base_dir, "archive", "docs"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "archive", "capabilities"), exist_ok=True)
os.makedirs(os.path.join(base_dir, "archive", ".agents", "skills"), exist_ok=True)

def move_safe(src, dst):
    if os.path.exists(src):
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Failed to move {src} to {dst}: {e}")

move_safe(os.path.join(base_dir, "CHITTI_PROJECT_ARCHITECTURE"), os.path.join(base_dir, "archive", "CHITTI_PROJECT_ARCHITECTURE"))
move_safe(os.path.join(base_dir, "desktop", "capabilities", "robotics"), os.path.join(base_dir, "archive", "capabilities", "robotics"))
move_safe(os.path.join(base_dir, "desktop", "services", "remote"), os.path.join(base_dir, "archive", "remote"))

keep_agents = {"ai_lead", "desktop_lead", "ui_ux_engineer", "qa_engineer", "system_architect", "project_director"}
agents_dir = os.path.join(base_dir, ".agents", "skills")
if os.path.exists(agents_dir):
    for agent in os.listdir(agents_dir):
        if agent not in keep_agents and os.path.isdir(os.path.join(agents_dir, agent)):
            move_safe(os.path.join(agents_dir, agent), os.path.join(base_dir, "archive", ".agents", "skills", agent))

print("Cleanup complete.")
