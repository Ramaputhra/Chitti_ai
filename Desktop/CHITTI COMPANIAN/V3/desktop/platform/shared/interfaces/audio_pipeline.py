from desktop.platform.shared.interfaces.service import IService


class IAudioPipeline(IService):
    """
    Listens to microphone frames, routes them through VAD, and aggregates
    continuous speech into a single AudioReady event.
    """
    pass
