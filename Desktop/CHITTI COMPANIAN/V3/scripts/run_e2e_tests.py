import sys
import os
import asyncio
import time
from importlib import util

# Setup path so we can import desktop and scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def main():
    print("="*60)
    print("🚀 CHITTI COMPANION: COMPREHENSIVE E2E PLATFORM TESTER")
    print("="*60)
    
    suites_dir = os.path.join(os.path.dirname(__file__), "e2e_suites")
    if not os.path.exists(suites_dir):
        print(f"❌ Could not find suites directory: {suites_dir}")
        sys.exit(1)
        
    test_files = [f for f in os.listdir(suites_dir) if f.startswith("test_") and f.endswith(".py")]
    
    total = len(test_files)
    passed = 0
    failed = 0
    
    results = []
    
    for test_file in test_files:
        test_name = test_file.replace(".py", "")
        module_name = f"scripts.e2e_suites.{test_name}"
        
        # Load module dynamically
        spec = util.spec_from_file_location(module_name, os.path.join(suites_dir, test_file))
        module = util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if hasattr(module, "run_test"):
            print(f"\n▶️ Running {test_name}...")
            t_start = time.time()
            try:
                success, msg = await module.run_test()
            except Exception as e:
                success, msg = False, f"Unhandled exception: {e}"
                
            elapsed = time.time() - t_start
            
            if success:
                print(f"   ✅ PASSED ({elapsed:.2f}s)")
                passed += 1
                results.append((test_name, "PASSED", msg))
            else:
                print(f"   ❌ FAILED ({elapsed:.2f}s) - {msg}")
                failed += 1
                results.append((test_name, "FAILED", msg))
        else:
            print(f"⚠️ Skipping {test_name}: no run_test() coroutine found.")
            
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, status, msg in results:
        icon = "✅" if status == "PASSED" else "❌"
        print(f"{icon} {test_name.ljust(20)} | {status.ljust(6)} | {msg}")
        
    print("-" * 60)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)
    
    if failed > 0:
        print("\n❌ NOT ALL TESTS RAN SUCCESSFULLY.")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS RAN SUCCESSFULLY.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
