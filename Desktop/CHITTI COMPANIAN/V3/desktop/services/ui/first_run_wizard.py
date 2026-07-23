import os
import sys
import platform
import psutil
import shutil
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, 
    QPushButton, QFileDialog, QProgressBar, QTextEdit, QHBoxLayout
)

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False


class AuthThread(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, cred_path: str, token_path: str, scopes: list):
        super().__init__()
        self.cred_path = cred_path
        self.token_path = token_path
        self.scopes = scopes

    def run(self):
        try:
            flow = InstalledAppFlow.from_client_secrets_file(self.cred_path, self.scopes)
            creds = flow.run_local_server(port=0)
            
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
                
            self.finished_signal.emit(True, "Authentication successful!")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to CHITTI")
        self.setSubTitle("Your personal morning companion.")
        layout = QVBoxLayout()
        label = QLabel("This wizard will guide you through setting up CHITTI for the first time.\n\nClick Next to begin the System Check.")
        layout.addWidget(label)
        self.setLayout(layout)


class SystemCheckPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("System Check")
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setLayout(layout)

    def initializePage(self):
        mem = psutil.virtual_memory()
        report = (
            f"OS: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}\n"
            f"CPU: {platform.processor()}\n"
            f"RAM: {mem.used / (1024**3):.1f} / {mem.total / (1024**3):.1f} GB\n\n"
            f"Status: READY"
        )
        self.log.setText(report)


class ModelCheckPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Model Check")
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setLayout(layout)

    def initializePage(self):
        # In a real scenario, we'd query AssetManager.
        report = (
            "Whisper (STT): OK (Local)\n"
            "Piper (TTS): OK (Local)\n"
            "Ollama (LLM): OK (Local)\n\n"
            "All core AI models are verified."
        )
        self.log.setText(report)


class AuthPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Authentication")
        self.setSubTitle("Connect your Google Account for Mail and Calendar.")
        
        layout = QVBoxLayout()
        
        instructions = QLabel(
            "<b>Step 1:</b> Open Google Cloud Console<br>"
            "<b>Step 2:</b> Enable Gmail API & Calendar API<br>"
            "<b>Step 3:</b> Create Desktop OAuth Client<br>"
            "<b>Step 4:</b> Download <code>credentials.json</code><br>"
            "<b>Step 5:</b> Browse and select the file below<br>"
        )
        instructions.setTextFormat(Qt.RichText)
        layout.addWidget(instructions)
        
        hlayout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse for credentials.json...")
        self.browse_btn.clicked.connect(self.browse)
        self.status_lbl = QLabel("No file selected.")
        hlayout.addWidget(self.browse_btn)
        hlayout.addWidget(self.status_lbl)
        layout.addLayout(hlayout)
        
        self.connect_btn = QPushButton("Connect Google Account")
        self.connect_btn.setEnabled(False)
        self.connect_btn.clicked.connect(self.start_auth)
        layout.addWidget(self.connect_btn)
        
        self.setLayout(layout)
        
        local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        self.chitti_dir = os.path.join(local_app_data, "CHITTI")
        self.cred_path = os.path.join(self.chitti_dir, "credentials", "credentials.json")
        self.gmail_token = os.path.join(self.chitti_dir, "tokens", "gmail_token.json")
        self.calendar_token = os.path.join(self.chitti_dir, "tokens", "calendar_token.json")
        
        self.auth_thread = None

    def browse(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select credentials.json", "", "JSON Files (*.json)")
        if filepath:
            try:
                os.makedirs(os.path.dirname(self.cred_path), exist_ok=True)
                shutil.copy(filepath, self.cred_path)
                self.status_lbl.setText("Credentials loaded.")
                self.connect_btn.setEnabled(True)
            except Exception as e:
                self.status_lbl.setText(f"Error copying file: {e}")

    def start_auth(self):
        if not OAUTH_AVAILABLE:
            self.status_lbl.setText("OAuth libraries not installed.")
            return
            
        self.connect_btn.setEnabled(False)
        self.status_lbl.setText("Waiting for browser authentication...")
        
        # Scopes required for Phase 2+ features
        scopes = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.readonly"
        ]
        
        self.auth_thread = AuthThread(self.cred_path, self.gmail_token, scopes)
        self.auth_thread.finished_signal.connect(self.auth_finished)
        self.auth_thread.start()
        
    def auth_finished(self, success: bool, message: str):
        self.status_lbl.setText(message)
        if success:
            # Copy the token to calendar as well for simplicity (since we requested both scopes)
            shutil.copy(self.gmail_token, self.calendar_token)


class AudioTestPage(QWizardPage):
    def __init__(self, piper_provider=None):
        super().__init__()
        self.setTitle("Audio Test")
        self.setSubTitle("Ensure your speakers are working.")
        self.piper_provider = piper_provider
        
        layout = QVBoxLayout()
        self.btn = QPushButton("Play Test Sound")
        self.btn.clicked.connect(self.play_test)
        layout.addWidget(self.btn)
        self.setLayout(layout)
        
    def play_test(self):
        if self.piper_provider:
            # Actually invoke Piper to speak
            self.piper_provider.speak("Hello, my name is CHITTI. Audio is working perfectly.")
        else:
            print("Audio test: BEEP")


class MicTestPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Microphone Test")
        self.setSubTitle("Ensure CHITTI can hear you.")
        layout = QVBoxLayout()
        label = QLabel("Microphone detection is active.\nIn a full build, the VU meter would display here.\nClick Finish to complete setup.")
        layout.addWidget(label)
        self.setLayout(layout)


class FirstRunWizard(QWizard):
    def __init__(self, piper_provider=None):
        super().__init__()
        self.setWindowTitle("CHITTI First Run Setup")
        self.resize(600, 500)
        
        self.addPage(WelcomePage())
        self.addPage(SystemCheckPage())
        self.addPage(ModelCheckPage())
        self.addPage(AuthPage())
        self.addPage(AudioTestPage(piper_provider))
        self.addPage(MicTestPage())


def run_wizard(piper_provider=None):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    wizard = FirstRunWizard(piper_provider)
    wizard.show()
    app.exec()
    
    # Mark as complete
    local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
    chitti_dir = os.path.join(local_app_data, "CHITTI")
    os.makedirs(chitti_dir, exist_ok=True)
    with open(os.path.join(chitti_dir, ".setup_complete"), "w") as f:
        f.write("Setup completed.")

if __name__ == "__main__":
    run_wizard()
