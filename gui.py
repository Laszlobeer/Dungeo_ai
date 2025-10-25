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
                             QSlider, QSpinBox, QDoubleSpinBox, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QRegExp, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QTextCharFormat, QSyntaxHighlighter, QRegExpValidator, QIcon, QPainter, QLinearGradient

# Configuration
CONFIG = {
    "ALLTALK_API_URL": "http://localhost:7851/api/tts-generate",
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    "LOG_FILE": "error_log.txt",
    "SAVE_DIR": "saves",
    "CONFIG_FILE": "config.ini",
    "AUTO_SAVE_INTERVAL": 300000,
}

# Theme configurations
THEMES = {
    "Deep Space": {
        "primary": "#667eea",
        "secondary": "#764ba2", 
        "accent": "#f093fb",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0c0c2e, stop:0.5 #1a1a3e, stop:1 #2d1b69)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(20, 20, 46, 0.9), stop:1 rgba(30, 25, 65, 0.9))",
        "card_bg": "rgba(255,255,255,0.08)",
        "border": "rgba(102, 126, 234, 0.4)"
    },
    "Cyber Neon": {
        "primary": "#00f5ff",
        "secondary": "#ff00ff",
        "accent": "#00ff87", 
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a12, stop:0.5 #1a1a2e, stop:1 #16213e)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(10, 15, 35, 0.9), stop:1 rgba(20, 25, 55, 0.9))",
        "card_bg": "rgba(0, 245, 255, 0.1)",
        "border": "rgba(0, 245, 255, 0.3)"
    },
    "Forest Mystic": {
        "primary": "#4ecdc4",
        "secondary": "#44a08d",
        "accent": "#ff6b6b",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f2b1d, stop:0.5 #1a3d2c, stop:1 #2d5a4a)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(20, 40, 30, 0.9), stop:1 rgba(40, 70, 55, 0.9))",
        "card_bg": "rgba(78, 205, 196, 0.1)",
        "border": "rgba(78, 205, 196, 0.4)"
    },
    "Crimson Night": {
        "primary": "#ff6b6b",
        "secondary": "#c6426e", 
        "accent": "#ffd93d",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c0b1a, stop:0.5 #4a142d, stop:1 #6d1f41)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 15, 25, 0.9), stop:1 rgba(80, 25, 45, 0.9))",
        "card_bg": "rgba(255, 107, 107, 0.1)",
        "border": "rgba(255, 107, 107, 0.4)"
    },
    "Golden Sands": {
        "primary": "#f7b733",
        "secondary": "#fc4a1a",
        "accent": "#4abdac",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c1a0b, stop:0.5 #4a2e14, stop:1 #6d451f)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 35, 15, 0.9), stop:1 rgba(80, 55, 25, 0.9))",
        "card_bg": "rgba(247, 183, 51, 0.1)",
        "border": "rgba(247, 183, 51, 0.4)"
    },
    "Arctic Frost": {
        "primary": "#74ebd5",
        "secondary": "#9face6",
        "accent": "#ff7e5f",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b2c2c, stop:0.5 #144a4a, stop:1 #1f6d6d)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 40, 40, 0.9), stop:1 rgba(25, 70, 70, 0.9))",
        "card_bg": "rgba(116, 235, 213, 0.1)",
        "border": "rgba(116, 235, 213, 0.4)"
    },
    "Purple Dream": {
        "primary": "#da22ff",
        "secondary": "#9733ee",
        "accent": "#38ef7d",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a0b2c, stop:0.5 #2e144a, stop:1 #451f6d)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 15, 50, 0.9), stop:1 rgba(55, 25, 85, 0.9))",
        "card_bg": "rgba(218, 34, 255, 0.1)",
        "border": "rgba(218, 34, 255, 0.4)"
    },
    "Ocean Depth": {
        "primary": "#2193b0",
        "secondary": "#6dd5ed",
        "accent": "#cc2b5e",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1a2c, stop:0.5 #142e4a, stop:1 #1f456d)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 25, 40, 0.9), stop:1 rgba(25, 45, 70, 0.9))",
        "card_bg": "rgba(33, 147, 176, 0.1)",
        "border": "rgba(33, 147, 176, 0.4)"
    },
    "Volcanic Fire": {
        "primary": "#ff416c",
        "secondary": "#ff4b2b",
        "accent": "#ffc371",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c150b, stop:0.5 #4a2414, stop:1 #6d341f)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 25, 15, 0.9), stop:1 rgba(80, 40, 25, 0.9))",
        "card_bg": "rgba(255, 65, 108, 0.1)",
        "border": "rgba(255, 65, 108, 0.4)"
    },
    "Emerald Forest": {
        "primary": "#38ef7d",
        "secondary": "#11998e",
        "accent": "#ff4b1f",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b2c15, stop:0.5 #144a24, stop:1 #1f6d34)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 40, 25, 0.9), stop:1 rgba(25, 70, 45, 0.9))",
        "card_bg": "rgba(56, 239, 125, 0.1)",
        "border": "rgba(56, 239, 125, 0.4)"
    },
    "Royal Purple": {
        "primary": "#8e2de2",
        "secondary": "#4a00e0",
        "accent": "#ff6b6b",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #150b2c, stop:0.5 #24144a, stop:1 #341f6d)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(25, 15, 50, 0.9), stop:1 rgba(45, 25, 85, 0.9))",
        "card_bg": "rgba(142, 45, 226, 0.1)",
        "border": "rgba(142, 45, 226, 0.4)"
    },
    "Sunset Glow": {
        "primary": "#ff6a00",
        "secondary": "#ee0979",
        "accent": "#2575fc",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c1a0b, stop:0.5 #4a2e14, stop:1 #6d451f)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 30, 15, 0.9), stop:1 rgba(80, 50, 25, 0.9))",
        "card_bg": "rgba(255, 106, 0, 0.1)",
        "border": "rgba(255, 106, 0, 0.4)"
    },
    "Mystic Twilight": {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "accent": "#f093fb",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 30, 46, 0.9), stop:1 rgba(25, 25, 35, 0.9))",
        "card_bg": "rgba(255,255,255,0.08)",
        "border": "rgba(255,255,255,0.2)"
    },
    "Steel Blue": {
        "primary": "#4facfe",
        "secondary": "#00f2fe",
        "accent": "#ff9a8b",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b1a2c, stop:0.5 #142e4a, stop:1 #1f456d)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 25, 40, 0.9), stop:1 rgba(25, 45, 70, 0.9))",
        "card_bg": "rgba(79, 172, 254, 0.1)",
        "border": "rgba(79, 172, 254, 0.4)"
    },
    "Rose Gold": {
        "primary": "#ffafbd",
        "secondary": "#ffc3a0",
        "accent": "#6a85b6",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c0b1a, stop:0.5 #4a142d, stop:1 #6d1f41)",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(50, 20, 30, 0.9), stop:1 rgba(80, 35, 50, 0.9))",
        "card_bg": "rgba(255, 175, 189, 0.1)",
        "border": "rgba(255, 175, 189, 0.4)"
    }
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

