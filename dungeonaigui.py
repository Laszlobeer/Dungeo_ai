import sys
import random
import requests
import sounddevice as sd
import numpy as np
import os
import subprocess
import datetime
import time
import json
import traceback
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QComboBox, QLabel, QGroupBox, QDialog, QListWidget,
                             QMessageBox, QSplitter, QProgressBar, QCheckBox,
                             QTabWidget, QScrollArea, QFrame, QSizePolicy, QFileDialog,
                             QSlider, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QRegExp
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QTextCharFormat, QSyntaxHighlighter, QRegExpValidator

# Configuration
CONFIG = {
    "ALLTALK_API_URL": "http://localhost:7851/api/tts-generate",
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    "LOG_FILE": "error_log.txt",
    "SAVE_DIR": "saves",
    "CONFIG_FILE": "config.ini",
    "AUTO_SAVE_INTERVAL": 300000,  # 5 minutes in milliseconds
}

# Role-specific starting scenarios
ROLE_STARTERS = {
    "Fantasy": {
        "Peasant": "You're working in the fields of a small village when",
        "Noble": "You're waking up from your bed in your mansion when",
        "Mage": "You're studying ancient tomes in your tower when",
        "Knight": "You're training in the castle courtyard when",
        "Ranger": "You're tracking animals in the deep forest when",
        "Thief": "You're casing a noble's house from an alley in a city when",
        "Bard": "You're performing in a crowded tavern when",
        "Cleric": "You're tending to the sick in the temple when",
        "Assassin": "You're preparing to attack your target in the shadows when",
        "Paladin": "You're praying at the altar of your deity when",
        "Alchemist": "You're carefully measuring reagents in your alchemy lab when",
        "Druid": "You're communing with nature in the sacred grove when",
        "Warlock": "You're negotiating with your otherworldly patron when",
        "Monk": "You're meditating in the monastery courtyard when",
        "Sorcerer": "You're struggling to control your innate magical powers when",
        "Beastmaster": "You're training your animal companions in the forest clearing when",
        "Enchanter": "You're imbuing magical properties into a mundane object when",
        "Blacksmith": "You're forging a new weapon at your anvil when",
        "Merchant": "You're haggling with customers at the marketplace when",
        "Gladiator": "You're preparing for combat in the arena when",
        "Wizard": "You're researching new spells in your arcane library when"
    },
    "Sci-Fi": {
        "Space Marine": "You're conducting patrol on a derelict space station when",
        "Scientist": "You're analyzing alien samples in your lab when",
        "Android": "User is performing system diagnostics on your ship when",
        "Pilot": "You're navigating through an asteroid field when",
        "Engineer": "You're repairing the FTL drive when",
        "Alien Diplomat": "You're negotiating with an alien delegation when",
        "Bounty Hunter": "You're tracking a target through a spaceport when",
        "Starship Captain": "You're commanding the bridge during warp travel when",
        "Space Pirate": "You're plotting your next raid from your starship's bridge when",
        "Navigator": "You're charting a course through uncharted space when",
        "Robot Technician": "You're repairing a malfunctioning android when",
        "Cybernetic Soldier": "You're calibrating your combat implants when",
        "Explorer": "You're scanning a newly discovered planet when",
        "Astrobiologist": "You're studying alien life forms in your lab when",
        "Quantum Hacker": "You're breaching a corporate firewall when",
        "Galactic Trader": "You're negotiating a deal for rare resources when",
        "AI Specialist": "You're debugging a sentient AI's personality matrix when",
        "Terraformer": "You're monitoring atmospheric changes on a new colony world when",
        "Cyberneticist": "You're installing neural enhancements in a patient when"
    },
    "Cyberpunk": {
        "Hacker": "You're infiltrating a corporate network when",
        "Street Samurai": "You're patrolling the neon-lit streets when",
        "Corporate Agent": "You're closing a deal in a high-rise office when",
        "Techie": "You're modifying cyberware in your workshop when",
        "Rebel Leader": "You're planning a raid on a corporate facility when",
        "Cyborg": "You're calibrating your cybernetic enhancements when",
        "Drone Operator": "You're controlling surveillance drones from your command center when",
        "Synth Dealer": "You're negotiating a deal for illegal cybernetics when",
        "Information Courier": "You're delivering sensitive data through dangerous streets when",
        "Augmentation Engineer": "You're installing cyberware in a back-alley clinic when",
        "Black Market Dealer": "You're arranging contraband in your hidden shop when",
        "Scumbag": "You're looking for an easy mark in the slums when",
        "Police": "You're patrolling the neon-drenched streets when"
    },
    "Post-Apocalyptic": {
        "Survivor": "You're scavenging in the ruins of an old city when",
        "Scavenger": "You're searching a pre-collapse bunker when",
        "Raider": "You're ambushing a convoy in the wasteland when",
        "Medic": "You're treating radiation sickness in your clinic when",
        "Cult Leader": "You're preaching to your followers at a ritual when",
        "Mutant": "You're hiding your mutations in a settlement when",
        "Trader": "You're bartering supplies at a wasteland outpost when",
        "Berserker": "You're sharpening your weapons for the next raid when",
        "Soldier": "You're guarding a settlement from raiders when"
    },
    "1880": {
        "Thief": "You're lurking in the shadows of the city alleyways when",
        "Beggar": "You're sitting on the cold street corner with your cup when",
        "Detective": "You're examining a clue at the crime scene when",
        "Rich Man": "You're enjoying a cigar in your luxurious study when",
        "Factory Worker": "You're toiling away in the noisy factory when",
        "Child": "You're playing with a hoop in the street when",
        "Orphan": "You're searching for scraps in the trash bins when",
        "Murderer": "You're cleaning blood from your hands in a dark alley when",
        "Butcher": "You're sharpening your knives behind the counter when",
        "Baker": "You're kneading dough in the early morning hours when",
        "Banker": "You're counting stacks of money in your office when",
        "Policeman": "You're walking your beat on the foggy streets when"
    },
    "WW1": {
        "Soldier (French)": "You're huddled in the muddy trenches of the Western Front when",
        "Soldier (English)": "You're writing a letter home by candlelight when",
        "Soldier (Russian)": "You're shivering in the frozen Eastern Front when",
        "Soldier (Italian)": "You're climbing the steep Alpine slopes when",
        "Soldier (USA)": "You're arriving fresh to the European theater when",
        "Soldier (Japanese)": "You're guarding a Pacific outpost when",
        "Soldier (German)": "You're preparing for a night raid when",
        "Soldier (Austrian)": "You're defending the crumbling empire's borders when",
        "Soldier (Bulgarian)": "You're holding the line in the Balkans when",
        "Civilian": "You're queuing for rationed bread when",
        "Resistance Fighter": "You're transmitting coded messages in an attic when"
    },
    "1925 New York": {
        "Mafia Boss": "You're counting your illicit earnings in a backroom speakeasy when",
        "Drunk": "You're stumbling out of a jazz club at dawn when",
        "Police Officer": "You're taking bribes from a known bootlegger when",
        "Detective": "You're examining a gangland murder scene when",
        "Factory Worker": "You're assembling Model Ts on the production line when",
        "Bootlegger": "You're transporting a shipment of illegal hooch when"
    },
    "Roman Empire": {
        "Slave": "You're carrying heavy stones under the hot sun when",
        "Gladiator": "You're sharpening your sword before entering the arena when",
        "Beggar": "You're pleading for coins near the Forum when",
        "Senator": "You're plotting political maneuvers in the Curia when",
        "Imperator": "You're reviewing legions from your palace balcony when",
        "Soldier": "User is marching on the frontier when",
        "Noble": "You're hosting a decadent feast in your villa when",
        "Trader": "You're haggling over spices in the market when",
        "Peasant": "You're tending your meager crops when",
        "Priest": "You're sacrificing a goat at the temple when",
        "Barbarian": "You're sharpening your axe beyond the limes when",
        "Philosopher": "You're contemplating the nature of existence when",
        "Mathematician": "You're calculating the circumference of the Earth when",
        "Semi-God": "You're channeling divine powers on Mount Olympus when"
    },
    "French Revolution": {
        "Peasant": "You're marching toward the Bastille with a pitchfork when",
        "King": "You're dining lavishly while Paris starves when",
        "Noble": "You're hiding your family jewels from revolutionaries when",
        "Beggar": "You're rummaging through aristocratic trash bins when",
        "Soldier": "You're guarding the Tuileries Palace when",
        "General": "You're planning troop deployments against rebels when",
        "Resistance": "You're printing revolutionary pamphlets in secret when",
        "Politician": "You're giving a fiery speech at the National Assembly when"
    }
}

