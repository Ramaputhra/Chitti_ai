from desktop.platform.shared.interfaces.service import IService


class IScenarioRunner(IService):
    """
    Executes automated YAML scenarios by injecting text into the LanguageRuntime,
    monitoring the EventBus via the EventRecorder, and validating assertions.
    """
    def run_all(self, directory: str) -> bool:
        """
        Runs all .yaml files in the specified directory recursively.
        Returns True if all passed, False otherwise.
        """
        ...
