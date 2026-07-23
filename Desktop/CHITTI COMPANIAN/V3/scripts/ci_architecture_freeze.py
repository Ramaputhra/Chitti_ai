import os
import sys
import subprocess

FROZEN_DIRS = [
    "desktop/core/kernel/",
    "desktop/core/lifecycle/",
    "desktop/runtimes/",
    "desktop/services/tasks/scheduler.py"
]

def check_architecture_freeze(base_ref="main"):
    print(f"Checking architecture freeze against '{base_ref}'...")
    try:
        # Check both committed changes against base branch and uncommitted changes
        cmd_diff = ["git", "diff", "--name-only", base_ref]
        result = subprocess.run(cmd_diff, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Could not run git diff against {base_ref}. Are you in a git repo?")
            return
            
        changed_files = result.stdout.strip().split('\n')
        
        cmd_uncommitted = ["git", "diff", "--name-only", "HEAD"]
        res_uncommitted = subprocess.run(cmd_uncommitted, capture_output=True, text=True)
        if res_uncommitted.returncode == 0 and res_uncommitted.stdout:
            changed_files.extend(res_uncommitted.stdout.strip().split('\n'))

        cmd_untracked = ["git", "ls-files", "--others", "--exclude-standard"]
        res_untracked = subprocess.run(cmd_untracked, capture_output=True, text=True)
        if res_untracked.returncode == 0 and res_untracked.stdout:
            changed_files.extend(res_untracked.stdout.strip().split('\n'))

        # Clean empty strings
        changed_files = [f.replace("\\", "/") for f in changed_files if f]
        
        violations = []
        for file in set(changed_files):
            for frozen_dir in FROZEN_DIRS:
                if file.startswith(frozen_dir):
                    violations.append(file)
                    break
        
        if violations:
            print("\n❌ ARCHITECTURE FREEZE VIOLATION DETECTED ❌")
            print("The following frozen platform components were modified:")
            for v in sorted(violations):
                print(f"  - {v}")
            print("\nPlease revert these changes or seek architectural exception approval.")
            sys.exit(1)
            
        # Check for new runtime directories
        runtimes_dir = "desktop/runtimes"
        if os.path.exists(runtimes_dir):
            current_runtimes = [d for d in os.listdir(runtimes_dir) if os.path.isdir(os.path.join(runtimes_dir, d))]
            # We hardcode the allowed runtimes for the freeze check
            allowed_runtimes = {"activity", "browser", "capability", "expression", "inference", "memory", "perception", "presence"}
            new_runtimes = [r for r in current_runtimes if r not in allowed_runtimes and r != "__pycache__"]
            if new_runtimes:
                print("\n❌ ARCHITECTURE FREEZE VIOLATION DETECTED ❌")
                print("New runtime directories were introduced:")
                for r in new_runtimes:
                    print(f"  - desktop/runtimes/{r}")
                print("\nPlatform v3.0 prohibits new top-level runtimes.")
                sys.exit(1)
                
        # Check for modified constitutional rules
        for file in set(changed_files):
            if file == ".agents/AGENTS.md" or file == ".agents/rules.md":
                print("\n❌ ARCHITECTURE FREEZE VIOLATION DETECTED ❌")
                print(f"Constitutional rules modified without review: {file}")
                sys.exit(1)
                
        # Check for modified public interfaces
        interfaces_dir = "desktop/core/interfaces/"
        interface_violations = [f for f in set(changed_files) if f.startswith(interfaces_dir)]
        if interface_violations:
            print("\n❌ ARCHITECTURE FREEZE VIOLATION DETECTED ❌")
            print("Public interfaces were modified:")
            for v in sorted(interface_violations):
                print(f"  - {v}")
            sys.exit(1)
            
        print("✅ Architecture Freeze verified: No core components, interfaces, or rules were modified, and no new runtimes were introduced.")
        sys.exit(0)
        
    except FileNotFoundError:
        print("Warning: git not found. Skipping freeze check.")
        sys.exit(0)

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    check_architecture_freeze(base)
