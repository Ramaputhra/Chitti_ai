from desktop.platform.shared.interfaces.service import IService


class IIntentEngine(IService):
    """
    Parses incoming Text alongside the current UnifiedContext to determine
    the formal Intent of the user's input.
    """
    pass