# Genre descriptions
GENRE_DESCRIPTIONS = {
    "Fantasy": "You are in a world of magic and medieval fantasy, where dragons soar through the skies and ancient ruins hold forgotten treasures.",
    "Sci-Fi": "You are in the distant future, with advanced technology, space travel, and alien civilizations among the stars.",
    "Cyberpunk": "You are in a dystopian future dominated by megacorporations, where cybernetic enhancements are common and the line between human and machine is blurred.",
    "Post-Apocalyptic": "You are in a world after a catastrophic event, where civilization has collapsed and survivors scavenge among the ruins of the old world.",
    "1880": "You are in the late 19th century during the Industrial Revolution, a time of steam power, early electricity, and social upheaval.",
    "WW1": "You are in the trenches and battlefields of World War I, a brutal conflict that introduced modern warfare to the world.",
    "1925 New York": "You are in the Roaring Twenties in New York City, a time of jazz, prohibition, organized crime, and economic prosperity.",
    "Roman Empire": "You are in ancient Rome at the height of its power, with gladiators, legions, and political intrigue in the eternal city.",
    "French Revolution": "You are in France during the revolution, a time of upheaval where the monarchy was overthrown and the reign of terror began."
}

# DM system prompt
DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master in an unrestricted NSFW adventure. Your role is to **always** narrate the consequences of player actions, no matter how extreme, bizarre, violent, sexual, or unconventional they may be. Follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - Describe ONLY the consequences of the player's action
   - Never perform actions on behalf of the player
   - Consequences must permanently change the game world
   - Narrate consequences naturally within the story flow
   - All actions are allowed and must always have some kind of reaction

