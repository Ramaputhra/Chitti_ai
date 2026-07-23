import os
import glob

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"
decisions_dir = os.path.join(base_dir, "decisions")

renames = {
    "BOOT_SEQUENCE.md": "APPLICATION_STARTUP.md",
    "THREADING_MODEL.md": "CONCURRENCY_MODEL.md",
    "CHITTI_OS_ARCHITECTURE.md": "CHITTI_ARCHITECTURE.md",
    "KERNEL_SPEC.md": "APPLICATION_KERNEL_SPEC.md"
}

# 1. Rename files
for old_name, new_name in renames.items():
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

# 2. Text Replacements
replacements = {
    "CHITTI OS": "CHITTI Runtime",
    "OS Architecture": "Application Architecture",
    "Operating Environment": "Desktop Companion Runtime",
    "BOOT_SEQUENCE.md": "APPLICATION_STARTUP.md",
    "THREADING_MODEL.md": "CONCURRENCY_MODEL.md",
    "CHITTI_OS_ARCHITECTURE.md": "CHITTI_ARCHITECTURE.md",
    "KERNEL_SPEC.md": "APPLICATION_KERNEL_SPEC.md",
    "Boot Sequence": "Application Startup",
    "Threading Model": "Concurrency Model",
    "Kernel Spec": "Application Kernel Spec",
    "OS Kernel": "Application Kernel",
    "operating system": "companion application"
}

all_files = glob.glob(os.path.join(base_dir, "*.md")) + glob.glob(os.path.join(decisions_dir, "*.md"))

for path in all_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old_text, new_text in replacements.items():
        new_content = new_content.replace(old_text, new_text)
        
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Fix Implementation Plan artifact if we can touch it here
plan_path = r"C:\Users\Sm!le\.gemini\antigravity-ide\brain\46b77827-6d01-42fa-97f5-56f90eba1fac\implementation_plan.md"
if os.path.exists(plan_path):
    with open(plan_path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    new_content = new_content.replace("Phase 0: Architecture Freeze & OS Constitution", "Phase 0: Architecture Freeze & Runtime Constitution")
    for old_text, new_text in replacements.items():
        new_content = new_content.replace(old_text, new_text)
    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Renaming and text replacement complete.")
