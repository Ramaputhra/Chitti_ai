import os
import sys
import time

def run_benchmarks():
    print("========================================")
    print("  CHITTI BENCHMARK RUNNER")
    print("========================================\n")
    
    benchmarks = [
        ("Benchmark 001: Find File", "desktop.benchmarks.jobs.benchmark_001_find_file"),
        ("Benchmark 002: Organize Downloads", "desktop.benchmarks.jobs.benchmark_002_organize_downloads"),
        ("Benchmark 003: Empty Downloads", "desktop.benchmarks.jobs.benchmark_003_empty_downloads")
    ]
    
    passed_count = 0
    total = len(benchmarks)
    
    for name, module_path in benchmarks:
        print(f"Running {name}...")
        try:
            # We import and run the module dynamically so we can catch exceptions properly
            import importlib
            module = importlib.import_module(module_path)
            
            # Find the benchmark class
            benchmark_class = None
            for attr_name in dir(module):
                if attr_name.startswith("Benchmark") and "00" in attr_name:
                    benchmark_class = getattr(module, attr_name)
                    break
                    
            if not benchmark_class:
                print(f"  [FAIL] Could not find benchmark class in {module_path}")
                continue
                
            instance = benchmark_class()
            
            start_time = time.time()
            result_data = instance.execute()
            result = instance.assert_success(result_data)
            duration = (time.time() - start_time) * 1000
            
            if result.passed:
                print(f"  [PASS] {name} ({duration:.0f} ms)")
                passed_count += 1
            else:
                print(f"  [FAIL] {name}: {result.error_message}")
                
        except Exception as e:
            print(f"  [FAIL] {name}: Exception raised -> {e}")
            
    print("\n----------------")
    print(f"{passed_count} / {total} Passed")
    
    if passed_count < total:
        sys.exit(1)

if __name__ == "__main__":
    # Ensure the parent directory is in PYTHONPATH so imports work
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    run_benchmarks()
