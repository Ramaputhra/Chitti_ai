from abc import ABC, abstractmethod

class InputDriver(ABC):
    @abstractmethod
    def type_text(self, text: str) -> None:
        pass

    @abstractmethod
    def press_key(self, key: str) -> None:
        pass

    @abstractmethod
    def press_hotkey(self, *keys: str) -> None:
        pass

    @abstractmethod
    def click(self, x: int = None, y: int = None) -> None:
        pass

class PyAutoGuiDriver(InputDriver):
    def __init__(self):
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.FAILSAFE = True
        except ImportError:
            self.pyautogui = None

    def _check_installed(self):
        if self.pyautogui is None:
            raise RuntimeError("pyautogui is not installed. Add it to dependencies.")

    def type_text(self, text: str) -> None:
        self._check_installed()
        self.pyautogui.typewrite(text, interval=0.01)

    def press_key(self, key: str) -> None:
        self._check_installed()
        self.pyautogui.press(key)

    def press_hotkey(self, *keys: str) -> None:
        self._check_installed()
        self.pyautogui.hotkey(*keys)

    def click(self, x: int = None, y: int = None) -> None:
        self._check_installed()
        if x is not None and y is not None:
            self.pyautogui.click(x=x, y=y)
        else:
            self.pyautogui.click()

class NativeWindowsDriver(InputDriver):
    def type_text(self, text: str) -> None:
        # Placeholder for ctypes implementation
        pass

    def press_key(self, key: str) -> None:
        pass

    def press_hotkey(self, *keys: str) -> None:
        pass

    def click(self, x: int = None, y: int = None) -> None:
        pass
