from desktop.platform.shared.interfaces.service import IService


class IResponseBuilder(IService):
    """
    Receives triggers from the WorkflowExecutor to build a textual response,
    then dispatches the response text to the SpeechSynthesizer.
    """
    pass
