"""
CHITTI V2 — ROOT ENTRY POINT
=============================================================================
CLASSIFICATION : ARCHITECTURAL BOOTSTRAP STUB (Non-Production)
RSM-1 CID-002  : This file is intentionally a prototype that demonstrates
                 the BootstrapManager contract only. It is NOT the production
                 launch point and MUST NOT be used to run CHITTI.

PRODUCTION ENTRY: desktop/app/main.py
  Run: python desktop/app/main.py
  With LLM: python desktop/app/main.py --use-llm

This file wires only ObservabilityManager (real) + MockInstance_* for all
other services. The main loop body is empty (try: pass) by design. The file
remains here as the architectural prototype for the BootstrapManager pattern.
=============================================================================
"""
import sys
from desktop.bootstrap.manager import BootstrapManager, BootstrapManifest


def main():
    manifest = BootstrapManifest(
        required_services=["SQLiteConnection", "CognitivePipeline", "InteractionSession"],
        optional_services=["DiscordWebhook"],
        failure_policy="HARD_CRASH"
    )
    
    bootstrap = BootstrapManager(manifest)
    bootstrap.boot()
    
    try:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        bootstrap.shutdown()

if __name__ == "__main__":
    main()
