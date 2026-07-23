"""
Capability descriptors for the runtime capability system.

This module re-exports from the canonical location in desktop.app.capability_contracts
for backward compatibility with the capability runtime system.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Dict, Any, Optional

# Import canonical types
from desktop.app.capability_contracts import CapabilityDescriptor as CanonicalCapabilityDescriptor

# Re-export for backward compatibility
CapabilityDescriptor = CanonicalCapabilityDescriptor

# Keep VerificationSupport here as it's specific to the runtime system
class VerificationSupport(str, Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
