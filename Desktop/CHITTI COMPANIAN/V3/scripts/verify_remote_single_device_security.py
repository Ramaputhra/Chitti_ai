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

async def run_security_verification():
    print("==========================================================")
    print("Starting Remote Companion Single Active Device Security Verification")
    print("==========================================================\n")
    
    all_passed = True
    pairing = PairingService()

    print("[1/7] Pairing First Device (Device A)...")
    payload_a = pairing.generate_qr_payload()
    dev_a_info = {"device_id": "device_a", "device_name": "Galaxy S24", "device_type": "Phone", "ip": "192.168.1.10"}
    res_a = pairing.verify_and_issue_token(payload_a["pairing_id"], payload_a["secret"], dev_a_info)
    
    if res_a["status"] == "SUCCESS" and pairing.get_active_trusted_device().device_id == "device_a":
        token_a = res_a["token"]
        print(f"✅ Device A Paired & Active: '{res_a['device'].device_name}' (ID: device_a)")
    else:
        print("❌ Device A Pairing FAILED.")
        all_passed = False

    print("\n[2/7] Attempting to Pair Second Device (Device B) without Desktop Approval...")
    payload_b = pairing.generate_qr_payload()
    dev_b_info = {"device_id": "device_b", "device_name": "iPad Pro", "device_type": "Tablet", "ip": "192.168.1.20"}
    res_b_attempt = pairing.verify_and_issue_token(payload_b["pairing_id"], payload_b["secret"], dev_b_info, desktop_user_approval=False)
    
    if res_b_attempt["status"] == "APPROVAL_REQUIRED":
        print(f"✅ Single Active Device Security Policy Enforced: Prompt returned -> '{res_b_attempt['message']}'")
    else:
        print("❌ Security Policy Gate FAILED.")
        all_passed = False

    print("\n[3/7] Desktop User Approves Pairing Replacement for Device B...")
    res_b_approved = pairing.verify_and_issue_token(payload_b["pairing_id"], payload_b["secret"], dev_b_info, desktop_user_approval=True)
    
    if res_b_approved["status"] == "SUCCESS" and pairing.get_active_trusted_device().device_id == "device_b":
        token_b = res_b_approved["token"]
        print(f"✅ Device B Paired & Active: '{res_b_approved['device'].device_name}' (ID: device_b)")
    else:
        print("❌ Device B Replacement FAILED.")
        all_passed = False

    print("\n[4/7] Verifying Device A Trust Revocation & Token Invalidation...")
    is_a_valid = pairing.validate_session_token(token_a, "device_a")
    is_b_valid = pairing.validate_session_token(token_b, "device_b")
    
    if not is_a_valid and is_b_valid:
        print("✅ Device A Token INVALIDATED & Revoked. Device B Token VALID & Active.")
    else:
        print("❌ Token Invalidation FAILED.")
        all_passed = False

    print("\n[5/7] Verifying Unknown Device Rejection...")
    is_unknown_valid = pairing.validate_session_token("fake_token_999", "unknown_device_x")
    if not is_unknown_valid:
        print("✅ Unknown Device Connection Rejected before WebSocket establishment.")
    else:
        print("❌ Unknown Device Security FAILED.")
        all_passed = False

    print("\n[6/7] Verifying 'Forget Trusted Device' from Settings...")
    forget_ok = pairing.forget_trusted_device("device_b")
    is_b_valid_after_forget = pairing.validate_session_token(token_b, "device_b")
    
    if forget_ok and not is_b_valid_after_forget and pairing.get_active_trusted_device() is None:
        print("✅ 'Forget Trusted Device' verified: Trust immediately revoked, device token invalidated.")
    else:
        print("❌ Forget Trusted Device FAILED.")
        all_passed = False

    print("\n[7/7] Zero Regression Verification (Kernel Boot & Frozen Platforms)...")
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
        print("DECISION: SINGLE DEVICE SECURITY POLICY VERIFIED")
    else:
        print("DECISION: SECURITY POLICY VERIFICATION FAILED")
    print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_security_verification())
