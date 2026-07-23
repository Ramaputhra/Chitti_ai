from desktop.platform.shared.interfaces.service import IService


class ILanguageRuntime(IService):
    """
    Orchestrates the conversion of Audio to Text, and acts as the entry point
    for Developer Console text injections.
    """
    def inject_text(self, text: str) -> None:
        """
        Bypasses the microphone and STT pipeline, emitting Language.TextRecognized directly.
        """
        ...
