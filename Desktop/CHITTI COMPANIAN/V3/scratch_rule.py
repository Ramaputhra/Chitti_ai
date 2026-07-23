import os

agents_md_path = r"C:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\.agents\AGENTS.md"

rule = """

## Rule 999 — Sprint E.2 Freeze Rule
No new features may be added until every command in the Dogfood Matrix passes end-to-end through the real production pipeline.
"""

with open(agents_md_path, "a", encoding="utf-8") as f:
    f.write(rule)
    
print("Successfully appended Sprint E.2 Freeze Rule.")
