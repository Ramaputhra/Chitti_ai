import os
import glob
import re

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"

# 1. Rename APPLICATION_CORE_SPEC
old_core = os.path.join(base_dir, "CORE_RUNTIME_SPEC.md")
new_core = os.path.join(base_dir, "APPLICATION_CORE_SPEC.md")
if os.path.exists(old_core):
    os.rename(old_core, new_core)

# Update index and plan
for path in [
    os.path.join(base_dir, "ARCHITECTURE_INDEX.md"),
    r"C:\Users\Sm!le\.gemini\antigravity-ide\brain\46b77827-6d01-42fa-97f5-56f90eba1fac\implementation_plan.md"
]:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace("CORE_RUNTIME_SPEC.md", "APPLICATION_CORE_SPEC.md")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

# 2. Update CHITTI_ARCHITECTURE.md description explicitly
chitti_arch_path = os.path.join(base_dir, "CHITTI_ARCHITECTURE.md")
if os.path.exists(chitti_arch_path):
    with open(chitti_arch_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex replace the entire line under "## 1. Purpose"
    content = re.sub(r"## 1\. Purpose\n.*?\n", "## 1. Purpose\nThe master blueprint for CHITTI's Runtime-based AI Desktop Companion architecture.\n", content, count=1)
    
    with open(chitti_arch_path, 'w', encoding='utf-8') as f:
        f.write(content)


new_acceptance = """
## Acceptance Criteria

□ Purpose is defined
□ Responsibilities are complete
□ Interfaces are documented
□ Events are documented
□ Dependencies are identified
□ Failure modes are defined
□ Lifecycle is complete
□ Future extensions are identified
□ Out-of-scope boundaries are defined
□ Version 1 / Version 2 / Final Architecture comparison is complete
"""

# 3. Update Acceptance Criteria in all specs (strip old one if exists, add new one)
all_files = glob.glob(os.path.join(base_dir, "*.md"))
for path in all_files:
    filename = os.path.basename(path)
    if filename not in ["ARCHITECTURE_INDEX.md", "V1_FROZEN_ARCHITECTURE.md"]:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove old acceptance criteria
        content = content.split("## Acceptance Criteria")[0].strip()
        
        # Add new acceptance criteria
        content += "\n\n" + new_acceptance.strip() + "\n"
        
        # Ensure APPLICATION_CORE_SPEC internal references are updated
        content = content.replace("CORE_RUNTIME_SPEC.md", "APPLICATION_CORE_SPEC.md")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Applied final user review requirements.")
