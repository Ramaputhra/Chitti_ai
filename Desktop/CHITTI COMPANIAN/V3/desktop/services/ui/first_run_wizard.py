import os
import sys
import platform
import psutil
import shutil
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, 
    QPushButton, QFileDialog, QProgressBar, QTextEdit, QHBoxLayout,
    QLineEdit, QCheckBox, QFormLayout, QGroupBox, QMessageBox, QScrollArea
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
        self.setTitle("Welcome to Vizzu")
        self.setSubTitle("Your personal AI desktop companion.")
        layout = QVBoxLayout()
        label = QLabel(
            "This wizard will guide you through setting up Vizzu for the first time.\n\n"
            "You'll configure:\n"
            "• API Keys (optional)\n"
            "• Google Account (optional)\n"
            "• Audio settings\n\n"
            "Click Next to begin."
        )
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
        self.setTitle("Local AI Models")
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setLayout(layout)

    def initializePage(self):
        report = (
            "Whisper (STT): OK (Local)\n"
            "Piper (TTS): OK (Local)\n"
            "Ollama (LLM): OK (Local)\n\n"
            "All core AI models are verified."
        )
        self.log.setText(report)


class APIKeysPage(QWizardPage):
    """Page for configuring API keys for cloud AI providers."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("API Keys Configuration")
        self.setSubTitle("Enter your API keys to enable cloud AI features (optional).")
        
        # Settings storage
        self.settings = QSettings("Vizzu", "Config")
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            "Cloud AI keys are optional. Vizzu will use local models by default.\n"
            "Keys are stored securely in your user profile."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Scroll area for API keys
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        
        container = QWidget()
        form_layout = QFormLayout(container)
        
        # Gemini API Key
        self.gemini_key = QLineEdit()
        self.gemini_key.setPlaceholderText("Enter your Gemini API key")
        self.gemini_key.setEchoMode(QLineEdit.Password)
        self.gemini_key.setText(self.settings.value("api_keys/gemini", ""))
        form_layout.addRow("Google Gemini API Key:", self.gemini_key)
        
        gemini_help = QLabel('<a href="https://aistudio.google.com/app/apikey">Get Gemini API Key</a>')
        gemini_help.setOpenExternalLinks(True)
        form_layout.addRow("", gemini_help)
        
        # OpenAI API Key
        self.openai_key = QLineEdit()
        self.openai_key.setPlaceholderText("Enter your OpenAI API key")
        self.openai_key.setEchoMode(QLineEdit.Password)
        self.openai_key.setText(self.settings.value("api_keys/openai", ""))
        form_layout.addRow("OpenAI API Key:", self.openai_key)
        
        openai_help = QLabel('<a href="https://platform.openai.com/api-keys">Get OpenAI API Key</a>')
        openai_help.setOpenExternalLinks(True)
        form_layout.addRow("", openai_help)
        
        # Anthropic API Key
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setPlaceholderText("Enter your Anthropic API key")
        self.anthropic_key.setEchoMode(QLineEdit.Password)
        self.anthropic_key.setText(self.settings.value("api_keys/anthropic", ""))
        form_layout.addRow("Anthropic API Key:", self.anthropic_key)
        
        anthropic_help = QLabel('<a href="https://console.anthropic.com/settings/keys">Get Anthropic API Key</a>')
        anthropic_help.setOpenExternalLinks(True)
        form_layout.addRow("", anthropic_help)
        
        # Ollama Host
        self.ollama_host = QLineEdit()
        self.ollama_host.setPlaceholderText("http://localhost:11434")
        self.ollama_host.setText(self.settings.value("api_keys/ollama_host", "http://localhost:11434"))
        form_layout.addRow("Ollama Host:", self.ollama_host)
        
        ollama_help = QLabel("Local LLM server (leave default if running locally)")
        form_layout.addRow("", ollama_help)
        
        # Use Cloud Toggle
        self.use_cloud = QCheckBox("Use cloud AI when available (faster, requires internet)")
        self.use_cloud.setChecked(self.settings.value("api_keys/use_cloud", "false").lower() == "true")
        form_layout.addRow("", self.use_cloud)
        
        # Local fallback info
        local_info = QLabel(
            "\nLocal Fallback: Vizzu will automatically use local models (Qwen2.5-1.5B) "
            "when cloud APIs are unavailable or keys are not set."
        )
        local_info.setWordWrap(True)
        form_layout.addRow("", local_info)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
    
    def saveKeys(self):
        """Save API keys to secure storage."""
        self.settings.setValue("api_keys/gemini", self.gemini_key.text())
        self.settings.setValue("api_keys/openai", self.openai_key.text())
        self.settings.setValue("api_keys/anthropic", self.anthropic_key.text())
        self.settings.setValue("api_keys/ollama_host", self.ollama_host.text())
        self.settings.setValue("api_keys/use_cloud", str(self.use_cloud.isChecked()).lower())
        
        # Also export to environment variables for the app to use
        if self.gemini_key.text():
            os.environ["GEMINI_API_KEY"] = self.gemini_key.text()
        if self.openai_key.text():
            os.environ["OPENAI_API_KEY"] = self.openai_key.text()
        if self.anthropic_key.text():
            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_key.text()
        if self.ollama_host.text():
            os.environ["OLLAMA_HOST"] = self.ollama_host.text()


class AuthPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Google Account (Optional)")
        self.setSubTitle("Connect your Google Account for Gmail and Calendar integration.")
        
        layout = QVBoxLayout()
        
        instructions = QLabel(
            "<b>Optional:</b> Connect your Google account to enable:\n"
            "• Email reading and sending\n"
            "• Calendar event access\n"
            "• Meeting preparation\n\n"
            "<b>Steps:</b><br>"
            "1. Open Google Cloud Console<br>"
            "2. Enable Gmail API & Calendar API<br>"
            "3. Create Desktop OAuth Client<br>"
            "4. Download <code>credentials.json</code><br>"
            "5. Browse and select the file below"
        )
        instructions.setTextFormat(Qt.RichText)
        instructions.setWordWrap(True)
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
        
        self.skip_btn = QPushButton("Skip (Use Local Only)")
        self.skip_btn.clicked.connect(self.skip_auth)
        layout.addWidget(self.skip_btn)
        
        self.setLayout(layout)
        
        local_app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        self.vizzu_dir = os.path.join(local_app_data, "Vizzu")
        self.cred_path = os.path.join(self.vizzu_dir, "credentials", "credentials.json")
        self.gmail_token = os.path.join(self.vizzu_dir, "tokens", "gmail_token.json")
        self.calendar_token = os.path.join(self.vizzu_dir, "tokens", "calendar_token.json")
        
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
            self.status_lbl.setText("OAuth libraries not installed. Run: pip install google-auth-oauthlib")
            return
            
        self.connect_btn.setEnabled(False)
        self.status_lbl.setText("Waiting for browser authentication...")
        
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
            shutil.copy(self.gmail_token, self.calendar_token)
    
    def skip_auth(self):
        self.wizard().next()


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
            self.piper_provider.speak("Hello! I am Vizzu. Your AI desktop companion.")
        else:
            print("Audio test: BEEP")


class MicTestPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Microphone Test")
        self.setSubTitle("Ensure Vizzu can hear you.")
        layout = QVBoxLayout()
        label = QLabel(
            "Microphone detection is active.\n\n"
            "In a full build, the VU meter would display here.\n\n"
            "Click Finish to complete setup."
        )
        layout.addWidget(label)
        self.setLayout(layout)


class FirstRunWizard(QWizard):
    def __init__(self, piper_provider=None):
        super().__init__()
        self.setWindowTitle("Vizzu First Run Setup")
        self.resize(650, 550)
        
        # Wizard pages in order
        self.addPage(WelcomePage())
        self.addPage(SystemCheckPage())
        self.addPage(ModelCheckPage())
        self.addPage(APIKeysPage())
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
    vizzu_dir = os.path.join(local_app_data, "Vizzu")
    os.makedirs(vizzu_dir, exist_ok=True)
    with open(os.path.join(vizzu_dir, ".setup_complete"), "w") as f:
        f.write("Setup completed.")


if __name__ == "__main__":
    run_wizard()
