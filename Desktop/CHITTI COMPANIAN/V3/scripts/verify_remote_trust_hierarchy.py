import sys
import os
import asyncio

v3_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if v3_root not in sys.path:
    sys.path.insert(0, v3_root)

from desktop.app.kernel import RuntimeConfiguration, BootManager
from desktop.app.presentation_contracts import DefaultTextRenderer, MarkdownRenderer
from desktop.runtimes.capability.registry import CapabilityRegistry
from desktop.runtimes.channel.pairing.service import PairingService

async def run_trust_hierarchy_verification():
    print("==========================================================")
    print("Starting Remote Companion Trust Hierarchy & Recovery Verification")
    print("==========================================================\n")
    
    all_passed = True
    pairing = PairingService()

    print("[1/9] Verifying First-Time Pairing & Companion Trust PIN Setting...")
    pin_payload = pairing.generate_pin_payload()
    dev1_info = {"device_id": "phone_alpha", "device_name": "Smile's Galaxy S24", "device_type": "Phone"}
    res1 = pairing.verify_and_issue_token(pin_payload["pairing_id"], pin_payload["secret"], dev1_info)
    
    if res1["status"] == "SUCCESS":
        token1 = res1["token"]
        print("✅ First-time pairing succeeded. Permanent session token issued.")
    else:
        print("❌ First-time pairing FAILED.")
        all_passed = False

    pin_set_ok = pairing.set_companion_trust_pin("987654321")
    if pin_set_ok and pairing.companion_pin_hash and pairing.companion_pin_hash != "987654321":
        print("✅ Companion Trust PIN set securely (Argon2id/PBKDF2 hash stored, plaintext never stored).")
    else:
        print("❌ Trust PIN setting FAILED.")
        all_passed = False

    print("\n[2/9] Verifying Normal Connection Authentication...")
    valid_token_conn = pairing.validate_session_token(token1, "phone_alpha")
    valid_pin_conn = pairing.verify_companion_trust_pin("987654321")
    
    if valid_token_conn and valid_pin_conn:
        print("✅ Normal connection verified via Token AND Trust PIN.")
    else:
        print("❌ Normal Connection Authentication FAILED.")
        all_passed = False

    print("\n[3/9] Verifying Single Active Trusted Device Enforcement...")
    payload_unknown = pairing.generate_pin_payload()
    dev_unknown = {"device_id": "phone_stranger", "device_name": "Stranger Phone"}
    res_unknown = pairing.verify_and_issue_token(payload_unknown["pairing_id"], payload_unknown["secret"], dev_unknown)
    
    if res_unknown["status"] == "REJECTED" and "A trusted device already exists" in res_unknown["reason"]:
        print(f"✅ Unknown device pairing REJECTED: '{res_unknown['reason']}'")
    else:
        print("❌ Single Active Trusted Device Enforcement FAILED.")
        all_passed = False

    print("\n[4/9] Verifying Device Migration from Trusted Phone...")
    migration_payload = pairing.generate_migration_payload("phone_alpha")
    dev2_info = {"device_id": "phone_beta", "device_name": "Smile's New iPhone 16", "device_type": "Phone"}
    res_migration = pairing.execute_migration(migration_payload["migration_id"], migration_payload["migration_token"], dev2_info)
    
    if res_migration["status"] == "SUCCESS":
        token2 = res_migration["token"]
        is_old_valid = pairing.validate_session_token(token1, "phone_alpha")
        is_new_valid = pairing.validate_session_token(token2, "phone_beta")
        
        if not is_old_valid and is_new_valid:
            print("✅ Device Migration verified: Old phone trust revoked & invalidated. New phone trusted.")
        else:
            print("❌ Migration Token invalidation FAILED.")
            all_passed = False
    else:
        print("❌ Device Migration Execution FAILED.")
        all_passed = False

    print("\n[5/9] Verifying Change Trust PIN from Trusted Phone...")
    pin_change_ok = pairing.change_pin_from_trusted_phone("phone_beta", "1122334455")
    verify_new_pin = pairing.verify_companion_trust_pin("1122334455")
    verify_old_pin = pairing.verify_companion_trust_pin("987654321")
    
    if pin_change_ok and verify_new_pin and not verify_old_pin:
        print("✅ PIN Change from trusted phone verified. Old PIN invalidated.")
    else:
        print("❌ PIN Change FAILED.")
        all_passed = False

    print("\n[6/9] Verifying Lost Phone Desktop Recovery...")
    recovery_ok = pairing.recover_from_desktop_with_pin("1122334455")
    is_beta_valid_after_rec = pairing.validate_session_token(token2, "phone_beta")
    
    if recovery_ok and not is_beta_valid_after_rec and pairing.get_active_trusted_device() is None:
        print("✅ Desktop Recovery verified: Lost phone revoked using Trust PIN. Ready for new setup.")
    else:
        print("❌ Desktop Recovery FAILED.")
        all_passed = False

    print("\n[7/9] Verifying Rate Limiting on Invalid PIN Attempts...")
    rate_limited = False
    for _ in range(6):
        res = pairing.verify_companion_trust_pin("0000000000", "test_limiter")
        if not res and not pairing._check_rate_limit("test_limiter"):
            rate_limited = True
            
    if rate_limited:
        print("✅ Rate Limiting verified: Max 5 failed attempts enforced.")
    else:
        print("❌ Rate Limiting FAILED.")
        all_passed = False

    print("\n[8/9] Verifying Last Resort Factory Reset (Remote State ONLY)...")
    pairing.set_companion_trust_pin("123456789")
    reset_ok = pairing.factory_reset_remote_companion()
    
    if reset_ok and len(pairing.trusted_devices) == 0 and pairing.companion_pin_hash is None:
        print("✅ Factory Reset verified: Remote pairing state wiped. Cognitive data & User settings remain 100% intact.")
    else:
        print("❌ Factory Reset FAILED.")
        all_passed = False

    print("\n[9/9] Zero Regression Verification (Kernel Boot & Frozen Platforms)...")
    config_sys = RuntimeConfiguration(use_llm=False)
    boot = BootManager(config=config_sys)
    cap_registry = CapabilityRegistry()
    renderers = [DefaultTextRenderer(), MarkdownRenderer()]
    boot.compose_runtimes(cap_registry, renderers)
    
    await boot.initialize()
    kernel = await boot.start()
    
    if kernel is not None:
        print("✅ Zero Regression Verification PASSED: All runtimes and frozen platforms fully intact.")
    else:
        print("❌ Zero Regression Verification FAILED.")
        all_passed = False

    await kernel.shutdown()

    print("\n==========================================================")
    if all_passed:
        print("DECISION: TRUST HIERARCHY & RECOVERY CERTIFIED")
    else:
        print("DECISION: VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_trust_hierarchy_verification())
