import os
import glob

base_dir = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\architecture"
decisions_dir = os.path.join(base_dir, "decisions")

renames = {
    "APPLICATION_KERNEL_SPEC.md": "CORE_RUNTIME_SPEC.md",
    "APPLICATION_STARTUP.md": "RUNTIME_INITIALIZATION.md"
}

# 1. Rename files
for old_name, new_name in renames.items():
    old_path = os.path.join(base_dir, old_name)
    new_path = os.path.join(base_dir, new_name)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

# 2. Text Replacements
replacements = {
    "APPLICATION_KERNEL_SPEC.md": "CORE_RUNTIME_SPEC.md",
    "APPLICATION_STARTUP.md": "RUNTIME_INITIALIZATION.md",
    "Application Kernel Spec": "Core Runtime Spec",
    "Application Startup": "Runtime Initialization",
    "The master blueprint for the Application Architecture orchestration design.": "The master blueprint for CHITTI's Runtime-based AI Desktop Companion architecture."
}

golden_rule_5 = "> **5. Every runtime, planner, scheduler, and capability must exist only to improve the AI Desktop Companion experience. Architectural complexity must always provide measurable product value.**\n\n## 1. Purpose"

acceptance_criteria = """

## Acceptance Criteria

This specification is considered complete when:

- [ ] Interfaces are defined
- [ ] Events are defined
- [ ] Failure modes are defined
- [ ] Tests are identifiable
- [ ] Dependencies are documented
- [ ] Future extensions are documented
"""

all_files = glob.glob(os.path.join(base_dir, "*.md"))

for path in all_files:
    filename = os.path.basename(path)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    
    # Simple replacements
    for old_text, new_text in replacements.items():
        new_content = new_content.replace(old_text, new_text)
        
    # Apply Golden Rule #5 to specs (not index, not adrs)
    if filename != "ARCHITECTURE_INDEX.md" and filename != "V1_FROZEN_ARCHITECTURE.md":
        if "## 1. Purpose" in new_content and "> **5." not in new_content:
            new_content = new_content.replace("## 1. Purpose", golden_rule_5)
            
        if "## Acceptance Criteria" not in new_content:
            new_content += acceptance_criteria
        
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

# Process ADRs for text replacements only
adr_files = glob.glob(os.path.join(decisions_dir, "*.md"))
for path in adr_files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    for old_text, new_text in replacements.items():
        new_content = new_content.replace(old_text, new_text)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Final tweaks applied.")
