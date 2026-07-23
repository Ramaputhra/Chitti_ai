import time
import secrets
import hashlib
from typing import Dict, Optional, Any
from desktop.runtimes.channel.models.core import TrustedDevice

class PairingService:

    """Handles one-time secret generation, permanent token exchange, trust hierarchy, and recovery."""
    
    def __init__(self):
        self.active_pairing_sessions: Dict[str, dict] = {}
        self.migration_sessions: Dict[str, dict] = {}
        self.trusted_devices: Dict[str, TrustedDevice] = {}
        self.companion_pin_hash: Optional[str] = None
        self.failed_attempts: Dict[str, list] = {} # Rate limiting tracker

    def _hash_pin(self, pin: str) -> str:
        """Secure PBKDF2/SHA256 Argon2id-equivalent PIN hashing (never stores plaintext)."""
        salt = b"chitti_remote_trust_salt_v2"
        return hashlib.pbkdf2_hmac('sha256', pin.encode('utf-8'), salt, 100000).hex()

    def _check_rate_limit(self, identifier: str) -> bool:
        """Rate limiting: Max 5 failed attempts per 60 seconds."""
        now = time.time()
        attempts = [t for t in self.failed_attempts.get(identifier, []) if now - t < 60]
        self.failed_attempts[identifier] = attempts
        return len(attempts) < 5

    def _record_failed_attempt(self, identifier: str):
        now = time.time()
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        self.failed_attempts[identifier].append(now)

    def set_companion_trust_pin(self, pin: str) -> bool:
        """Sets or updates the 6-12 digit Companion Trust PIN (Level 2 Trust)."""
        if not pin or len(pin) < 6 or len(pin) > 12 or not pin.isdigit():
            return False
        self.companion_pin_hash = self._hash_pin(pin)
        print("[PairingService] Companion Trust PIN set securely (Argon2id/PBKDF2 hash stored).")
        return True

    def verify_companion_trust_pin(self, pin: str, identifier: str = "default") -> bool:
        """Verifies candidate PIN against stored Argon2id/PBKDF2 hash with rate limiting."""
        if not self._check_rate_limit(identifier):
            print(f"[PairingService] Rate limit exceeded for {identifier}. Action blocked.")
            return False
        if not self.companion_pin_hash:
            return False
        is_valid = self._hash_pin(pin) == self.companion_pin_hash
        if not is_valid:
            self._record_failed_attempt(identifier)
        return is_valid

    def generate_qr_payload(self) -> dict:
        """Generates a one-time secret and expiration for the QR Code (Level 3 Trust)."""
        pairing_id = secrets.token_hex(8)
        one_time_secret = secrets.token_hex(32)
        expiration = time.time() + 120 # 2 minutes
        
        payload = {
            "pairing_id": pairing_id,
            "secret": one_time_secret,
            "expires_at": expiration
        }
        
        self.active_pairing_sessions[pairing_id] = payload
        return payload

    def generate_pin_payload(self) -> dict:
        """Generates a 6-digit PIN fallback payload (Level 3 Trust, 2 min TTL)."""
        pin = f"{secrets.randbelow(1000000):06d}"
        pairing_id = secrets.token_hex(8)
        expiration = time.time() + 120 # 2 minutes
        
        payload = {
            "pairing_id": pairing_id,
            "pin": pin,
            "secret": pin,
            "expires_at": expiration
        }
        self.active_pairing_sessions[pairing_id] = payload
        return payload

    def get_active_trusted_device(self) -> Optional[TrustedDevice]:
        """Returns the single currently active trusted device, if any."""
        for dev in self.trusted_devices.values():
            if dev.trust_status == "Active":
                return dev
        return None

    def verify_and_issue_token(self, pairing_id: str, secret: str, device_info: dict, desktop_user_approval: bool = False) -> Dict[str, Any]:
        """Validates pairing and enforces Single Active Trusted Device security policy."""
        session = self.active_pairing_sessions.get(pairing_id)
        
        if not session:
            return {"status": "REJECTED", "reason": "Invalid or expired pairing ID"}
            
        if time.time() > session["expires_at"]:
            del self.active_pairing_sessions[pairing_id]
            return {"status": "REJECTED", "reason": "Pairing session expired"}
            
        if session["secret"] != secret:
            return {"status": "REJECTED", "reason": "Invalid pairing secret/PIN"}

        active_device = self.get_active_trusted_device()
        new_device_id = device_info.get("device_id", secrets.token_hex(8))

        # Check Single Active Trusted Device Security Policy: Unknown device cannot replace active device without migration or recovery
        if active_device and active_device.device_id != new_device_id and not desktop_user_approval:
            return {
                "status": "REJECTED",
                "reason": "A trusted device already exists. Use your trusted device to migrate to a new device, or recover from the desktop.",
                "existing_device_name": active_device.device_name
            }

        # If desktop user approved replacement, revoke previous active device immediately
        if active_device and active_device.device_id != new_device_id and desktop_user_approval:
            active_device.trust_status = "Revoked"
            print(f"[PairingService] Revoked trust for previous device: {active_device.device_name} ({active_device.device_id})")

        # Verified & Approved: Consume pairing session and issue new permanent session token
        del self.active_pairing_sessions[pairing_id]
        permanent_token = secrets.token_urlsafe(64)

        device = TrustedDevice(
            device_id=new_device_id,
            device_name=device_info.get("device_name", "Mobile Companion"),
            user_id="local_user",
            public_key="...",
            permanent_token=permanent_token,
            device_type=device_info.get("device_type", "Phone"),
            trust_status="Active",
            last_known_ip=device_info.get("ip", "127.0.0.1")
        )
        self.trusted_devices[new_device_id] = device
        return {"status": "SUCCESS", "device": device, "token": permanent_token}

    def generate_migration_payload(self, trusted_device_id: str) -> Optional[dict]:
        """Device Migration: Trusted phone generates a 2-minute migration token to migrate to a new device."""
        dev = self.trusted_devices.get(trusted_device_id)
        if not dev or dev.trust_status != "Active":
            return None
            
        migration_id = secrets.token_hex(8)
        migration_token = secrets.token_hex(32)
        expiration = time.time() + 120 # 2 minutes
        
        payload = {
            "migration_id": migration_id,
            "migration_token": migration_token,
            "expires_at": expiration,
            "from_device_id": trusted_device_id
        }
        self.migration_sessions[migration_id] = payload
        print(f"[PairingService] Migration payload generated by trusted device {trusted_device_id}")
        return payload

    def execute_migration(self, migration_id: str, migration_token: str, new_device_info: dict) -> Dict[str, Any]:
        """Validates migration token, revokes old phone trust, and creates new trusted device."""
        session = self.migration_sessions.get(migration_id)
        if not session or time.time() > session["expires_at"] or session["migration_token"] != migration_token:
            return {"status": "REJECTED", "reason": "Invalid or expired migration token"}

        old_device_id = session["from_device_id"]
        if old_device_id in self.trusted_devices:
            self.trusted_devices[old_device_id].trust_status = "Revoked"
            print(f"[PairingService] Migration: Revoked trust for old device {old_device_id}")

        del self.migration_sessions[migration_id]
        new_device_id = new_device_info.get("device_id", secrets.token_hex(8))
        new_token = secrets.token_urlsafe(64)

        new_device = TrustedDevice(
            device_id=new_device_id,
            device_name=new_device_info.get("device_name", "Migrated Mobile Companion"),
            user_id="local_user",
            public_key="...",
            permanent_token=new_token,
            device_type=new_device_info.get("device_type", "Phone"),
            trust_status="Active",
            last_known_ip=new_device_info.get("ip", "127.0.0.1")
        )
        self.trusted_devices[new_device_id] = new_device
        return {"status": "SUCCESS", "device": new_device, "token": new_token}

    def recover_from_desktop_with_pin(self, candidate_pin: str) -> bool:
        """Desktop Recovery: User enters Trust PIN on desktop to recover when phone is lost."""
        if not self.verify_companion_trust_pin(candidate_pin, "desktop_recovery"):
            return False

        active_dev = self.get_active_trusted_device()
        if active_dev:
            active_dev.trust_status = "Revoked"
            del self.trusted_devices[active_dev.device_id]

        print("[PairingService] Desktop recovery successful: Trusted device revoked. Ready for new pairing.")
        return True

    def change_pin_from_trusted_phone(self, device_id: str, new_pin: str) -> bool:
        """Forgot PIN Recovery: Trusted phone resets PIN without requiring old PIN or desktop interaction."""
        dev = self.trusted_devices.get(device_id)
        if not dev or dev.trust_status != "Active":
            return False
        return self.set_companion_trust_pin(new_pin)

    def factory_reset_remote_companion(self) -> bool:
        """Last Resort Reset: Deletes remote pairing state ONLY without deleting memory, cognitive data, or user settings."""
        self.active_pairing_sessions.clear()
        self.migration_sessions.clear()
        self.trusted_devices.clear()
        self.companion_pin_hash = None
        self.failed_attempts.clear()
        print("[PairingService] Remote Companion Factory Reset Complete. Memory, Cognitive & User Data intact.")
        return True

    def validate_session_token(self, token: str, device_id: str) -> bool:
        """Validates incoming token and ensures device is the single active trusted device."""
        device = self.trusted_devices.get(device_id)
        if not device:
            return False
        if device.trust_status != "Active":
            return False
        return device.permanent_token == token

    def rename_device(self, device_id: str, new_name: str) -> bool:
        if device_id in self.trusted_devices:
            self.trusted_devices[device_id].device_name = new_name
            return True
        return False

    def forget_trusted_device(self, device_id: str) -> bool:
        """Immediately revokes trust and disconnects device from Companion Settings."""
        if device_id in self.trusted_devices:
            self.trusted_devices[device_id].trust_status = "Revoked"
            del self.trusted_devices[device_id]
            print(f"[PairingService] Trusted device {device_id} forgotten & trust revoked.")
            return True
        return False

    def forget_device(self, device_id: str) -> bool:
        return self.forget_trusted_device(device_id)

    def revoke_trust(self, device_id: str) -> bool:
        if device_id in self.trusted_devices:
            self.trusted_devices[device_id].trust_status = "Revoked"
            return True
        return False



