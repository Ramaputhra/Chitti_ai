from desktop.models.presentation import PresentationExperienceManifest

class ExperienceValidator:
    """
    Executable Experience Quality Checklist.
    No experience should register unless it passes validation.
    """
    
    REQUIRED_ACTIONS = {"export_pdf", "export_html", "pin", "replay"}

    @staticmethod
    def validate(manifest: PresentationExperienceManifest) -> bool:
        missing_actions = ExperienceValidator.REQUIRED_ACTIONS - set(manifest.supported_actions)
        
        if missing_actions:
            print(f"[FAIL] Experience {manifest.id} is missing required actions: {missing_actions}")
            return False
            
        if not manifest.supported_widgets:
            print(f"[FAIL] Experience {manifest.id} declares no widgets.")
            return False
            
        # Additional checks: Narration Sync, Theme switching compatibility, etc.
        print(f"[PASS] Experience {manifest.id} validated successfully.")
        return True
