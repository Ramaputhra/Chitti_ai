import os

agents_md_path = r"C:\Users\Sm!le\Desktop\CHITTI COMPANIAN\V3\.agents\AGENTS.md"

rule_text = """
## Rule 243 — Product Experience First

New infrastructure, runtimes, frameworks, abstractions, or platform layers may only be introduced when required by at least three independent product features or when they eliminate a demonstrable architectural limitation. Otherwise, product development shall extend the existing frozen platform through composition.
"""

with open(agents_md_path, "a", encoding="utf-8") as f:
    f.write("\n" + rule_text)

print("Rule 243 appended successfully.")
