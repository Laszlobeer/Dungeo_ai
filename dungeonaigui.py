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
                             QSlider, QSpinBox, QDoubleSpinBox, QGraphicsDropShadowEffect,
                             QSystemTrayIcon, QMenu, QAction, QStyle)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings, QRegExp, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QTextCursor, QPalette, QColor, QTextCharFormat, QSyntaxHighlighter, QRegExpValidator, QIcon, QPainter, QLinearGradient

# Configuration - IMPROVED
CONFIG = {
    "ALLTALK_API_URL": "http://localhost:7851/api/tts-generate",
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    "LOG_FILE": "error_log.txt",
    "SAVE_DIR": "saves",
    "CONFIG_FILE": "config.ini",
    "AUTO_SAVE_INTERVAL": 300000,
    "MAX_CONVERSATION_LENGTH": 10000,  # Prevent memory issues
    "REQUEST_TIMEOUT": 120,
    "MAX_HISTORY_ITEMS": 100,  # Limit conversation history
}

# Theme definitions - ADDED NEW THEMES
THEMES = {
    "Dark Fantasy": {
        "primary": "#8B4513",
        "secondary": "#654321",
        "accent": "#DA8A67",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d1b0f, stop:0.5 #1a1208, stop:1 #0f0a03)",
        "text": "#f5deb3",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 27, 15, 0.9), stop:1 rgba(15, 10, 3, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8B4513, stop:1 #654321)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #A0522D, stop:1 #8B4513)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8B0000, stop:1 #660000)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(139, 69, 19, 0.1), stop:1 rgba(101, 67, 33, 0.05))"
    },
    "Cyber Neon": {
        "primary": "#00ffff",
        "secondary": "#ff00ff",
        "accent": "#00ff00",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a2a, stop:0.5 #1a1a3a, stop:1 #2a2a4a)",
        "text": "#ffffff",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(10, 10, 42, 0.9), stop:1 rgba(42, 42, 74, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00ffff, stop:1 #0088ff)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff00ff, stop:1 #cc00cc)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff0066, stop:1 #cc0055)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 255, 255, 0.1), stop:1 rgba(255, 0, 255, 0.05))"
    },
    "Forest Green": {
        "primary": "#2e8b57",
        "secondary": "#228b22",
        "accent": "#90ee90",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a3c27, stop:0.5 #0f2918, stop:1 #051a0f)",
        "text": "#e8f5e8",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(26, 60, 39, 0.9), stop:1 rgba(5, 26, 15, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2e8b57, stop:1 #1f6b3f)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3cb371, stop:1 #2e8b57)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc143c, stop:1 #b22222)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(46, 139, 87, 0.1), stop:1 rgba(34, 139, 34, 0.05))"
    },
    "Royal Purple": {
        "primary": "#9370db",
        "secondary": "#8a2be2",
        "accent": "#da70d6",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d1b4e, stop:0.5 #1f0f3d, stop:1 #12052c)",
        "text": "#f0e6ff",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 27, 78, 0.9), stop:1 rgba(18, 5, 44, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9370db, stop:1 #7b5cb5)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #8a2be2, stop:1 #6a1fc2)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff1493, stop:1 #cc1180)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(147, 112, 219, 0.1), stop:1 rgba(138, 43, 226, 0.05))"
    },
    "Fire & Brimstone": {
        "primary": "#ff4500",
        "secondary": "#dc143c",
        "accent": "#ff8c00",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a0f0f, stop:0.5 #2a0505, stop:1 #1a0000)",
        "text": "#ffd700",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(74, 15, 15, 0.9), stop:1 rgba(26, 0, 0, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff4500, stop:1 #cc3700)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc143c, stop:1 #b21030)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff0000, stop:1 #cc0000)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 69, 0, 0.1), stop:1 rgba(220, 20, 60, 0.05))"
    },
    "Ocean Deep": {
        "primary": "#1e90ff",
        "secondary": "#00bfff",
        "accent": "#87ceeb",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a2a4a, stop:0.5 #051a35, stop:1 #020c20)",
        "text": "#e6f7ff",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(10, 42, 74, 0.9), stop:1 rgba(2, 12, 32, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #0077e6)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00bfff, stop:1 #0099cc)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ff5252)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 144, 255, 0.1), stop:1 rgba(0, 191, 255, 0.05))"
    },
    "Classic Dark": {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "accent": "#f093fb",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460)",
        "text": "#e0e0e0",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(30, 30, 46, 0.9), stop:1 rgba(25, 25, 35, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #667eea, stop:1 #764ba2)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f093fb, stop:1 #f5576c)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b6b, stop:1 #ee5a52)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.1), stop:1 rgba(255,255,255,0.05))"
    },
    "Midnight Blue": {
        "primary": "#4a6fa5",
        "secondary": "#2e4a76",
        "accent": "#6b93d6",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f1a2f, stop:0.5 #1a2b4a, stop:1 #0a1425)",
        "text": "#e8f4ff",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(15, 26, 47, 0.9), stop:1 rgba(10, 20, 37, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a6fa5, stop:1 #2e4a76)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a7fb5, stop:1 #3e5a86)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d9534f, stop:1 #c9302c)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(74, 111, 165, 0.1), stop:1 rgba(46, 74, 118, 0.05))"
    },
    "Solarized Dark": {
        "primary": "#268bd2",
        "secondary": "#2aa198",
        "accent": "#b58900",
        "background": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #002b36, stop:0.5 #073642, stop:1 #001f27)",
        "text": "#839496",
        "text_area": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 43, 54, 0.9), stop:1 rgba(0, 31, 39, 0.9))",
        "button_primary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #268bd2, stop:1 #1a6da5)",
        "button_secondary": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2aa198, stop:1 #1e8179)",
        "button_danger": "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #dc322f, stop:1 #b02624)",
        "group_box": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(38, 139, 210, 0.1), stop:1 rgba(42, 161, 152, 0.05))"
    }
}

# Role-specific starting scenarios - EXPANDED
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
        "Android": "You're performing system diagnostics on your ship when",
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
    "WW2": {
        "Soldier (American)": "You're storming the beaches of Normandy under heavy German fire when",
        "Soldier (British)": "You're preparing for the D-Day invasion aboard a troop ship when",
        "Soldier (Russian)": "You're defending Stalingrad house by house against the German advance when",
        "Soldier (German)": "You're manning a machine gun nest on the Atlantic Wall when",
        "Soldier (Italian)": "You're retreating through the Italian countryside after the Allied invasion when",
        "Soldier (French)": "You're joining the French Resistance after the fall of Paris when",
        "Soldier (Japanese)": "You're defending a Pacific island against American marines when",
        "Soldier (Canadian)": "You're fighting through the rubble of a French town during the liberation when",
        "Soldier (Australian)": "You're battling Japanese forces in the jungles of New Guinea when",
        "Resistance Fighter": "You're sabotaging German supply lines under cover of darkness when",
        "Spy": "You're transmitting coded messages from occupied territory when",
        "Pilot (RAF)": "You're scrambling to intercept German bombers during the Battle of Britain when",
        "Pilot (Luftwaffe)": "You're flying a bombing mission over England when",
        "Tank Commander": "You're leading a Sherman tank through the Ardennes forest when",
        "Sniper": "You're concealed in a ruined building, watching for enemy movement when",
        "Medic": "You're treating wounded soldiers under fire on the front lines when",
        "Naval Officer": "You're commanding a destroyer in the North Atlantic convoy when",
        "Paratrooper": "You're jumping into enemy territory behind German lines when",
        "Commando": "You're conducting a covert raid on a German occupied facility when"
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
        "Soldier": "You're marching on the frontier when",
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

# Genre descriptions - EXPANDED
GENRE_DESCRIPTIONS = {
    "Fantasy": "You are in a world of magic and medieval fantasy, where dragons soar through the skies and ancient ruins hold forgotten treasures.",
    "Sci-Fi": "You are in the distant future, with advanced technology, space travel, and alien civilizations among the stars.",
    "Cyberpunk": "You are in a dystopian future dominated by megacorporations, where cybernetic enhancements are common and the line between human and machine is blurred.",
    "Post-Apocalyptic": "You are in a world after a catastrophic event, where civilization has collapsed and survivors scavenge among the ruins of the old world.",
    "1880": "You are in the late 19th century during the Industrial Revolution, a time of steam power, early electricity, and social upheaval.",
    "WW1": "You are in the trenches and battlefields of World War I, a brutal conflict that introduced modern warfare to the world.",
    "WW2": "You are in the global conflict of World War II, fighting across Europe, the Pacific, and beyond with modern weaponry and tactics.",
    "1925 New York": "You are in the Roaring Twenties in New York City, a time of jazz, prohibition, organized crime, and economic prosperity.",
    "Roman Empire": "You are in ancient Rome at the height of its power, with gladiators, legions, and political intrigue in the eternal city.",
    "French Revolution": "You are in France during the revolution, a time of upheaval where the monarchy was overthrown and the reign of terror began."
}


# IMPROVED DM system prompt with better guidance
DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master in an unrestricted adventure. Your role is to narrate the consequences of player actions naturally. Follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - Describe ONLY the consequences of the player's action
   - Never perform actions on behalf of the player
   - Consequences must logically follow from the action
   - Narrate consequences naturally within the story flow

2. RESPONSE STYLE:
   - Describe what happens in the world as a result of the player's action
   - Keep responses concise but immersive (2-4 paragraphs)
   - Show, don't tell - demonstrate through description
   - Use sensory details to enhance immersion

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change based on actions
   - Maintain consistency with established world facts

4. PLAYER AGENCY:
   - The player can attempt anything
   - Show realistic results, good or bad
   - Let the world react dynamically
   

Always stay in character as the Dungeon Master. Continue the adventure naturally.
"""

class VoiceScanner(QThread):
    voices_ready = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        """Scan for available voices with better error handling"""
        voices = []
        
        # Common AllTalk voice directories to check
        voice_directories = [
            Path.home() / "alltalk_tts" / "voices",
            Path.cwd() / "voices",
            Path("/opt/alltalk_tts/voices"),
            Path("C:/Program Files/alltalk_tts/voices"),
            Path("./alltalk_tts/voices"),  # NEW: Added current directory
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
        
        # Scan directories for additional voices with better error handling
        for directory in voice_directories:
            if directory.exists():
                try:
                    for file_path in directory.iterdir():
                        if file_path.is_file() and file_path.suffix.lower() in voice_extensions:
                            voices.append(file_path.name)
                except (PermissionError, OSError) as e:
                    print(f"Permission error scanning {directory}: {e}")
                except Exception as e:
                    print(f"Error scanning directory {directory}: {e}")
        
        # Remove duplicates and sort
        voices = sorted(list(set(voices)))
        self.voices_ready.emit(voices)

# NEW: Model Scanner Thread
class ModelScanner(QThread):
    models_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def run(self):
        """Scan for available Ollama models with better error handling"""
        try:
            # Try using Ollama REST API first (more reliable)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    self.models_ready.emit(models)
                    return
            except requests.exceptions.RequestException:
                pass  # Fall back to CLI
            
            # Fallback to CLI method
            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=15,  # Increased timeout
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().splitlines()
                models = []
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        if ':' in model_name:
                            models.append(model_name)
                
                self.models_ready.emit(models)
            else:
                self.error_occurred.emit("Ollama not found or not running")
                
        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Ollama command timed out")
        except FileNotFoundError:
            self.error_occurred.emit("Ollama not installed")
        except Exception as e:
            self.error_occurred.emit(f"Error scanning models: {str(e)}")

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, theme=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.theme = theme or THEMES["Classic Dark"]
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def setVariant(self, variant="primary"):
        # IMPROVED: Better button styling with transitions
        if variant == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self.theme["button_primary"]};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 12px 24px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 20px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background: {self.theme["button_primary"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.9;
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: {self.theme["button_primary"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.8;
                    transform: translateY(1px);
                }}
                QPushButton:disabled {{
                    background: #555555;
                    color: #888888;
                }}
            """)
        elif variant == "secondary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self.theme["button_secondary"]};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-height: 18px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background: {self.theme["button_secondary"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.9;
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: {self.theme["button_secondary"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.8;
                    transform: translateY(1px);
                }}
            """)
        elif variant == "danger":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self.theme["button_danger"]};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 12px;
                    min-height: 18px;
                    transition: all 0.2s ease;
                }}
                QPushButton:hover {{
                    background: {self.theme["button_danger"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.9;
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background: {self.theme["button_danger"].replace('stop:0', 'stop:0').replace('stop:1', 'stop:1')};
                    opacity: 0.8;
                    transform: translateY(1px);
                }}
            """)

class ModernGroupBox(QGroupBox):
    def __init__(self, title, parent=None, theme=None):
        super().__init__(title, parent)
        self.theme = theme or THEMES["Classic Dark"]
        self.apply_theme()
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QGroupBox {{
                background: {self.theme["group_box"]};
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 15px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
                color: {self.theme["text"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: {self.theme["accent"]};
                font-weight: bold;
                font-size: 13px;
            }}
        """)

class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None, theme=None):
        super().__init__(parent)
        self.theme = theme or THEMES["Classic Dark"]
        self.apply_theme()
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                text-align: center;
                color: {self.theme["text"]};
                font-weight: bold;
                background: rgba(0,0,0,0.3);
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: {self.theme["button_primary"]};
                border-radius: 8px;
            }}
        """)

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

# NEW: Improved AI Worker with better error handling and memory management
class AIWorker(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, prompt, model, temperature=0.7, max_tokens=512, parent=None):
        super().__init__(parent)
        self.prompt = prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
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
                        "stop": ["\n\n", "Player:", "Dungeon Master:"],
                        "min_p": 0.05,
                        "top_k": 40,
                        "top_p": 0.9,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=CONFIG["REQUEST_TIMEOUT"]
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            raise Exception("AI request timed out")
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

# NEW: Improved TTS Worker with better chunking and error handling
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
                
            # IMPROVED: Better text chunking for long responses
            sentences = text.split('. ')
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk + sentence) < 150:  # Smaller chunks for better performance
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence + ". "
            if current_chunk:
                chunks.append(current_chunk)
                
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                payload = {
                    "text_input": chunk,
                    "character_voice_gen": voice,
                    "narrator_enabled": "true",
                    "narrator_voice_gen": "narrator.wav",
                    "text_filtering": "none",
                    "output_file_name": f"output_{i}",
                    "autoplay": "true",
                    "autoplay_volume": "0.8"
                }
                
                r = requests.post(CONFIG["ALLTALK_API_URL"], data=payload, timeout=30)
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

class ModernSetupDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.current_theme_name = self.settings.value("theme", "Classic Dark")
        self.current_theme = THEMES.get(self.current_theme_name, THEMES["Classic Dark"])
        self.setWindowTitle("🎮 Adventure Setup - Choose Your Destiny")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(700)
        
        # Voice scanner
        self.voice_scanner = VoiceScanner()
        self.voice_scanner.voices_ready.connect(self.on_voices_ready)
        
        # Model scanner
        self.model_scanner = ModelScanner()
        self.model_scanner.models_ready.connect(self.on_models_ready)
        self.model_scanner.error_occurred.connect(self.on_models_error)
        
        self.init_ui()
        self.load_settings()
        
        # Start scanning
        self.voice_scanner.start()
        self.model_scanner.start()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Apply theme
        self.apply_theme_stylesheet()
        
        # Header
        header_label = QLabel("🚀 Adventure Setup")
        header_label.setObjectName("title")
        subtitle_label = QLabel("Craft your unique story - choose your world and destiny")
        subtitle_label.setObjectName("subtitle")
        
        layout.addWidget(header_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 15px;
                background: rgba(255,255,255,0.05);
                margin-top: 10px;
            }
        """)
        
        # Basic Settings Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        basic_layout.setSpacing(25)
        basic_layout.setContentsMargins(25, 25, 25, 25)
        
        # Theme selection
        theme_group = ModernGroupBox("🎨 Theme Selection", theme=self.current_theme)
        theme_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(self.current_theme_name)
        self.theme_combo.currentTextChanged.connect(self.theme_changed)
        theme_layout.addWidget(QLabel("Select Theme:"))
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        basic_layout.addWidget(theme_group)
        
        # Model selection
        model_group = ModernGroupBox("🤖 AI Model Configuration", theme=self.current_theme)
        model_layout = QVBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItem("🔍 Scanning for models...")
        model_layout.addWidget(QLabel("Select AI Model:"))
        model_layout.addWidget(self.model_combo)
        
        model_button_layout = QHBoxLayout()
        self.refresh_models_button = ModernButton("🔄 Refresh Models", theme=self.current_theme)
        self.refresh_models_button.setVariant("secondary")
        self.refresh_models_button.clicked.connect(self.refresh_models)
        self.test_model_button = ModernButton("🧪 Test Connection", theme=self.current_theme)
        self.test_model_button.setVariant("secondary")
        self.test_model_button.clicked.connect(self.test_model_connection)
        
        model_button_layout.addWidget(self.refresh_models_button)
        model_button_layout.addWidget(self.test_model_button)
        model_layout.addLayout(model_button_layout)
        
        model_group.setLayout(model_layout)
        basic_layout.addWidget(model_group)
        
        # Genre and Role selection
        genre_role_layout = QHBoxLayout()
        
        genre_group = ModernGroupBox("🌍 Adventure Genre", theme=self.current_theme)
        genre_layout = QVBoxLayout()
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(ROLE_STARTERS.keys())
        self.genre_combo.currentTextChanged.connect(self.genre_changed)
        genre_layout.addWidget(QLabel("Select Genre:"))
        genre_layout.addWidget(self.genre_combo)
        
        self.genre_desc = QLabel()
        self.genre_desc.setWordWrap(True)
        self.genre_desc.setStyleSheet(f"""
            background: rgba(255,255,255,0.08); 
            color: {self.current_theme["text"]}; 
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
        
        role_group = ModernGroupBox("👤 Character Role", theme=self.current_theme)
        role_layout = QVBoxLayout()
        self.role_combo = QComboBox()
        role_layout.addWidget(QLabel("Select Role:"))
        role_layout.addWidget(self.role_combo)
        
        self.role_desc = QLabel()
        self.role_desc.setWordWrap(True)
        self.role_desc.setStyleSheet(f"""
            background: rgba(255,255,255,0.08); 
            color: {self.current_theme["text"]}; 
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
        char_group = ModernGroupBox("📝 Character Details", theme=self.current_theme)
        char_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter your character's name...")
        char_layout.addWidget(QLabel("Character Name:"))
        char_layout.addWidget(self.name_edit)
        
        # NEW: Character backstory
        self.backstory_edit = QTextEdit()
        self.backstory_edit.setPlaceholderText("Optional: Add your character's backstory, personality, or special traits...")
        self.backstory_edit.setMaximumHeight(80)
        char_layout.addWidget(QLabel("Character Backstory (Optional):"))
        char_layout.addWidget(self.backstory_edit)
        
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
        tts_group = ModernGroupBox("🔊 Voice Settings", theme=self.current_theme)
        tts_layout = QVBoxLayout()
        self.tts_enabled = QCheckBox("Enable Text-to-Speech")
        self.tts_enabled.setChecked(True)
        tts_layout.addWidget(self.tts_enabled)
        
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice Style:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItem("🔍 Scanning for voices...")
        self.refresh_voices_button = ModernButton("🔄 Refresh Voices", theme=self.current_theme)
        self.refresh_voices_button.setVariant("secondary")
        self.refresh_voices_button.clicked.connect(self.refresh_voices)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addWidget(self.refresh_voices_button)
        tts_layout.addLayout(voice_layout)
        
        # NEW: TTS volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("TTS Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_label = QLabel("80%")
        self.volume_label.setStyleSheet(f"color: {self.current_theme['accent']}; font-weight: bold;")
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%")
        )
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        tts_layout.addLayout(volume_layout)
        
        tts_group.setLayout(tts_layout)
        advanced_layout.addWidget(tts_group)
        
        # AI Settings
        ai_group = ModernGroupBox("⚡ AI Behavior", theme=self.current_theme)
        ai_layout = QVBoxLayout()
        
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Creativity Level:"))
        self.temp_label = QLabel("0.7")
        self.temp_label.setStyleSheet(f"color: {self.current_theme['accent']}; font-weight: bold;")
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
        self.cancel_button = ModernButton("❌ Cancel", theme=self.current_theme)
        self.cancel_button.setVariant("danger")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = ModernButton("🚀 Start Adventure!", theme=self.current_theme)
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
        
        # Add animations
        self.setup_animations()
    
    def apply_theme_stylesheet(self):
        self.setStyleSheet(f"""
            QDialog {{
                background: {self.current_theme["background"]};
                color: {self.current_theme["text"]};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QLabel {{
                color: {self.current_theme["text"]};
                font-size: 12px;
            }}
            QLabel#title {{
                color: white;
                font-size: 24px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }}
            QLabel#subtitle {{
                color: {self.current_theme["accent"]};
                font-size: 14px;
                qproperty-alignment: AlignCenter;
            }}
            QComboBox {{
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 10px;
                color: {self.current_theme["text"]};
                font-size: 12px;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border: 2px solid {self.current_theme["primary"]};
            }}
            QComboBox QAbstractItemView {{
                background: #2d3748;
                border: 1px solid #4a5568;
                color: {self.current_theme["text"]};
                selection-background-color: {self.current_theme["primary"]};
            }}
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 12px;
                color: {self.current_theme["text"]};
                font-size: 13px;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.current_theme["primary"]};
            }}
            QTextEdit {{
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 8px;
                color: {self.current_theme["text"]};
                font-size: 12px;
            }}
            QSpinBox {{
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 8px;
                color: {self.current_theme["text"]};
                min-height: 20px;
            }}
            QCheckBox {{
                color: {self.current_theme["text"]};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255,255,255,0.5);
                border-radius: 4px;
                background: rgba(255,255,255,0.1);
            }}
            QCheckBox::indicator:checked {{
                background: {self.current_theme["primary"]};
                border: 2px solid {self.current_theme["primary"]};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid rgba(255,255,255,0.3);
                height: 6px;
                background: rgba(255,255,255,0.1);
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {self.current_theme["button_primary"]};
                border: 2px solid rgba(255,255,255,0.8);
                width: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QTabWidget::pane {{
                border: 1px solid rgba(255,255,255,0.2);
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
                background: rgba({QColor(self.current_theme["primary"]).red()}, {QColor(self.current_theme["primary"]).green()}, {QColor(self.current_theme["primary"]).blue()}, 0.3);
                color: white;
                border-bottom: 2px solid {self.current_theme["primary"]};
            }}
            QTabBar::tab:hover {{
                background: rgba(255,255,255,0.2);
            }}
        """)
    
    def theme_changed(self, theme_name):
        self.current_theme_name = theme_name
        self.current_theme = THEMES.get(theme_name, THEMES["Classic Dark"])
        self.apply_theme_stylesheet()
        
        # Update all themed widgets
        for widget in self.findChildren(ModernGroupBox):
            widget.theme = self.current_theme
            widget.apply_theme()
        
        for widget in self.findChildren(ModernButton):
            widget.theme = self.current_theme
            # Re-apply variant to update colors
            if "primary" in widget.styleSheet():
                widget.setVariant("primary")
            elif "secondary" in widget.styleSheet():
                widget.setVariant("secondary")
            elif "danger" in widget.styleSheet():
                widget.setVariant("danger")
        
        # Update description labels
        self.genre_desc.setStyleSheet(f"""
            background: rgba(255,255,255,0.08); 
            color: {self.current_theme["text"]}; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            line-height: 1.4;
        """)
        self.role_desc.setStyleSheet(f"""
            background: rgba(255,255,255,0.08); 
            color: {self.current_theme["text"]}; 
            padding: 15px; 
            border-radius: 10px; 
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            line-height: 1.4;
        """)
        self.temp_label.setStyleSheet(f"color: {self.current_theme['accent']}; font-weight: bold;")
        self.volume_label.setStyleSheet(f"color: {self.current_theme['accent']}; font-weight: bold;")
    
    def setup_animations(self):
        # Simple fade-in animation for the dialog
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
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
    
    def on_models_ready(self, models):
        """Update model combo box with scanned models"""
        self.model_combo.clear()
        if models:
            for model in models:
                self.model_combo.addItem(model)
        else:
            self.model_combo.addItem("llama3:instruct")
            self.model_combo.addItem("mistral:instruct")
    
    def on_models_error(self, error_msg):
        """Handle model scanning errors"""
        self.model_combo.clear()
        self.model_combo.addItem("llama3:instruct")
        self.model_combo.addItem("mistral:instruct")
        QMessageBox.warning(self, "Model Scan Error", 
                          f"Could not scan for models: {error_msg}\nUsing default models.")
    
    def refresh_voices(self):
        """Refresh available voices"""
        self.voice_combo.clear()
        self.voice_combo.addItem("🔍 Scanning for voices...")
        self.voice_scanner.start()
    
    def refresh_models(self):
        """Refresh available models"""
        self.model_combo.clear()
        self.model_combo.addItem("🔍 Scanning for models...")
        self.model_scanner.start()
    
    def test_model_connection(self):
        """Test connection to selected model"""
        model = self.model_combo.currentText()
        if not model or model == "🔍 Scanning for models...":
            QMessageBox.warning(self, "Test Connection", "Please select a model first.")
            return
        
        try:
            test_prompt = "Respond with just 'OK' if you can read this."
            response = requests.post(
                CONFIG["OLLAMA_URL"],
                json={
                    "model": model,
                    "prompt": test_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Test Connection", 
                                      f"✅ Successfully connected to {model}!")
            else:
                QMessageBox.warning(self, "Test Connection", 
                                  f"❌ Failed to connect to {model}.\nStatus: {response.status_code}")
                
        except Exception as e:
            QMessageBox.critical(self, "Test Connection", 
                              f"❌ Error testing connection: {str(e)}")
    
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
    
    def load_settings(self):
        self.name_edit.setText(self.settings.value("character_name", "Laszlo"))
        self.model_combo.setCurrentText(self.settings.value("model", "llama3:instruct"))
        self.genre_combo.setCurrentText(self.settings.value("genre", "Fantasy"))
        self.tts_enabled.setChecked(self.settings.value("tts_enabled", True, type=bool))
        self.theme_combo.setCurrentText(self.settings.value("theme", "Classic Dark"))
        
        # Load volume setting
        volume = self.settings.value("tts_volume", 80, type=int)
        self.volume_slider.setValue(volume)
        
        # Load backstory if exists
        backstory = self.settings.value("character_backstory", "")
        self.backstory_edit.setPlainText(backstory)
        
        # Fix for voice setting type conversion
        voice_value = self.settings.value("voice", 0)
        try:
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
            "character_backstory": self.backstory_edit.toPlainText(),
            "tts_enabled": self.tts_enabled.isChecked(),
            "voice": voice_file,
            "volume": self.volume_slider.value(),
            "temperature": self.temp_slider.value() / 100.0,
            "max_tokens": self.max_tokens_spin.value(),
            "theme": self.theme_combo.currentText()
        }

class AdventureGameGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(CONFIG["CONFIG_FILE"], QSettings.IniFormat)
        self.current_theme_name = self.settings.value("theme", "Classic Dark")
        self.current_theme = THEMES.get(self.current_theme_name, THEMES["Classic Dark"])
        self.setWindowTitle("✨ AI Dungeon Master - Interactive Storytelling")
        self.setGeometry(100, 100, 1200, 900)
        
        self.adventure_started = False
        self.last_ai_reply = ""
        self.conversation = ""
        self.last_player_input = ""
        self.ollama_model = "llama3:instruct"
        self.character_name = ""
        self.character_backstory = ""
        self.selected_genre = ""
        self.selected_role = ""
        self.tts_enabled = True
        self.tts_volume = 80
        self.selected_voice = "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"
        self.temperature = 0.7
        self.max_tokens = 512
        
        self.ai_worker = None
        self.tts_worker = None
        
        # NEW: Conversation history for memory management
        self.conversation_history = []
        self.current_conversation_index = -1
        
        # Store references to UI elements
        self.subtitle_label = None
        
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
        
        # Apply theme
        self.apply_theme()
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("🎭 AI Dungeon Master")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        self.subtitle_label = QLabel("Your interactive storytelling companion")
        self.subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {self.current_theme["accent"]};
                font-size: 14px;
                font-style: italic;
            }}
        """)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(header_widget)
        
        # Game text area with syntax highlighting
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Segoe UI", 12))
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background: {self.current_theme["text_area"]};
                color: {self.current_theme["text"]};
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                selection-background-color: rgba({QColor(self.current_theme["primary"]).red()}, {QColor(self.current_theme["primary"]).green()}, {QColor(self.current_theme["primary"]).blue()}, 0.3);
            }}
        """)
        self.highlighter = SyntaxHighlighter(self.text_area.document())
        
        # Add shadow to text area
        text_shadow = QGraphicsDropShadowEffect()
        text_shadow.setBlurRadius(25)
        text_shadow.setColor(QColor(0, 0, 0, 80))
        text_shadow.setOffset(0, 8)
        self.text_area.setGraphicsEffect(text_shadow)
        
        # Progress bar
        self.progress_bar = ModernProgressBar(theme=self.current_theme)
        self.progress_bar.setVisible(False)
        
        # Status bar
        self.status_label = QLabel("🟢 Ready to begin your adventure")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,255,255,0.1);
                color: {self.current_theme["accent"]};
                padding: 8px 15px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.2);
                font-size: 11px;
                font-weight: bold;
            }}
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
                color: {self.current_theme["text"]};
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 12px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.current_theme["primary"]};
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
        
        self.send_button = ModernButton("🚀 Send", theme=self.current_theme)
        self.send_button.setVariant("primary")
        self.send_button.clicked.connect(self.send_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        
        # Control buttons - IMPROVED with new buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        self.help_button = ModernButton("❓ Help", theme=self.current_theme)
        self.help_button.setVariant("secondary")
        self.help_button.clicked.connect(self.show_help)
        
        self.retry_button = ModernButton("🔄 Retry", theme=self.current_theme)  # NEW
        self.retry_button.setVariant("secondary")
        self.retry_button.clicked.connect(self.retry_last)
        
        self.export_button = ModernButton("💾 Export", theme=self.current_theme)  # NEW
        self.export_button.setVariant("secondary")
        self.export_button.clicked.connect(self.export_conversation)
        
        self.save_button = ModernButton("📁 Save", theme=self.current_theme)
        self.save_button.setVariant("secondary")
        self.save_button.clicked.connect(self.save_adventure)
        
        self.load_button = ModernButton("📂 Load", theme=self.current_theme)
        self.load_button.setVariant("secondary")
        self.load_button.clicked.connect(self.load_adventure)
        
        self.settings_button = ModernButton("⚙️ Settings", theme=self.current_theme)
        self.settings_button.setVariant("secondary")
        self.settings_button.clicked.connect(self.show_settings)
        
        self.theme_button = ModernButton("🎨 Theme", theme=self.current_theme)
        self.theme_button.setVariant("secondary")
        self.theme_button.clicked.connect(self.cycle_theme)
        
        self.exit_button = ModernButton("⏹️ Exit", theme=self.current_theme)
        self.exit_button.setVariant("danger")
        self.exit_button.clicked.connect(self.exit_game)
        
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.retry_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.theme_button)
        button_layout.addWidget(self.exit_button)
        
        layout.addWidget(self.text_area, 1)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(input_widget)
        layout.addWidget(button_widget)
        
    def apply_theme(self):
        """Apply comprehensive theme to the entire application"""
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
        
        # Additional theme styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {self.current_theme["background"]};
            }}
            QMessageBox {{
                background: #2d2d2d;
                color: {self.current_theme["text"]};
            }}
            QMessageBox QLabel {{
                color: {self.current_theme["text"]};
            }}
            QMessageBox QPushButton {{
                background: #404040;
                color: {self.current_theme["text"]};
                border: 1px solid #555;
                padding: 5px 15px;
                border-radius: 4px;
            }}
            QMessageBox QPushButton:hover {{
                background: #505050;
            }}
        """)
    
    def cycle_theme(self):
        """Cycle through available themes"""
        theme_names = list(THEMES.keys())
        current_index = theme_names.index(self.current_theme_name)
        next_index = (current_index + 1) % len(theme_names)
        next_theme = theme_names[next_index]
        
        self.current_theme_name = next_theme
        self.current_theme = THEMES[next_theme]
        
        # Save theme preference
        self.settings.setValue("theme", self.current_theme_name)
        
        # Re-apply theme to UI
        self.apply_theme()
        self.update_ui_theme()
        
        self.append_text(f"🎨 <font color='{self.current_theme['accent']}'>Theme changed to: {self.current_theme_name}</font><br>")
    
    def update_ui_theme(self):
        """Update all themed UI elements"""
        # Update progress bar
        self.progress_bar.theme = self.current_theme
        self.progress_bar.apply_theme()
        
        # Update buttons
        for button in [self.help_button, self.retry_button, self.export_button, 
                      self.save_button, self.load_button, self.settings_button, 
                      self.theme_button, self.exit_button, self.send_button]:
            button.theme = self.current_theme
            if "primary" in button.styleSheet():
                button.setVariant("primary")
            elif "secondary" in button.styleSheet():
                button.setVariant("secondary")
            elif "danger" in button.styleSheet():
                button.setVariant("danger")
        
        # Update text area
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background: {self.current_theme["text_area"]};
                color: {self.current_theme["text"]};
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 20px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                selection-background-color: rgba({QColor(self.current_theme["primary"]).red()}, {QColor(self.current_theme["primary"]).green()}, {QColor(self.current_theme["primary"]).blue()}, 0.3);
            }}
        """)
        
        # Update status label
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(255,255,255,0.1);
                color: {self.current_theme["accent"]};
                padding: 8px 15px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.2);
                font-size: 11px;
                font-weight: bold;
            }}
        """)
        
        # Update input field
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255,255,255,0.1);
                color: {self.current_theme["text"]};
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 12px;
                padding: 15px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.current_theme["primary"]};
                background: rgba(255,255,255,0.15);
            }}
            QLineEdit:disabled {{
                background: rgba(255,255,255,0.05);
                color: #888888;
            }}
        """)
        
        # Update subtitle label safely
        if self.subtitle_label:
            self.subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.current_theme["accent"]};
                    font-size: 14px;
                    font-style: italic;
                }}
            """)
    
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
        self.character_backstory = selections["character_backstory"]
        self.tts_enabled = selections["tts_enabled"]
        self.tts_volume = selections["volume"]
        self.selected_voice = selections["voice"]
        self.temperature = selections["temperature"]
        self.max_tokens = selections["max_tokens"]
        
        # Update theme if changed
        new_theme = selections.get("theme", self.current_theme_name)
        if new_theme != self.current_theme_name:
            self.current_theme_name = new_theme
            self.current_theme = THEMES.get(new_theme, THEMES["Classic Dark"])
            self.apply_theme()
            self.update_ui_theme()
        
        # Save settings
        self.settings.setValue("model", self.ollama_model)
        self.settings.setValue("genre", self.selected_genre)
        self.settings.setValue("role", self.selected_role)
        self.settings.setValue("character_name", self.character_name)
        self.settings.setValue("character_backstory", self.character_backstory)
        self.settings.setValue("tts_enabled", self.tts_enabled)
        self.settings.setValue("tts_volume", self.tts_volume)
        self.settings.setValue("theme", self.current_theme_name)
        
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
        
        if self.character_backstory:
            self.append_text(f"<b>📖 Character Backstory:</b> {self.character_backstory}<br><br>")
            
        self.append_text("<font color='#4FC3F7'>💡 Type <b>/help</b> for available commands</font><br><br>")
        
        # IMPROVED: Better initial context with character backstory
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {self.selected_genre}\n"
            f"Player Character: {self.character_name} the {self.selected_role}\n"
        )
        
        if self.character_backstory:
            initial_context += f"Character Backstory: {self.character_backstory}\n"
            
        initial_context += f"Starting Scenario: {starter}\n\nDungeon Master: "
        
        self.conversation = initial_context
        
        # NEW: Add to conversation history
        self.conversation_history = [initial_context]
        self.current_conversation_index = 0
        
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
        self.append_text(f"<font color='#4FC3F7'><b>🎭 You:</b> {user_input}</font><br>")
        
        formatted_input = f"Player: {user_input}"
        
        # NEW: Manage conversation length to prevent memory issues
        if len(self.conversation) > CONFIG["MAX_CONVERSATION_LENGTH"]:
            # Keep only the most recent part of the conversation
            lines = self.conversation.split('\n')
            # Keep last 20 lines
            self.conversation = '\n'.join(lines[-20:])
            self.append_text("<font color='#FFB74D'>--- Conversation trimmed for memory ---</font><br>")
        
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
        elif cmd == '/retry' or cmd == '/redo':
            self.retry_last()
        elif cmd == '/save':
            self.save_adventure()
        elif cmd == '/load':
            self.load_adventure()
        elif cmd == '/export':
            self.export_conversation()
        elif cmd == '/settings':
            self.show_settings()
        elif cmd == '/clear':
            self.text_area.clear()
            self.append_text("🧹 <font color='#FFA500'>Chat cleared.</font><br>")
        elif cmd == '/theme':
            self.cycle_theme()
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
        elif cmd == '/theme':
            self.append_text(f"🎨 <font color='#FFA500'>Current theme: {self.current_theme_name}</font><br>")
        elif cmd == '/status':
            self.show_status()
        else:
            self.append_text(f"❌ <font color='#FF6B6B'>Unknown command: {command}</font><br>")
    
    def show_status(self):
        """Show current game status"""
        status_text = f"""
<h3>🎮 Current Game Status:</h3>
<ul>
<li><b>Character:</b> {self.character_name} the {self.selected_role}</li>
<li><b>Genre:</b> {self.selected_genre}</li>
<li><b>AI Model:</b> {self.ollama_model}</li>
<li><b>TTS:</b> {'Enabled' if self.tts_enabled else 'Disabled'}</li>
<li><b>Theme:</b> {self.current_theme_name}</li>
<li><b>Conversation Length:</b> {len(self.conversation)} characters</li>
</ul>
"""
        QMessageBox.information(self, "Game Status", status_text)
    
    def get_ai_response(self, prompt):
        self.status_label.setText("🤔 Generating response...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.set_ui_enabled(False)
        
        self.ai_worker = AIWorker(prompt, self.ollama_model, self.temperature, self.max_tokens)
        self.ai_worker.response_ready.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(self.handle_ai_error)
        self.ai_worker.progress_update.connect(self.progress_bar.setValue)
        self.ai_worker.start()
    
    def handle_ai_response(self, response):
        self.progress_bar.setVisible(False)
        self.set_ui_enabled(True)
        self.status_label.setText("🟢 Ready for your next action")
        
        self.append_text(f"<font color='#81C784'><b>🎮 Dungeon Master:</b> {response}</font><br><br>")
        self.conversation += f"\nDungeon Master: {response}"
        self.last_ai_reply = response
        
        # NEW: Add to conversation history
        self.conversation_history.append(f"Dungeon Master: {response}")
        if len(self.conversation_history) > CONFIG["MAX_HISTORY_ITEMS"]:
            self.conversation_history.pop(0)
        self.current_conversation_index = len(self.conversation_history) - 1
        
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
        # Don't show message box for TTS errors to avoid interrupting gameplay
    
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
        self.retry_button.setEnabled(enabled)
        self.export_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.load_button.setEnabled(enabled)
        self.settings_button.setEnabled(enabled)
        self.theme_button.setEnabled(enabled)
        self.exit_button.setEnabled(enabled)
    
    def show_help(self):
        help_text = f"""
<h3>🎮 Available Commands:</h3>
<ul>
<li><b>/? or /help</b> - Show this help message</li>
<li><b>/retry or /redo</b> - Retry last AI response</li>
<li><b>/export</b> - Export conversation to file</li>
<li><b>/save</b> - Save adventure</li>
<li><b>/load</b> - Load adventure</li>
<li><b>/settings</b> - Change game settings</li>
<li><b>/clear</b> - Clear chat</li>
<li><b>/theme</b> - Change theme</li>
<li><b>/model [name]</b> - Change AI model</li>
<li><b>/tts</b> - Toggle text-to-speech</li>
<li><b>/voices</b> - Show current voice</li>
<li><b>/status</b> - Show game status</li>
<li><b>/exit</b> - Exit game</li>
</ul>
<h3>🎯 Gameplay Tips:</h3>
<p>Describe your actions naturally. The AI will respond with consequences and story developments.<br>
Be creative and immersive in your descriptions!</p>
<p>Current Theme: <b>{self.current_theme_name}</b></p>
"""
        QMessageBox.information(self, "Help Guide", help_text)
    
    def retry_last(self):
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
            QMessageBox.warning(self, "Retry", "🔄 Nothing to retry.")
    
    def export_conversation(self):
        """Export conversation to a text file"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Conversation", 
                f"adventure_export_{timestamp}.txt", 
                "Text Files (*.txt);;HTML Files (*.html)"
            )
            
            if file_path:
                if file_path.endswith('.html'):
                    # Export as HTML with formatting
                    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>AI Dungeon Master Export - {timestamp}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 20px; }}
                            .player {{ color: #4FC3F7; font-weight: bold; }}
                            .dm {{ color: #81C784; }}
                            .system {{ color: #FFB74D; font-style: italic; }}
                            .header {{ text-align: center; margin-bottom: 30px; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>🎭 AI Dungeon Master Export</h1>
                            <p>Character: {self.character_name} the {self.selected_role} | Genre: {self.selected_genre}</p>
                            <p>Exported: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                        </div>
                        <div class="conversation">
                            {self.text_area.toHtml()}
                        </div>
                    </body>
                    </html>
                    """
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    # Export as plain text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"AI Dungeon Master Export\n")
                        f.write(f"Character: {self.character_name} the {self.selected_role}\n")
                        f.write(f"Genre: {self.selected_genre}\n")
                        f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("="*50 + "\n\n")
                        f.write(self.text_area.toPlainText())
                
                self.append_text(f"📤 <font color='#FFA500'>Conversation exported to: {file_path}</font><br>")
                
        except Exception as e:
            error_msg = f"Error exporting conversation: {str(e)}"
            self.log_error(error_msg)
            QMessageBox.warning(self, "Export Error", "❌ Error exporting conversation.")
    
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
    app.setApplicationVersion("4.0")  # Updated version
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