class VoiceScanner(QThread):
    voices_ready = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        """Scan for available voices by checking common voice directories"""
        voices = []
        
        # Common AllTalk voice directories to check
        voice_directories = [
            Path.home() / "alltalk_tts" / "voices",
            Path.cwd() / "voices",
            Path("/opt/alltalk_tts/voices"),
            Path("C:/Program Files/alltalk_tts/voices")
        ]
        
        # Common voice file extensions
        voice_extensions = ['.wav', '.mp3', '.ogg', '.flac']
        
        # Default voices that are commonly available
        default_voices = [
            "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav",
            "MaleBritishAccent.wav",
            "FemaleAmericanAccent.wav",
            "MaleAmericanAccent.wav",
            "narrator.wav"
        ]
        
        # First, add default voices
        for voice in default_voices:
            voices.append(voice)
        
        # Scan directories for additional voices
        for directory in voice_directories:
            if directory.exists():
                try:
                    for file_path in directory.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in voice_extensions:
                            voices.append(file_path.name)
                except Exception as e:
                    print(f"Error scanning directory {directory}: {e}")
        
        # Remove duplicates and sort
        voices = sorted(list(set(voices)))
        self.voices_ready.emit(voices)

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def setVariant(self, variant="primary", theme=None):
        if not theme:
            theme = THEMES["Mystic Twilight"]
            
        if variant == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 20px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.adjust_color(theme['primary'], -20)}, stop:1 {self.adjust_color(theme['secondary'], -20)});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.adjust_color(theme['primary'], -40)}, stop:1 {self.adjust_color(theme['secondary'], -40)});
                }}
                QPushButton:disabled {{
                    background: #cccccc;
                    color: #666666;
                }}
            """)
        elif variant == "secondary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme['accent']}, stop:1 {self.adjust_color(theme['accent'], -30)});
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-height: 18px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.adjust_color(theme['accent'], -10)}, stop:1 {self.adjust_color(theme['accent'], -40)});
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {self.adjust_color(theme['accent'], -20)}, stop:1 {self.adjust_color(theme['accent'], -50)});
                }}
            """)
        elif variant == "danger":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff6b6b, stop:1 #ee5a52);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-height: 18px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff5252, stop:1 #e04a42);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff3838, stop:1 #d23a32);
                }}
            """)
    
    def adjust_color(self, color, amount):
        """Adjust color brightness by amount"""
        if color.startswith('#'):
            r = max(0, min(255, int(color[1:3], 16) + amount))
            g = max(0, min(255, int(color[3:5], 16) + amount))
            b = max(0, min(255, int(color[5:7], 16) + amount))
            return f"#{r:02x}{g:02x}{b:02x}"
        return color

class ModernGroupBox(QGroupBox):
    def __init__(self, title, parent=None, theme=None):
        super().__init__(title, parent)
        if not theme:
            theme = THEMES["Mystic Twilight"]
            
        self.setStyleSheet(f"""
            QGroupBox {{
                background: {theme['card_bg']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {theme['primary']};
                font-weight: bold;
                font-size: 13px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        if not theme:
            theme = THEMES["Mystic Twilight"]
            
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {theme['border']};
                border-radius: 10px;
                text-align: center;
                color: white;
                font-weight: bold;
                background: rgba(0,0,0,0.3);
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                border-radius: 8px;
            }}
        """)

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        if not theme:
            theme = THEMES["Mystic Twilight"]
            
        self.highlighting_rules = []
        
        # Player text format
        player_format = QTextCharFormat()
        player_format.setForeground(QColor(theme['primary']))
        player_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((QRegExp("You:.*"), player_format))
        
        # DM text format
        dm_format = QTextCharFormat()
        dm_format.setForeground(QColor(theme['accent']))
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

class ThemePreviewWidget(QWidget):
    def __init__(self, theme_name, theme_data, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.theme_data = theme_data
        self.setFixedSize(120, 80)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw theme preview
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(self.theme_data['primary']))
        gradient.setColorAt(1, QColor(self.theme_data['secondary']))
        
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # Draw theme name
        painter.setPen(QColor('white'))
        painter.drawText(self.rect(), Qt.AlignCenter, self.theme_name)

class ModernSetupDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.current_theme = self.settings.value("theme", "Mystic Twilight")
        self.setWindowTitle("🎮 Adventure Setup - Choose Your Destiny")
        self.setModal(True)
        self.setMinimumWidth(900)
        self.setMinimumHeight(800)
        
        # Voice scanner
        self.voice_scanner = VoiceScanner()
        self.voice_scanner.voices_ready.connect(self.on_voices_ready)
        
        self.init_ui()
        self.load_settings()
        self.apply_theme(THEMES[self.current_theme])
        
        # Start voice scanning
        self.voice_scanner.start()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("🚀 Adventure Setup")
        header_label.setObjectName("title")
        header_label.setStyleSheet("""
            QLabel#title {
                color: white;
                font-size: 28px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
                padding: 10px;
            }
        """)
        subtitle_label = QLabel("Craft your unique story - choose your world and destiny")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setStyleSheet("""
            QLabel#subtitle {
                color: #a0a0ff;
                font-size: 14px;
                qproperty-alignment: AlignCenter;
                padding-bottom: 10px;
            }
        """)
        
        layout.addWidget(header_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        
        tab_widget = QTabWidget()
        
        # Basic Settings Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setSpacing(25)
        basic_layout.setContentsMargins(25, 25, 25, 25)
        
        # Theme selection
        theme_group = ModernGroupBox("🎨 Visual Theme")
        theme_layout = QVBoxLayout()
        
        theme_select_layout = QHBoxLayout()
        theme_select_layout.addWidget(QLabel("Select Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_select_layout.addWidget(self.theme_combo)
        theme_select_layout.addStretch()
        
        # Theme preview area
        self.theme_preview = QLabel()
        self.theme_preview.setFixedHeight(100)
        self.theme_preview.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                border: 2px solid rgba(255,255,255,0.3);
            }
        """)
        
        theme_layout.addLayout(theme_select_layout)
        theme_layout.addWidget(QLabel("Preview:"))
        theme_layout.addWidget(self.theme_preview)
        theme_group.setLayout(theme_layout)
        basic_layout.addWidget(theme_group)
        
        # Model selection
        model_group = ModernGroupBox("🤖 AI Model Configuration")
        model_layout = QVBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        model_layout.addWidget(QLabel("Select AI Model:"))
        model_layout.addWidget(self.model_combo)
        self.refresh_models_button = ModernButton("🔄 Refresh Models")
        self.refresh_models_button.setVariant("secondary")
        self.refresh_models_button.clicked.connect(self.load_models)
        model_layout.addWidget(self.refresh_models_button)
        model_group.setLayout(model_layout)
        basic_layout.addWidget(model_group)
        
        # Genre and Role selection
        genre_role_layout = QHBoxLayout()
        
        genre_group = ModernGroupBox("🌍 Adventure Genre")
        genre_layout = QVBoxLayout()
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(ROLE_STARTERS.keys())
        self.genre_combo.currentTextChanged.connect(self.genre_changed)
        genre_layout.addWidget(QLabel("Select Genre:"))
        genre_layout.addWidget(self.genre_combo)
        
        self.genre_desc = QLabel()
        self.genre_desc.setWordWrap(True)
        self.genre_desc.setStyleSheet("""
            background: rgba(255,255,255,0.08); 
            color: #e0e0e0; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            line-height: 1.4;
        """)
        self.genre_desc.setMinimumHeight(80)
        self.genre_desc.setMaximumHeight(100)
        genre_layout.addWidget(self.genre_desc)
        genre_group.setLayout(genre_layout)
        genre_role_layout.addWidget(genre_group)
        
        role_group = ModernGroupBox("👤 Character Role")
        role_layout = QVBoxLayout()
        self.role_combo = QComboBox()
        role_layout.addWidget(QLabel("Select Role:"))
        role_layout.addWidget(self.role_combo)
        
        self.role_desc = QLabel()
        self.role_desc.setWordWrap(True)
        self.role_desc.setStyleSheet("""
            background: rgba(255,255,255,0.08); 
            color: #e0e0e0; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            line-height: 1.4;
        """)
        self.role_desc.setMinimumHeight(80)
        self.role_desc.setMaximumHeight(100)
        role_layout.addWidget(self.role_desc)
        role_group.setLayout(role_layout)
        genre_role_layout.addWidget(role_group)
        
        basic_layout.addLayout(genre_role_layout)
        
        # Character details
        char_group = ModernGroupBox("📝 Character Details")
        char_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter your character's name...")
        char_layout.addWidget(QLabel("Character Name:"))
        char_layout.addWidget(self.name_edit)
        char_group.setLayout(char_layout)
        basic_layout.addWidget(char_group)
        
        basic_layout.addStretch()
        tab_widget.addTab(basic_tab, "🎯 Basic Settings")
        
        # Advanced Settings Tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setSpacing(25)
        advanced_layout.setContentsMargins(25, 25, 25, 25)
        
        # TTS Settings
        tts_group = ModernGroupBox("🔊 Voice Settings")
        tts_layout = QVBoxLayout()
        self.tts_enabled = QCheckBox("Enable Text-to-Speech")
        self.tts_enabled.setChecked(True)
        tts_layout.addWidget(self.tts_enabled)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice Style:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItem("🔍 Scanning for voices...")
        self.refresh_voices_button = ModernButton("🔄 Refresh Voices")
        self.refresh_voices_button.setVariant("secondary")
        self.refresh_voices_button.clicked.connect(self.refresh_voices)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addWidget(self.refresh_voices_button)
        tts_layout.addLayout(voice_layout)
        tts_group.setLayout(tts_layout)
        advanced_layout.addWidget(tts_group)
        
        # AI Settings
        ai_group = ModernGroupBox("⚡ AI Behavior")
        ai_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Creativity Level:"))
        self.temp_label = QLabel("0.7")
        self.temp_label.setStyleSheet("color: #a0a0ff; font-weight: bold;")
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_slider.valueChanged.connect(
            lambda v: self.temp_label.setText(f"{v/100:.2f}")
        )
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        ai_layout.addLayout(temp_layout)
        
        ai_layout.addWidget(QLabel("Higher = more creative, Lower = more focused"))
        
        max_tokens_layout = QHBoxLayout()
        max_tokens_layout.addWidget(QLabel("Response Length:"))
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
        tab_widget.addTab(advanced_tab, "⚙️ Advanced Settings")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = ModernButton("❌ Cancel")
        self.cancel_button.setVariant("danger")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = ModernButton("🚀 Start Adventure!")
        self.ok_button.setVariant("primary")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Initialize
        self.genre_changed(self.genre_combo.currentText())
        self.load_models()
        self.theme_changed(self.current_theme)
        
        # Add animations
        self.setup_animations()
    
    def setup_animations(self):
        # Simple fade-in animation for the dialog
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def theme_changed(self, theme_name):
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        self.apply_theme(theme)
        
        # Update theme preview
        self.theme_preview.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                border-radius: 10px;
                border: 2px solid {theme['border']};
                color: white;
                font-weight: bold;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            }}
        """)
        self.theme_preview.setText(f"{theme_name}\nTheme Preview")
    
    def apply_theme(self, theme):
        """Apply the selected theme to the dialog"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {theme['background']};
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: #e0e0e0;
                font-size: 12px;
            }}
            QLabel#title {{
                color: white;
                font-size: 24px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }}
            QLabel#subtitle {{
                color: {theme['primary']};
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }}
            QComboBox {{
                background: rgba(255,255,255,0.1);
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 12px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border: 2px solid {theme['primary']};
            }}
            QComboBox QAbstractItemView {{
                background: #2d3748;
                border: 1px solid #4a5568;
                color: white;
                selection-background-color: {theme['primary']};
            }}
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 13px;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['primary']};
            }}
            QSpinBox {{
                background: rgba(255,255,255,0.1);
                border: 2px solid {theme['border']};
                border-radius: 8px;
                padding: 8px;
                color: white;
                min-height: 20px;
            }}
            QCheckBox {{
                color: white;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {theme['border']};
                border-radius: 4px;
                background: rgba(255,255,255,0.1);
            }}
            QCheckBox::indicator:checked {{
                background: {theme['primary']};
                border: 2px solid {theme['primary']};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {theme['border']};
                height: 6px;
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                border: 2px solid rgba(255,255,255,0.8);
                width: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme['border']};
                border-radius: 10px;
                background: rgba(255,255,255,0.05);
            }}
            QTabBar::tab {{
                background: rgba(255,255,255,0.1);
                color: #cccccc;
                padding: 12px 20px;
                margin: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background: rgba(102, 126, 234, 0.3);
                color: white;
                border-bottom: 2px solid {theme['primary']};
            }}
            QTabBar::tab:hover {{
                background: rgba(255,255,255,0.2);
            }}
        """)
        
        # Update buttons with new theme
        self.ok_button.setVariant("primary", theme)
        self.cancel_button.setVariant("danger", theme)
        self.refresh_models_button.setVariant("secondary", theme)
        self.refresh_voices_button.setVariant("secondary", theme)
    
    def on_voices_ready(self, voices):
        """Update voice combo box with scanned voices"""
        self.voice_combo.clear()
        if voices:
            for voice in voices:
                # Add emoji based on voice type
                emoji = "🎭"
                if "female" in voice.lower():
                    emoji = "👩"
                elif "male" in voice.lower():
                    emoji = "👨"
                elif "narrator" in voice.lower():
                    emoji = "📖"
                self.voice_combo.addItem(f"{emoji} {voice}")
        else:
            self.voice_combo.addItem("❌ No voices found")
    
    def refresh_voices(self):
        """Refresh available voices"""
        self.voice_combo.clear()
        self.voice_combo.addItem("🔍 Scanning for voices...")
        self.voice_scanner.start()
    
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
        self.theme_combo.setCurrentText(self.settings.value("theme", "Mystic Twilight"))
        
        # Fix for voice setting type conversion
        voice_value = self.settings.value("voice", 0)
        try:
            # Try to convert to int, handle both string and int types
            if isinstance(voice_value, str):
                voice_index = int(voice_value)
            else:
                voice_index = int(voice_value) if voice_value is not None else 0
        except (ValueError, TypeError):
            voice_index = 0
        
        # Voice index will be set after voices are loaded
    
    def get_selections(self):
        # Extract voice filename from the combo box display text
        voice_text = self.voice_combo.currentText()
        voice_file = voice_text.split(" ", 1)[-1] if " " in voice_text else voice_text
        
        return {
            "model": self.model_combo.currentText(),
            "genre": self.genre_combo.currentText(),
            "role": self.role_combo.currentText(),
            "character_name": self.name_edit.text(),
            "tts_enabled": self.tts_enabled.isChecked(),
            "voice": voice_file,
            "temperature": self.temp_slider.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value(),
            "theme": self.current_theme
        }

class AdventureGameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(CONFIG["CONFIG_FILE"], QSettings.IniFormat)
        self.current_theme = self.settings.value("theme", "Mystic Twilight")
        self.setWindowTitle("✨ AI Dungeon Master - Interactive Storytelling")
        self.setGeometry(100, 100, 1200, 900)
        
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
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("🎭 AI Dungeon Master")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        subtitle_label = QLabel("Your interactive storytelling companion")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #a0a0ff;
                font-size: 14px;
                font-style: italic;
            }
        """)
        
        self.theme_button = ModernButton("🎨 Change Theme")
        self.theme_button.setVariant("secondary")
        self.theme_button.clicked.connect(self.change_theme)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(self.theme_button)
        
        layout.addWidget(header_widget)
        
        # Game text area with syntax highlighting
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Segoe UI", 12))
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background: {THEMES[self.current_theme]['text_area']};
                color: #e0e0e0;
                border: 2px solid {THEMES[self.current_theme]['border']};
                border-radius: 15px;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                selection-background-color: rgba(102, 126, 234, 0.3);
            }}
        """)
        self.highlighter = SyntaxHighlighter(self.text_area.document(), THEMES[self.current_theme])
        
        # Add shadow to text area
        text_shadow = QGraphicsDropShadowEffect()
        text_shadow.setBlurRadius(25)
        text_shadow.setColor(QColor(0, 0, 0, 80))
        text_shadow.setOffset(0, 8)
        self.text_area.setGraphicsEffect(text_shadow)
        
        # Progress bar
        self.progress_bar = ModernProgressBar(self, THEMES[self.current_theme])
        self.progress_bar.setVisible(False)
        
        # Status bar
        self.status_label = QLabel("🟢 Ready to begin your adventure")
        self.status_label.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.1);
                color: #a0a0ff;
                padding: 8px 15px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.2);
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("💭 Describe your action or type /help for commands...")
        self.input_field.returnPressed.connect(self.send_input)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                color: white;
                border: 2px solid {THEMES[self.current_theme]['border']};
                border-radius: 12px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {THEMES[self.current_theme]['primary']};
                background: rgba(255,255,255,0.15);
            }}
            QLineEdit:disabled {{
                background: rgba(255,255,255,0.05);
                color: #888888;
            }}
        """)
        
        input_shadow = QGraphicsDropShadowEffect()
        input_shadow.setBlurRadius(15)
        input_shadow.setColor(QColor(0, 0, 0, 60))
        input_shadow.setOffset(0, 4)
        self.input_field.setGraphicsEffect(input_shadow)
        
        self.send_button = ModernButton("🚀 Send")
        self.send_button.setVariant("primary", THEMES[self.current_theme])
        self.send_button.clicked.connect(self.send_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Control buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self.help_button = ModernButton("❓ Help")
        self.help_button.setVariant("secondary", THEMES[self.current_theme])
        self.help_button.clicked.connect(self.show_help)
        
        self.redo_button = ModernButton("🔁 Redo")
        self.redo_button.setVariant("secondary", THEMES[self.current_theme])
        self.redo_button.clicked.connect(self.redo_last)
        
        self.save_button = ModernButton("💾 Save")
        self.save_button.setVariant("secondary", THEMES[self.current_theme])
        self.save_button.clicked.connect(self.save_adventure)
        
        self.load_button = ModernButton("📂 Load")
        self.load_button.setVariant("secondary", THEMES[self.current_theme])
        self.load_button.clicked.connect(self.load_adventure)
        
        self.settings_button = ModernButton("⚙️ Settings")
        self.settings_button.setVariant("secondary", THEMES[self.current_theme])
        self.settings_button.clicked.connect(self.show_settings)
        
        self.exit_button = ModernButton("⏹️ Exit")
        self.exit_button.setVariant("danger", THEMES[self.current_theme])
        self.exit_button.clicked.connect(self.exit_game)
        
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.redo_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.exit_button)
        
        layout.addWidget(self.text_area, 1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(input_widget)
        layout.addWidget(button_widget)
        
        self.apply_theme(THEMES[self.current_theme])
        
    def apply_theme(self, theme):
        """Apply the selected theme to the entire application"""
        # Apply palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Apply stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {theme['background']};
            }}
            QMessageBox {{
                background: #2d2d2d;
                color: white;
            }}
            QMessageBox QLabel {{
                color: white;
            }}
            QMessageBox QPushButton {{
                background: #404040;
                color: white;
                border: 1px solid #555;
                padding: 5px 15px;
                border-radius: 4px;
            }}
            QMessageBox QPushButton:hover {{
                background: #505050;
            }}
        """)
        
        # Update specific widgets
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background: {theme['text_area']};
                color: #e0e0e0;
                border: 2px solid {theme['border']};
                border-radius: 15px;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                selection-background-color: rgba(102, 126, 234, 0.3);
            }}
        """)
        
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                color: white;
                border: 2px solid {theme['border']};
                border-radius: 12px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['primary']};
                background: rgba(255,255,255,0.15);
            }}
            QLineEdit:disabled {{
                background: rgba(255,255,255,0.05);
                color: #888888;
            }}
        """)
        
        # Update buttons
        self.send_button.setVariant("primary", theme)
        self.help_button.setVariant("secondary", theme)
        self.redo_button.setVariant("secondary", theme)
        self.save_button.setVariant("secondary", theme)
        self.load_button.setVariant("secondary", theme)
        self.settings_button.setVariant("secondary", theme)
        self.exit_button.setVariant("danger", theme)
        self.theme_button.setVariant("secondary", theme)
        
        # Update progress bar
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {theme['border']};
                border-radius: 10px;
                text-align: center;
                color: white;
                font-weight: bold;
                background: rgba(0,0,0,0.3);
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {theme['primary']}, stop:1 {theme['secondary']});
                border-radius: 8px;
            }}
        """)
        
        # Update highlighter
        self.highlighter = SyntaxHighlighter(self.text_area.document(), theme)
    
    def change_theme(self):
        """Show theme selection dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🎨 Select Theme")
        dialog.setModal(True)
        dialog.setFixedSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Theme grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        container = QWidget()
        grid_layout = QVBoxLayout(container)
        
        for theme_name, theme_data in THEMES.items():
            theme_widget = QWidget()
            theme_widget_layout = QHBoxLayout(theme_widget)
            theme_widget_layout.setContentsMargins(10, 5, 10, 5)
            
            preview = ThemePreviewWidget(theme_name, theme_data)
            
            name_label = QLabel(theme_name)
            name_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            
            if theme_name == self.current_theme:
                current_indicator = QLabel("✅ Current")
                current_indicator.setStyleSheet("color: #4FC3F7; font-weight: bold;")
            else:
                current_indicator = QLabel("")
            
            theme_widget_layout.addWidget(preview)
            theme_widget_layout.addWidget(name_label)
            theme_widget_layout.addStretch()
            theme_widget_layout.addWidget(current_indicator)
            
            # Make the theme widget clickable
            theme_widget.setCursor(Qt.PointingHandCursor)
            theme_widget.mousePressEvent = lambda e, t=theme_name: self.select_theme(t, dialog)
            
            grid_layout.addWidget(theme_widget)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = ModernButton("Close")
        close_btn.setVariant("primary", THEMES[self.current_theme])
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def select_theme(self, theme_name, dialog):
        """Select and apply a new theme"""
        self.current_theme = theme_name
        self.settings.setValue("theme", theme_name)
        self.apply_theme(THEMES[theme_name])
        dialog.close()
        
        # Update the conversation with theme change notification
        if self.adventure_started:
            self.append_text(f"🎨 <font color='{THEMES[theme_name]['primary']}'>Theme changed to: {theme_name}</font><br>")
    
    def show_setup_dialog(self):
        dialog = ModernSetupDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            selections = dialog.get_selections()
            self.apply_settings(selections)
            self.start_adventure()
        else:
            self.close()
    
    def show_settings(self):
        dialog = ModernSetupDialog(self.settings, self)
        if dialog.exec_() == QDialog.Accepted:
            selections = dialog.get_selections()
            self.apply_settings(selections)
            self.append_text("🎛️ <font color='#FFB74D'>Settings updated.</font><br>")
    
    def apply_settings(self, selections):
        self.ollama_model = selections["model"]
        self.selected_genre = selections["genre"]
        self.selected_role = selections["role"]
        self.character_name = selections["character_name"]
        self.tts_enabled = selections["tts_enabled"]
        self.selected_voice = selections["voice"]
        self.temperature = selections["temperature"]
        self.max_tokens = selections["max_tokens"]
        
        # Apply theme if changed
        if selections["theme"] != self.current_theme:
            self.current_theme = selections["theme"]
            self.apply_theme(THEMES[self.current_theme])
        
        # Save settings
        self.settings.setValue("model", self.ollama_model)
        self.settings.setValue("genre", self.selected_genre)
        self.settings.setValue("role", self.selected_role)
        self.settings.setValue("character_name", self.character_name)
        self.settings.setValue("tts_enabled", self.tts_enabled)
        self.settings.setValue("theme", self.current_theme)
        
        # Save voice as string filename
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
                                       "📂 An auto-saved adventure exists. Load it?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.load_save_file(auto_save_path):
                    return
        
        # Start new adventure
        starter = ROLE_STARTERS[self.selected_genre][self.selected_role]
        self.append_text(f"<font color='#FFA500'><b>🌟 Adventure Start: {self.character_name} the {self.selected_role} 🌟</b></font><br><br>")
        self.append_text(f"<b>🎬 Starting scenario:</b> {starter}<br><br>")
        self.append_text("<font color='#4FC3F7'>💡 Type <b>/help</b> for available commands</font><br><br>")
        
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
        self.append_text(f"<font color='{THEMES[self.current_theme]['primary']}'><b>🎭 You:</b> {user_input}</font><br>")
        
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
            self.append_text("🧹 <font color='#FFA500'>Chat cleared.</font><br>")
        elif cmd.startswith('/model'):
            parts = cmd.split()
            if len(parts) > 1:
                self.ollama_model = parts[1]
                self.append_text(f"🔄 <font color='#FFA500'>Model changed to: {self.ollama_model}</font><br>")
            else:
                QMessageBox.information(self, "Current Model", f"🤖 Using model: {self.ollama_model}")
        elif cmd == '/tts':
            self.tts_enabled = not self.tts_enabled
            status = "enabled" if self.tts_enabled else "disabled"
            self.append_text(f"🔊 <font color='#FFA500'>Text-to-speech {status}.</font><br>")
        elif cmd == '/voices':
            self.append_text(f"🔊 <font color='#FFA500'>Current voice: {self.selected_voice}</font><br>")
        elif cmd == '/status':
            self.show_status()
        elif cmd == '/export':
            self.export_conversation()
        elif cmd == '/theme':
            self.change_theme()
        else:
            self.append_text(f"❌ <font color='#FF6B6B'>Unknown command: {command}</font><br>")
    
    def show_status(self):
        """Show current game status and settings"""
        status_text = f"""
