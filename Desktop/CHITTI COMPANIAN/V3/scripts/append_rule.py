import os

rule_264 = \"\"\"
## Rule 264 – Runtime Stability
Certified runtimes are considered stable platform components. New product features must not expand their responsibilities. Additional functionality should be implemented through capabilities, providers, experiences, skills, or plugins unless the runtime's core contract itself requires revision.
\"\"\"

path = r"c:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\.agents\AGENTS.md"
with open(path, "a", encoding="utf-8") as f:
    f.write(rule_264)
print("Rule appended successfully.")
