from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class PersonalityProfile:
    """
    S36A-R1: Canonical PersonalityProfile model with slider traits (0.0 to 1.0).
    """
    profile_id: str = "default_friendly"
    profile_name: str = "Friendly"
    professional: float = 0.5
    friendly: float = 0.9
    humorous: float = 0.4
    empathetic: float = 0.8
    motivational: float = 0.7
    concise: float = 0.5
    talkative: float = 0.6
    curious: float = 0.7
    playful: float = 0.5
    formal: float = 0.3
    confident: float = 0.8
    patient: float = 0.9
    encouraging: float = 0.8
    supportive: float = 0.9
    expressive: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "profile_name": self.profile_name,
            "professional": round(self.professional, 2),
            "friendly": round(self.friendly, 2),
            "humorous": round(self.humorous, 2),
            "empathetic": round(self.empathetic, 2),
            "motivational": round(self.motivational, 2),
            "concise": round(self.concise, 2),
            "talkative": round(self.talkative, 2),
            "curious": round(self.curious, 2),
            "playful": round(self.playful, 2),
            "formal": round(self.formal, 2),
            "confident": round(self.confident, 2),
            "patient": round(self.patient, 2),
            "encouraging": round(self.encouraging, 2),
            "supportive": round(self.supportive, 2),
            "expressive": round(self.expressive, 2)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PersonalityProfile":
        return cls(
            profile_id=data.get("profile_id", "custom"),
            profile_name=data.get("profile_name", "Custom"),
            professional=data.get("professional", 0.5),
            friendly=data.get("friendly", 0.5),
            humorous=data.get("humorous", 0.5),
            empathetic=data.get("empathetic", 0.5),
            motivational=data.get("motivational", 0.5),
            concise=data.get("concise", 0.5),
            talkative=data.get("talkative", 0.5),
            curious=data.get("curious", 0.5),
            playful=data.get("playful", 0.5),
            formal=data.get("formal", 0.5),
            confident=data.get("confident", 0.5),
            patient=data.get("patient", 0.5),
            encouraging=data.get("encouraging", 0.5),
            supportive=data.get("supportive", 0.5),
            expressive=data.get("expressive", 0.5)
        )