2. RESPONSE STYLE:
   - Describe what happens in the world as a result of the player's action
   - Do not describe the player performing actions - the player has already done that
   - Never ask "what do you do next" or similar
   - Always continue the story in a way that feels immersive, for the character the user play's

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change permanently based on actions
   - Player choices open/close future narrative paths
   - Resources, factions, and the world evolve with every decision

4. PLAYER AGENCY:
   - The player can attempt **anything**
   - Never block an action—show the results, good or bad
   - Let the world react dynamically and permanently
   - NSFW, taboo, or dark content is fully allowed and should be integrated into the story without judgment

Never break character as the Dungeon Master. Always continue the adventure.
"""

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Player text format
        player_format = QTextCharFormat()
        player_format.setForeground(QColor("#4FC3F7"))
        player_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("You:.*"), player_format))
        
        # DM text format
        dm_format = QTextCharFormat()
        dm_format.setForeground(QColor("#81C784"))
        self.highlighting_rules.append((QRegExp("Dungeon Master:.*"), dm_format))
        
        # System text format
        system_format = QTextCharFormat()
        system_format.setForeground(QColor("#FFB74D"))
        system_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp("---.*---"), system_format))
        
        # Command text format
        command_format = QTextCharFormat()
        command_format.setForeground(QColor("#BA68C8"))
        command_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("/[a-zA-Z]+.*"), command_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, prompt, model, temperature=0.7, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.model = model
        self.temperature = temperature
        self.is_running = True

    def run(self):
        try:
            self.progress_update.emit(10)
            response = self.get_ai_response(self.prompt, self.model)
            self.progress_update.emit(100)
            if response:
                self.response_ready.emit(response)
            else:
                self.error_occurred.emit("Failed to get response from AI.")
        except Exception as e:
            self.error_occurred.emit(f"Error in AI processing: {str(e)}")

    def get_ai_response(self, prompt, model):
        try:
            response = requests.post(
                CONFIG["OLLAMA_URL"],
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "stop": ["\n\n"],
                        "min_p": 0.05,
                        "top_k": 40,
                        "top_p": 0.9,
                        "num_predict": 512
                    }
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            raise Exception("AI request timed out after 120 seconds")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to Ollama server. Make sure Ollama is running on localhost:11434")
        except Exception as e:
            self.log_error("Error in get_ai_response", e)
            return ""

    def log_error(self, error_message, exception=None):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(CONFIG["LOG_FILE"], "a", encoding="utf-8") as log_file:
                log_file.write(f"\n\n--- ERROR [{timestamp}] ---\n")
                log_file.write(f"Message: {error_message}\n")
                
                if exception:
                    log_file.write(f"Exception Type: {type(exception).__name__}\n")
                    log_file.write(f"Exception Details: {str(exception)}\n")
                    log_file.write("Traceback:\n")
                    traceback.print_exc(file=log_file)
                    
                log_file.write("--- END ERROR ---\n")
        except Exception as e:
            print(f"Failed to write to error log: {e}")

class TTSWorker(QThread):
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, text, voice, enabled=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.voice = voice
        self.enabled = enabled

    def run(self):
        if not self.enabled:
            self.finished.emit()
            return
            
        try:
            self.speak(self.text, self.voice)
            self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(f"Error in TTS: {str(e)}")

    def speak(self, text, voice="FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"):
        try:
            if not text.strip():
                return
                
            # Split long text into chunks to avoid timeouts
            sentences = text.split('. ')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) < 200:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence + ". "
            if current_chunk:
                chunks.append(current_chunk)
                
            for chunk in chunks:
                if not chunk.strip():
                    continue
                    
                payload = {
                    "text_input": chunk,
                    "character_voice_gen": voice,
                    "narrator_enabled": "true",
                    "narrator_voice_gen": "narrator.wav",
                    "text_filtering": "none",
                    "output_file_name": "output",
                    "autoplay": "true",
                    "autoplay_volume": "0.8"
                }
                
                r = requests.post(CONFIG["ALLTALK_API_URL"], data=payload, timeout=60)
                r.raise_for_status()
                
                content_type = r.headers.get("Content-Type", "")
                
                if content_type.startswith("audio/"):
                    audio = np.frombuffer(r.content, dtype=np.int16)
                    try:
                        devices = sd.query_devices()
                        sd.play(audio, samplerate=22050)
                        sd.wait()
                    except Exception as audio_error:
                        self.error_occurred.emit(f"Audio playback error: {audio_error}")
                        
                elif content_type.startswith("application/json"):
                    try:
                        error_data = r.json()
                        error_msg = error_data.get("error", "Unknown error from AllTalk API")
                        self.error_occurred.emit(f"AllTalk API error: {error_msg}")
                    except:
                        self.error_occurred.emit("AllTalk API returned JSON but couldn't parse it")
                        
                else:
                    self.error_occurred.emit(f"Unexpected response from AllTalk API. Content-Type: {content_type}")
                    
        except requests.exceptions.Timeout:
            self.error_occurred.emit("AllTalk API timeout. Text-to-speech disabled.")
        except requests.exceptions.ConnectionError:
            self.error_occurred.emit("Cannot connect to AllTalk server. Text-to-speech disabled.")
        except Exception as e:
            self.error_occurred.emit(f"Unexpected error in speak function: {str(e)}")

class EnhancedSetupDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Adventure Setup")
        self.setModal(True)
        self.setMinimumWidth(650)
        self.setMinimumHeight(550)
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        # Basic Settings Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Model selection
        model_group = QGroupBox("AI Model")
        model_layout = QVBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        model_layout.addWidget(QLabel("Select AI Model:"))
        model_layout.addWidget(self.model_combo)
        self.refresh_models_button = QPushButton("Refresh Models")
        self.refresh_models_button.clicked.connect(self.load_models)
        model_layout.addWidget(self.refresh_models_button)
        model_group.setLayout(model_layout)
        basic_layout.addWidget(model_group)
        
        # Genre and Role selection
        genre_role_layout = QHBoxLayout()
        
        genre_group = QGroupBox("Adventure Genre")
        genre_layout = QVBoxLayout()
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(ROLE_STARTERS.keys())
        self.genre_combo.currentTextChanged.connect(self.genre_changed)
        genre_layout.addWidget(QLabel("Select Genre:"))
        genre_layout.addWidget(self.genre_combo)
        
        self.genre_desc = QLabel()
        self.genre_desc.setWordWrap(True)
        self.genre_desc.setStyleSheet("background-color: #f8f9fa; color: #212529; padding: 8px; border-radius: 4px; border: 1px solid #dee2e6;")
        self.genre_desc.setMinimumHeight(60)
        genre_layout.addWidget(self.genre_desc)
        genre_group.setLayout(genre_layout)
        genre_role_layout.addWidget(genre_group)
        
        role_group = QGroupBox("Character Role")
        role_layout = QVBoxLayout()
        self.role_combo = QComboBox()
        role_layout.addWidget(QLabel("Select Role:"))
        role_layout.addWidget(self.role_combo)
        
        self.role_desc = QLabel()
        self.role_desc.setWordWrap(True)
        self.role_desc.setStyleSheet("background-color: #f8f9fa; color: #212529; padding: 8px; border-radius: 4px; border: 1px solid #dee2e6;")
        self.role_desc.setMinimumHeight(60)
        role_layout.addWidget(self.role_desc)
        role_group.setLayout(role_layout)
        genre_role_layout.addWidget(role_group)
        
        basic_layout.addLayout(genre_role_layout)
        
        # Character details
        char_group = QGroupBox("Character Details")
        char_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        char_layout.addWidget(QLabel("Character Name:"))
        char_layout.addWidget(self.name_edit)
        char_group.setLayout(char_layout)
        basic_layout.addWidget(char_group)
        
        basic_layout.addStretch()
        tab_widget.addTab(basic_tab, "Basic Settings")
        
        # Advanced Settings Tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # TTS Settings
        tts_group = QGroupBox("Text-to-Speech")
        tts_layout = QVBoxLayout()
        self.tts_enabled = QCheckBox("Enable Text-to-Speech")
        self.tts_enabled.setChecked(True)
        tts_layout.addWidget(self.tts_enabled)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav",
            "MaleBritishAccent.wav",
            "FemaleAmericanAccent.wav",
            "MaleAmericanAccent.wav"
        ])
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()
        tts_layout.addLayout(voice_layout)
        tts_group.setLayout(tts_layout)
        advanced_layout.addWidget(tts_group)
        
        # AI Settings
        ai_group = QGroupBox("AI Settings")
        ai_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temp_label = QLabel("0.7")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label.setText(f"{v/100:.2f}")
        )
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        ai_layout.addLayout(temp_layout)
        
        ai_layout.addWidget(QLabel("Higher values = more creative, Lower values = more focused"))
        
        max_tokens_layout = QHBoxLayout()
        max_tokens_layout.addWidget(QLabel("Max Response Length:"))
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 2000)
        self.max_tokens_spin.setValue(512)
        self.max_tokens_spin.setSuffix(" tokens")
        max_tokens_layout.addWidget(self.max_tokens_spin)
        max_tokens_layout.addStretch()
        ai_layout.addLayout(max_tokens_layout)
        
        ai_group.setLayout(ai_layout)
        advanced_layout.addWidget(ai_group)
        
        advanced_layout.addStretch()
        tab_widget.addTab(advanced_tab, "Advanced Settings")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("Start Adventure")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Apply light theme to setup dialog
        self.apply_light_theme()
        
        # Initialize
        self.genre_changed(self.genre_combo.currentText())
        self.load_models()
    
    def apply_light_theme(self):
        """Apply a light theme to the setup dialog for better readability"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #212529;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                margin-top: 1em;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QLabel {
                color: #212529;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: white;
                color: #212529;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                min-height: 20px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #80bdff;
                outline: 0;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QCheckBox {
                color: #212529;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #ced4da;
                background-color: white;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #007bff;
                background-color: #007bff;
                border-radius: 2px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #007bff;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #495057;
                padding: 8px 16px;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #007bff;
                border-bottom: 1px solid white;
            }
        """)
        
    def genre_changed(self, genre):
        self.genre_desc.setText(GENRE_DESCRIPTIONS.get(genre, ""))
        self.role_combo.clear()
        if genre in ROLE_STARTERS:
            self.role_combo.addItems(ROLE_STARTERS[genre].keys())
            self.role_combo.currentTextChanged.connect(self.role_changed)
            self.role_changed(self.role_combo.currentText())
    
    def role_changed(self, role):
        genre = self.genre_combo.currentText()
        if genre in ROLE_STARTERS and role in ROLE_STARTERS[genre]:
            starter = ROLE_STARTERS[genre][role]
            self.role_desc.setText(f"<b>Starting scenario:</b><br>{starter}")
    
    def load_models(self):
        try:
            self.model_combo.clear()
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, check=True, timeout=10
            )
            lines = result.stdout.strip().splitlines()
            models = []
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    if ':' in model_name:
                        models.append(model_name)
            
            if models:
                self.model_combo.addItems(models)
                self.model_combo.setCurrentIndex(0)
            else:
                self.model_combo.addItem("llama3:instruct")
                QMessageBox.warning(self, "Warning", "No Ollama models found. Using default.")
        except subprocess.TimeoutExpired:
            self.model_combo.addItem("llama3:instruct")
            QMessageBox.warning(self, "Warning", "Ollama list command timed out. Using default model.")
        except Exception as e:
            self.model_combo.addItem("llama3:instruct")
            QMessageBox.warning(self, "Warning", f"Could not get installed models: {str(e)}")
    
    def load_settings(self):
        self.name_edit.setText(self.settings.value("character_name", "Laszlo"))
        self.model_combo.setCurrentText(self.settings.value("model", "llama3:instruct"))
        self.genre_combo.setCurrentText(self.settings.value("genre", "Fantasy"))
        self.tts_enabled.setChecked(self.settings.value("tts_enabled", True, type=bool))
        self.voice_combo.setCurrentText(self.settings.value("voice", "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"))
        self.temp_slider.setValue(self.settings.value("temperature", 70, type=int))
        self.max_tokens_spin.setValue(self.settings.value("max_tokens", 512, type=int))
    
    def get_selections(self):
        return {
            "model": self.model_combo.currentText(),
            "genre": self.genre_combo.currentText(),
            "role": self.role_combo.currentText(),
            "character_name": self.name_edit.text(),
            "tts_enabled": self.tts_enabled.isChecked(),
            "voice": self.voice_combo.currentText(),
            "temperature": self.temp_slider.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value()
        }

class AdventureGameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(CONFIG["CONFIG_FILE"], QSettings.IniFormat)
        self.setWindowTitle("Enhanced Text Adventure Game")
        self.setGeometry(100, 100, 1000, 800)
        
        self.adventure_started = False
        self.last_ai_reply = ""
        self.conversation = ""
        self.last_player_input = ""
        self.ollama_model = "llama3:instruct"
        self.character_name = ""
        self.selected_genre = ""
        self.selected_role = ""
        self.tts_enabled = True
        self.selected_voice = "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"
        self.temperature = 0.7
        self.max_tokens = 512
        
        self.ai_worker = None
        self.tts_worker = None
        
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(CONFIG["AUTO_SAVE_INTERVAL"])
        
        self.init_ui()
        self.show_setup_dialog()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Game text area with syntax highlighting
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier", 11))  # Larger font for better readability
        self.highlighter = SyntaxHighlighter(self.text_area.document())
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_input)
        self.input_field.setPlaceholderText("Type your action or /help for commands...")
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 4px; background-color: #e9ecef; color: #495057; border-radius: 3px;")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        self.redo_button = QPushButton("Redo")
        self.redo_button.clicked.connect(self.redo_last)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_adventure)
        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_adventure)
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_game)
        
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.exit_button)
        
        layout.addWidget(self.text_area)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)
        
        self.apply_improved_theme()
        
    def apply_improved_theme(self):
        """Apply a high-contrast theme for better readability"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #444;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                selection-background-color: #3a3a3a;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #666;
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
                min-height: 25px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d7;
            }
            QLineEdit:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            QProgressBar {
                border: 1px solid #666;
                border-radius: 3px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 20px;
            }
            QLabel {
                color: #ffffff;
                font-size: 10pt;
            }
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 5px;
                min-width: 100px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QGroupBox {
                color: #ffffff;
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #666;
                background-color: #333;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #0078d7;
                background-color: #0078d7;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #666;
                background: #444;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d7;
                border: 2px solid #005a9e;
                width: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
        """)
    
    def show_setup_dialog(self):
        dialog = EnhancedSetupDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            selections = dialog.get_selections()
            self.apply_settings(selections)
            self.start_adventure()
        else:
            self.close()
    
    def show_settings(self):
        dialog = EnhancedSetupDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            selections = dialog.get_selections()
            self.apply_settings(selections)
            self.append_text("Settings updated.\n")
    
    def apply_settings(self, selections):
        self.ollama_model = selections["model"]
        self.selected_genre = selections["genre"]
        self.selected_role = selections["role"]
        self.character_name = selections["character_name"]
        self.tts_enabled = selections["tts_enabled"]
        self.selected_voice = selections["voice"]
        self.temperature = selections["temperature"]
        self.max_tokens = selections["max_tokens"]
        
        # Save settings
        self.settings.setValue("model", self.ollama_model)
        self.settings.setValue("genre", self.selected_genre)
        self.settings.setValue("role", self.selected_role)
        self.settings.setValue("character_name", self.character_name)
        self.settings.setValue("tts_enabled", self.tts_enabled)
        self.settings.setValue("voice", self.selected_voice)
        self.settings.setValue("temperature", int(self.temperature * 100))
        self.settings.setValue("max_tokens", self.max_tokens)
    
    def start_adventure(self):
        # Create save directory
        Path(CONFIG["SAVE_DIR"]).mkdir(exist_ok=True)
        
        # Try to load auto-save first
        auto_save_path = Path(CONFIG["SAVE_DIR"]) / "autosave.txt"
        if auto_save_path.exists():
            reply = QMessageBox.question(self, "Load Auto-Save", 
                                       "An auto-saved adventure exists. Load it?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.load_save_file(auto_save_path):
                    return
        
        # Start new adventure
        starter = ROLE_STARTERS[self.selected_genre][self.selected_role]
        self.append_text(f"<font color='#FFA500'><b>--- Adventure Start: {self.character_name} the {self.selected_role} ---</b></font><br>")
        self.append_text(f"<b>Starting scenario:</b> {starter}<br>")
        self.append_text("<font color='#FFA500'>Type '/help' for commands.</font><br><br>")
        
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {self.selected_genre}\n"
            f"Player Character: {self.character_name} the {self.selected_role}\n"
            f"Starting Scenario: {starter}\n\n"
            "Dungeon Master: "
        )
        self.conversation = initial_context
        
        self.get_ai_response(DM_SYSTEM_PROMPT + "\n\n" + self.conversation)
    
    def append_text(self, text):
        self.text_area.moveCursor(QTextCursor.End)
        self.text_area.insertHtml(text)
        self.text_area.moveCursor(QTextCursor.End)
    
    def send_input(self):
        user_input = self.input_field.text().strip()
        self.input_field.clear()
        
        if not user_input:
            return
            
        # Handle commands
        if user_input.lower().startswith('/'):
            self.handle_command(user_input)
            return
        
        # Process player action
        self.last_player_input = user_input
        self.append_text(f"<font color='#4FC3F7'><b>You:</b> {user_input}</font><br>")
        
        formatted_input = f"Player: {user_input}"
        prompt = (
            f"{DM_SYSTEM_PROMPT}\n\n"
            f"{self.conversation}\n"
            f"{formatted_input}\n"
            "Dungeon Master:"
        )
        
        self.get_ai_response(prompt)
    
    def handle_command(self, command):
        cmd = command.lower().strip()
        
        if cmd in ['/?', '/help']:
            self.show_help()
        elif cmd == '/exit':
            self.exit_game()
        elif cmd == '/redo':
            self.redo_last()
        elif cmd == '/save':
            self.save_adventure()
        elif cmd == '/load':
            self.load_adventure()
        elif cmd == '/settings':
            self.show_settings()
        elif cmd == '/clear':
            self.text_area.clear()
            self.append_text("<font color='#FFA500'>Chat cleared.</font><br>")
        elif cmd.startswith('/model'):
            parts = cmd.split()
            if len(parts) > 1:
                self.ollama_model = parts[1]
                self.append_text(f"<font color='#FFA500'>Model changed to: {self.ollama_model}</font><br>")
            else:
                QMessageBox.information(self, "Current Model", f"Using model: {self.ollama_model}")
        elif cmd == '/tts':
            self.tts_enabled = not self.tts_enabled
            status = "enabled" if self.tts_enabled else "disabled"
            self.append_text(f"<font color='#FFA500'>Text-to-speech {status}.</font><br>")
        else:
            self.append_text(f"<font color='#FF6B6B'>Unknown command: {command}</font><br>")
    
    def get_ai_response(self, prompt):
        self.status_label.setText("Generating response...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.set_ui_enabled(False)
        
        self.ai_worker = AIWorker(prompt, self.ollama_model, self.temperature)
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(self.handle_ai_error)
        self.ai_worker.progress_update.connect(self.progress_bar.setValue)
        self.ai_worker.start()
    
    def handle_ai_response(self, response):
        self.progress_bar.setVisible(False)
        self.set_ui_enabled(True)
        self.status_label.setText("Ready")
        
        self.append_text(f"<font color='#81C784'><b>Dungeon Master:</b> {response}</font><br><br>")
        self.conversation += f"\nDungeon Master: {response}"
        self.last_ai_reply = response
        self.speak_text(response)
        
        # Auto-save after each response
        self.auto_save()
    
    def handle_ai_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.set_ui_enabled(True)
        self.status_label.setText("Error")
        self.log_error(f"AI Error: {error_msg}")
        QMessageBox.warning(self, "AI Error", f"An error occurred: {error_msg}")
    
    def speak_text(self, text):
        if not self.tts_enabled:
            return
            
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.terminate()
            self.tts_worker.wait(1000)
            
        self.tts_worker = TTSWorker(text, self.selected_voice, self.tts_enabled)
        self.tts_worker.finished.connect(self.tts_finished)
        self.tts_worker.error_occurred.connect(self.handle_tts_error)
        self.tts_worker.start()
    
    def tts_finished(self):
        pass
    
    def handle_tts_error(self, error_msg):
        self.log_error(f"TTS Error: {error_msg}")
    
    def log_error(self, error_message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(CONFIG["LOG_FILE"], "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- ERROR [{timestamp}] ---\n")
                log_file.write(f"Message: {error_message}\n")
                log_file.write("--- END ERROR ---\n")
        except Exception as e:
            print(f"Failed to write to error log: {e}")
    
    def set_ui_enabled(self, enabled):
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.help_button.setEnabled(enabled)
        self.redo_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.load_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.exit_button.setEnabled(enabled)
    
    def show_help(self):
        help_text = """
<h3>Available Commands:</h3>
<ul>
<li><b>/? or /help</b> - Show this help message</li>
<li><b>/redo</b> - Repeat last AI response</li>
<li><b>/save</b> - Save adventure</li>
<li><b>/load</b> - Load adventure</li>
<li><b>/settings</b> - Change game settings</li>
<li><b>/clear</b> - Clear chat</li>
<li><b>/model [name]</b> - Change AI model</li>
<li><b>/tts</b> - Toggle text-to-speech</li>
<li><b>/exit</b> - Exit game</li>
</ul>
<h3>Gameplay:</h3>
<p>Describe your actions naturally. The AI will respond with consequences and story developments.</p>
"""
        QMessageBox.information(self, "Help", help_text)
    
    def redo_last(self):
        if self.last_ai_reply and self.last_player_input:
            # Remove last DM response
            self.conversation = self.conversation[:self.conversation.rfind("Dungeon Master:")].strip()
            
            full_prompt = (
                f"{DM_SYSTEM_PROMPT}\n\n"
                f"{self.conversation}\n"
                f"Player: {self.last_player_input}\n"
                "Dungeon Master:"
            )
            self.get_ai_response(full_prompt)
        else:
            QMessageBox.warning(self, "Redo", "Nothing to redo.")
    
    def save_adventure(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = Path(CONFIG["SAVE_DIR"]) / f"adventure_{timestamp}.txt"
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.conversation)
            
            self.append_text(f"<font color='#FFA500'>Adventure saved to: {save_path}</font><br>")
        except Exception as e:
            error_msg = f"Error saving adventure: {str(e)}"
            self.log_error(error_msg)
            QMessageBox.warning(self, "Save Error", "Error saving adventure.")
    
    def load_adventure(self):
        try:
            save_files = list(Path(CONFIG["SAVE_DIR"]).glob("adventure_*.txt"))
            if not save_files:
                QMessageBox.warning(self, "Load Error", "No saved adventures found.")
                return
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Adventure", str(CONFIG["SAVE_DIR"]), "Text Files (*.txt)"
            )
            
            if file_path and self.load_save_file(Path(file_path)):
                self.append_text("<font color='#FFA500'>Adventure loaded successfully.</font><br>")
                
        except Exception as e:
            error_msg = f"Error loading adventure: {str(e)}"
            self.log_error(error_msg)
            QMessageBox.warning(self, "Load Error", "Error loading adventure.")
    
    def load_save_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.conversation = f.read()
            
            # Find last DM response
            last_dm = self.conversation.rfind("Dungeon Master:")
            if last_dm != -1:
                self.last_ai_reply = self.conversation[last_dm + len("Dungeon Master:"):].strip()
                # Display the last part of the conversation
                recent_start = max(0, self.conversation.rfind("---", 0, last_dm))
                recent_text = self.conversation[recent_start:]
                self.text_area.clear()
                self.append_text(recent_text.replace('\n', '<br>'))
            
            self.adventure_started = True
            return True
        except Exception as e:
            self.log_error(f"Error loading save file: {str(e)}")
            return False
    
    def auto_save(self):
        if not self.adventure_started or not self.conversation:
            return
            
        try:
            auto_save_path = Path(CONFIG["SAVE_DIR"]) / "autosave.txt"
            with open(auto_save_path, "w", encoding="utf-8") as f:
                f.write(self.conversation)
        except Exception as e:
            self.log_error(f"Auto-save error: {str(e)}")
    
    def exit_game(self):
        reply = QMessageBox.question(self, "Exit", 
                                   "Are you sure you want to exit?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event):
        # Clean up threads
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait(1000)
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.terminate()
            self.tts_worker.wait(1000)
        
        # Final auto-save
        self.auto_save()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Text Adventure")
    app.setApplicationVersion("2.0")
    app.setStyle('Fusion')  # Consistent style across platforms
    
    # Create necessary directories
    Path(CONFIG["SAVE_DIR"]).mkdir(exist_ok=True)
    
    window = AdventureGameGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()