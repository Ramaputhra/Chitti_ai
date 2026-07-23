"""
Platform shared capability models.

This module re-exports from the canonical location in desktop.app.capability_contracts
for backward compatibility with platform-level code.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

# Import canonical types
from desktop.app.capability_contracts import CapabilityDescriptor as CanonicalCapabilityDescriptor

# Re-export for backward compatibility
CapabilityDescriptor = CanonicalCapabilityDescriptor