<h3>🎮 Current Adventure Status</h3>
<p><b>Character:</b> {self.character_name} the {self.selected_role}<br>
<b>Genre:</b> {self.selected_genre}<br>
<b>Theme:</b> {self.current_theme}<br>
<b>AI Model:</b> {self.ollama_model}<br>
<b>TTS:</b> {'Enabled' if self.tts_enabled else 'Disabled'}<br>
<b>Voice:</b> {self.selected_voice}<br>
<b>Temperature:</b> {self.temperature}<br>
<b>Max Tokens:</b> {self.max_tokens}</p>
<p><b>Conversation Length:</b> {len(self.conversation.split())} words</p>
"""
        QMessageBox.information(self, "Adventure Status", status_text)
    
    def export_conversation(self):
        """Export conversation to a text file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Conversation", str(Path.home() / f"{self.character_name}_adventure.txt"), 
                "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Adventure Export: {self.character_name} the {self.selected_role}\n")
                    f.write(f"Genre: {self.selected_genre}\n")
                    f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(self.conversation)
                
                self.append_text(f"📤 <font color='#FFA500'>Conversation exported to: {file_path}</font><br>")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"❌ Error exporting conversation: {str(e)}")
    
    def get_ai_response(self, prompt):
        self.status_label.setText("🤔 Generating response...")
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
        self.status_label.setText("🟢 Ready for your next action")
        
        self.append_text(f"<font color='{THEMES[self.current_theme]['accent']}'><b>🎮 Dungeon Master:</b> {response}</font><br><br>")
        self.conversation += f"\nDungeon Master: {response}"
        self.last_ai_reply = response
        self.speak_text(response)
        
        # Auto-save after each response
        self.auto_save()
    
    def handle_ai_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.set_ui_enabled(True)
        self.status_label.setText("🔴 Error occurred")
        self.log_error(f"AI Error: {error_msg}")
        QMessageBox.warning(self, "AI Error", f"❌ An error occurred: {error_msg}")
    
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
        self.theme_button.setEnabled(enabled)
    
    def show_help(self):
        help_text = """
<h3>🎮 Available Commands:</h3>
<ul>
<li><b>/? or /help</b> - Show this help message</li>
<li><b>/redo</b> - Repeat last AI response</li>
<li><b>/save</b> - Save adventure</li>
<li><b>/load</b> - Load adventure</li>
<li><b>/settings</b> - Change game settings</li>
<li><b>/theme</b> - Change visual theme</li>
<li><b>/clear</b> - Clear chat</li>
<li><b>/model [name]</b> - Change AI model</li>
<li><b>/tts</b> - Toggle text-to-speech</li>
<li><b>/voices</b> - Show current voice</li>
<li><b>/status</b> - Show current game status</li>
<li><b>/export</b> - Export conversation to file</li>
<li><b>/exit</b> - Exit game</li>
</ul>
<h3>🎯 Gameplay Tips:</h3>
<p>Describe your actions naturally. The AI will respond with consequences and story developments.<br>
Be creative and immersive in your descriptions!</p>
"""
        QMessageBox.information(self, "Help Guide", help_text)
    
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
            QMessageBox.warning(self, "Redo", "🔄 Nothing to redo.")
    
    def save_adventure(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = Path(CONFIG["SAVE_DIR"]) / f"adventure_{timestamp}.txt"
            
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.conversation)
            
            self.append_text(f"💾 <font color='#FFA500'>Adventure saved to: {save_path}</font><br>")
        except Exception as e:
            error_msg = f"Error saving adventure: {str(e)}"
            self.log_error(error_msg)
            QMessageBox.warning(self, "Save Error", "❌ Error saving adventure.")
    
    def load_adventure(self):
        try:
            save_files = list(Path(CONFIG["SAVE_DIR"]).glob("adventure_*.txt"))
            if not save_files:
                QMessageBox.warning(self, "Load Error", "📂 No saved adventures found.")
                return
            
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Adventure", str(CONFIG["SAVE_DIR"]), "Text Files (*.txt)"
            )
            
            if file_path and self.load_save_file(Path(file_path)):
                self.append_text("📂 <font color='#FFA500'>Adventure loaded successfully.</font><br>")
                
        except Exception as e:
            error_msg = f"Error loading adventure: {str(e)}"
            self.log_error(error_msg)
            QMessageBox.warning(self, "Load Error", "❌ Error loading adventure.")
    
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
        reply = QMessageBox.question(self, "Exit Adventure", 
                                   "🚪 Are you sure you want to exit your adventure?",
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
    app.setApplicationName("AI Dungeon Master")
    app.setApplicationVersion("3.0")
    app.setStyle('Fusion')
    
    # Set modern font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create necessary directories
    Path(CONFIG["SAVE_DIR"]).mkdir(exist_ok=True)
    
    window = AdventureGameGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()