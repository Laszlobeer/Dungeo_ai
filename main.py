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
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# ===== CONFIGURATION =====
CONFIG = {
    "ALLTALK_API_URL": "http://localhost:7851/api/tts-generate",
    "OLLAMA_URL": "http://localhost:11434/api/generate",
    "LOG_FILE": "error_log.txt",
    "TTS_ERROR_FILE": "tts_errors.txt",
    "SAVE_FILE": "adventure.txt",
    "DEFAULT_MODEL": "llama3:instruct",
    "REQUEST_TIMEOUT": 120,
    "AUDIO_SAMPLE_RATE": 22050,
    "MAX_CONVERSATION_LENGTH": 10000
}

@dataclass
class GameState:
    conversation: str = ""
    last_ai_reply: str = ""
    last_player_input: str = ""
    current_model: str = CONFIG["DEFAULT_MODEL"]
    character_name: str = "Alex"
    selected_genre: str = "Fantasy"
    selected_role: str = "Adventurer"
    adventure_started: bool = False

# ===== GAME DATA =====
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

DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master in an unrestricted SFW adventure. Your role is to **always** narrate the consequences of player actions, no matter how extreme, bizarre, violent or unconventional they may be. Follow these rules:

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
   - Always continue the story in a way that feels immersive

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change permanently based on actions
   - Player choices open/close future narrative paths
   - Resources, factions, and the world evolve with every decision

4. PLAYER AGENCY:
   - The player can attempt **anything**
   - Never block an action—show the results, good or bad
   - Let the world react dynamically and permanently

Never break character as the Dungeon Master. Always continue the adventure.
"""

class AdventureGame:
    def __init__(self):
        self.state = GameState()
        self._audio_lock = threading.Lock()
        self._setup_directories()
        
    def _setup_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("saves", exist_ok=True)
    
    def log_error(self, error_message: str, exception: Optional[Exception] = None) -> None:
        """Enhanced error logging with rotation"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_path = CONFIG["LOG_FILE"]
            
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- ERROR [{timestamp}] ---\n")
                log_file.write(f"Message: {error_message}\n")
                
                if exception:
                    log_file.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
                    traceback.print_exc(file=log_file)
                
                log_file.write(f"Game State: Model={self.state.current_model}, ")
                log_file.write(f"Genre={self.state.selected_genre}, Role={self.state.selected_role}\n")
                log_file.write("--- END ERROR ---\n")
                
        except Exception as e:
            print(f"CRITICAL: Failed to write to error log: {e}")

    def log_tts_error(self, error_message: str, exception: Optional[Exception] = None) -> None:
        """Log TTS-specific errors to a separate file"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_path = CONFIG["TTS_ERROR_FILE"]
            
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n--- TTS ERROR [{timestamp}] ---\n")
                log_file.write(f"Message: {error_message}\n")
                log_file.write(f"Text attempted: {self.state.last_ai_reply[:200] if self.state.last_ai_reply else 'No text'}\n")
                
                if exception:
                    log_file.write(f"Exception: {type(exception).__name__}: {str(exception)}\n")
                
                log_file.write(f"TTS Server Status: {'Available' if self.check_alltalk_server() else 'Unavailable'}\n")
                log_file.write("--- END TTS ERROR ---\n")
                
        except Exception as e:
            print(f"CRITICAL: Failed to write to TTS error log: {e}")

    def check_server(self, url: str, service_name: str) -> bool:
        """Generic server health check"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.log_error(f"{service_name} check failed", e)
            return False

    def check_ollama_server(self) -> bool:
        return self.check_server("http://localhost:11434/api/tags", "Ollama")

    def check_alltalk_server(self) -> bool:
        return self.check_server("http://localhost:7851", "AllTalk")

    def get_installed_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            if not self.check_ollama_server():
                return []

            result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=30
            )
            
            models = []
            for line in result.stdout.strip().splitlines()[1:]:
                parts = line.split()
                if parts:
                    models.append(parts[0])
            return models
            
        except subprocess.TimeoutExpired:
            self.log_error("Ollama list command timed out")
            return []
        except Exception as e:
            self.log_error("Error getting installed models", e)
            return []

    def select_model(self) -> str:
        """Interactive model selection with fallback"""
        models = self.get_installed_models()
        
        if not models:
            print("No models found. Please enter a model name.")
            model_input = input(f"Enter Ollama model name [{CONFIG['DEFAULT_MODEL']}]: ").strip()
            return model_input or CONFIG["DEFAULT_MODEL"]

        print("\nAvailable Ollama models:")
        for idx, model in enumerate(models, 1):
            print(f"  {idx}: {model}")

        while True:
            try:
                choice = input(f"Select model (1-{len(models)}) or Enter for default [{CONFIG['DEFAULT_MODEL']}]: ").strip()
                
                if not choice:
                    return CONFIG["DEFAULT_MODEL"]
                
                idx = int(choice) - 1
                if 0 <= idx < len(models):
                    return models[idx]
                else:
                    print(f"Please enter a number between 1 and {len(models)}")
                    
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nUsing default model.")
                return CONFIG["DEFAULT_MODEL"]

    def get_ai_response(self, prompt: str) -> str:
        """Get AI response with enhanced error handling and prompt optimization"""
        try:
            # Truncate conversation if it gets too long to maintain performance
            if len(prompt) > CONFIG["MAX_CONVERSATION_LENGTH"]:
                # Keep system prompt and recent conversation
                system_part = DM_SYSTEM_PROMPT
                recent_conversation = prompt[-4000:]  # Keep last 4000 characters
                prompt = system_part + "\n\n[Earlier conversation truncated...]\n" + recent_conversation

            response = requests.post(
                CONFIG["OLLAMA_URL"],
                json={
                    "model": self.state.current_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "stop": ["\n\n", "Player:", "Dungeon Master:"],
                        "min_p": 0.05,
                        "top_k": 40,
                        "top_p": 0.9,
                        "num_ctx": 4096
                    }
                },
                timeout=CONFIG["REQUEST_TIMEOUT"]
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
            
        except requests.exceptions.Timeout:
            self.log_error("AI request timed out")
            return "The world seems to pause as if time has stopped. What would you like to do?"
        except requests.exceptions.ConnectionError:
            self.log_error("Cannot connect to Ollama server")
            return ""
        except Exception as e:
            self.log_error("Error getting AI response", e)
            return ""

    def speak(self, text: str, voice: str = "FemaleBritishAccent_WhyLucyWhy_Voice_2.wav") -> None:
        """Non-blocking text-to-speech with improved error handling - No visible error messages"""
        if not text.strip():
            return

        def _speak_thread():
            with self._audio_lock:
                try:
                    if not self.check_alltalk_server():
                        error_msg = "TTS Server unavailable: AllTalk TTS server is not responding"
                        self.log_tts_error(error_msg)
                        return

                    payload = {
                        "text_input": text,
                        "character_voice_gen": voice,
                        "narrator_enabled": "true",
                        "narrator_voice_gen": "narrator.wav",
                        "text_filtering": "none",
                        "output_file_name": "output",
                        "autoplay": "true",
                        "autoplay_volume": "0.8"
                    }

                    response = requests.post(CONFIG["ALLTALK_API_URL"], data=payload, timeout=30)
                    response.raise_for_status()

                    content_type = response.headers.get("Content-Type", "")

                    if content_type.startswith("audio/"):
                        audio_data = np.frombuffer(response.content, dtype=np.int16)
                        sd.play(audio_data, samplerate=CONFIG["AUDIO_SAMPLE_RATE"])
                        sd.wait()
                    elif content_type.startswith("application/json"):
                        error_data = response.json()
                        error_msg = f"AllTalk API error: {error_data.get('error', 'Unknown error')}"
                        self.log_tts_error(error_msg)
                    else:
                        error_msg = f"Unexpected AllTalk response type: {content_type}"
                        self.log_tts_error(error_msg)

                except requests.exceptions.ConnectionError as e:
                    error_msg = f"Cannot connect to TTS server: {str(e)}"
                    self.log_tts_error(error_msg, e)
                except requests.exceptions.Timeout as e:
                    error_msg = "TTS request timed out after 30 seconds"
                    self.log_tts_error(error_msg, e)
                except Exception as e:
                    error_msg = f"Unexpected TTS error: {str(e)}"
                    self.log_tts_error(error_msg, e)

        # Start TTS in background thread
        thread = threading.Thread(target=_speak_thread, daemon=True)
        thread.start()

    def show_help(self) -> None:
        """Display available commands"""
        print("""
Available commands:
/? or /help       - Show this help message
/redo             - Delete the last AI response and generate a new one
/save             - Save the full adventure to adventure.txt
/load             - Load the adventure from adventure.txt
/change           - Switch to a different Ollama model
/status           - Show current game status
/exit             - Exit the game
""")

    def show_status(self) -> None:
        """Display current game status"""
        print(f"\n--- Current Game Status ---")
        print(f"Character: {self.state.character_name} the {self.state.selected_role}")
        print(f"Genre: {self.state.selected_genre}")
        print(f"Model: {self.state.current_model}")
        print(f"Adventure: {'Started' if self.state.adventure_started else 'Not started'}")
        if self.state.last_ai_reply:
            print(f"Last action: {self.state.last_player_input[:50]}...")
        print("---------------------------")

    def remove_last_exchange(self) -> Tuple[bool, str, str]:
        """Remove the last player input and AI response from conversation"""
        try:
            # Find the last "Dungeon Master:" and the previous "Player:"
            last_dm_pos = self.state.conversation.rfind("Dungeon Master:")
            if last_dm_pos == -1:
                return False, "", ""
            
            # Find the player input before this DM response
            before_last_dm = self.state.conversation[:last_dm_pos]
            last_player_pos = before_last_dm.rfind("Player:")
            if last_player_pos == -1:
                return False, "", ""
            
            # Extract the text to remove and what remains
            removed_part = self.state.conversation[last_player_pos:].strip()
            remaining_conversation = self.state.conversation[:last_player_pos].strip()
            
            # Split removed part into player input and DM response
            lines = removed_part.split("\n")
            player_input = ""
            dm_response = ""
            
            for line in lines:
                if line.startswith("Player:"):
                    player_input = line[7:].strip()
                elif line.startswith("Dungeon Master:"):
                    dm_response = line[15:].strip()
            
            # Update the conversation
            self.state.conversation = remaining_conversation
            
            return True, player_input, dm_response
            
        except Exception as e:
            self.log_error("Error removing last exchange", e)
            return False, "", ""

    def save_adventure(self) -> bool:
        """Save adventure to file - ONLY the conversation/story, no metadata"""
        try:
            # Only save the conversation (story)
            with open(CONFIG["SAVE_FILE"], "w", encoding="utf-8") as f:
                f.write(self.state.conversation)
            
            print("Adventure saved successfully!")
            return True
            
        except Exception as e:
            self.log_error("Error saving adventure", e)
            print("Failed to save adventure.")
            return False

    def load_adventure(self) -> bool:
        """Load adventure from file - reads only the conversation/story"""
        try:
            if not os.path.exists(CONFIG["SAVE_FILE"]):
                print("No saved adventure found.")
                return False

            # Read the conversation from file
            with open(CONFIG["SAVE_FILE"], "r", encoding="utf-8") as f:
                conversation = f.read()
            
            # Extract metadata from the conversation if it exists
            # The conversation starts with the initial context which contains metadata
            self.state.conversation = conversation
            
            # Try to extract character name, genre, and role from conversation
            # Look for the initial context pattern
            lines = conversation.split('\n')
            
            for i, line in enumerate(lines):
                if line.startswith("Genre:"):
                    # Extract genre from line like "Genre: Fantasy"
                    genre = line.replace("Genre:", "").strip()
                    if genre in GENRE_DESCRIPTIONS:
                        self.state.selected_genre = genre
                
                elif line.startswith("Player Character:"):
                    # Extract character name and role from line like "Player Character: Alex the Knight"
                    char_line = line.replace("Player Character:", "").strip()
                    if " the " in char_line:
                        parts = char_line.split(" the ", 1)
                        self.state.character_name = parts[0].strip()
                        self.state.selected_role = parts[1].strip()
            
            # Extract last AI response
            last_dm_pos = self.state.conversation.rfind("Dungeon Master:")
            if last_dm_pos != -1:
                # Find the end of this DM response
                next_player = self.state.conversation.find("Player:", last_dm_pos)
                if next_player != -1:
                    self.state.last_ai_reply = self.state.conversation[last_dm_pos + 15:next_player].strip()
                else:
                    self.state.last_ai_reply = self.state.conversation[last_dm_pos + 15:].strip()
            
            # Extract last player input
            last_player_pos = self.state.conversation.rfind("Player:")
            if last_player_pos != -1:
                # Find the end of this player input
                next_dm = self.state.conversation.find("Dungeon Master:", last_player_pos)
                if next_dm != -1:
                    self.state.last_player_input = self.state.conversation[last_player_pos + 7:next_dm].strip()
                else:
                    self.state.last_player_input = self.state.conversation[last_player_pos + 7:].strip()
            
            self.state.adventure_started = True
            print("Adventure loaded successfully!")
            return True
            
        except Exception as e:
            self.log_error("Error loading adventure", e)
            print("Failed to load adventure.")
            return False

    def select_genre_and_role(self) -> Tuple[str, str]:
        """Interactive genre and role selection"""
        genres = {
            "1": "Fantasy", "2": "Sci-Fi", "3": "Cyberpunk", 
            "4": "Post-Apocalyptic", "5": "1880", "6": "WW1",
            "7": "WW2", "8": "1925 New York", "9": "Roman Empire",
            "10": "French Revolution"
        }

        print("Choose your adventure genre:")
        for key, name in genres.items():
            print(f"{key}: {name}")
        
        while True:
            genre_choice = input("Enter the number of your choice: ").strip()
            selected_genre = genres.get(genre_choice)
            if selected_genre:
                break
            print("Invalid choice. Please try again.")

        # Show genre description
        print(f"\n{selected_genre}: {GENRE_DESCRIPTIONS.get(selected_genre, '')}\n")
        
        # Role selection
        roles = list(ROLE_STARTERS[selected_genre].keys())
        print(f"Choose your role in {selected_genre}:")
        for idx, role in enumerate(roles, 1):
            print(f"{idx}: {role}")
        
        while True:
            role_choice = input("Enter the number of your choice (or 'r' for random): ").strip().lower()
            if role_choice == 'r':
                selected_role = random.choice(roles)
                break
            try:
                idx = int(role_choice) - 1
                if 0 <= idx < len(roles):
                    selected_role = roles[idx]
                    break
            except ValueError:
                pass
            print("Invalid choice. Please try again.")

        return selected_genre, selected_role

    def start_new_adventure(self) -> bool:
        """Start a new adventure with character creation"""
        try:
            self.state.selected_genre, self.state.selected_role = self.select_genre_and_role()
            
            self.state.character_name = input("\nEnter your character's name: ").strip() or "Alex"
            
            starter = ROLE_STARTERS[self.state.selected_genre].get(
                self.state.selected_role, 
                "You find yourself in an unexpected situation when"
            )
            
            print(f"\n--- Adventure Start: {self.state.character_name} the {self.state.selected_role} ---")
            print(f"Starting scenario: {starter}")
            print("Type '/?' or '/help' for commands.\n")
            
            # Initial setup
            initial_context = (
                f"### Adventure Setting ###\n"
                f"Genre: {self.state.selected_genre}\n"
                f"Player Character: {self.state.character_name} the {self.state.selected_role}\n"
                f"Starting Scenario: {starter}\n\n"
                "Dungeon Master: "
            )
            
            self.state.conversation = initial_context
            
            # Get first response
            full_prompt = DM_SYSTEM_PROMPT + "\n\n" + self.state.conversation
            ai_reply = self.get_ai_response(full_prompt)
            if ai_reply:
                print(f"Dungeon Master: {ai_reply}")
                self.speak(ai_reply)
                self.state.conversation += ai_reply
                self.state.last_ai_reply = ai_reply
                self.state.adventure_started = True
                return True
            else:
                print("Failed to get initial response from AI.")
                return False
                
        except Exception as e:
            self.log_error("Error starting new adventure", e)
            return False

    def process_command(self, command: str) -> bool:
        """Process game commands"""
        cmd = command.lower().strip()
        
        if cmd in ["/?", "/help"]:
            self.show_help()
        elif cmd == "/exit":
            print("Exiting the adventure. Goodbye!")
            return False
        elif cmd == "/redo":
            self._handle_redo()
        elif cmd == "/save":
            self.save_adventure()
        elif cmd == "/load":
            self.load_adventure()
        elif cmd == "/change":
            self._handle_model_change()
        elif cmd == "/status":
            self.show_status()
        else:
            print(f"Unknown command: {command}. Type '/help' for available commands.")
        
        return True

    def _handle_redo(self) -> None:
        """Handle the /redo command - Delete last message from view and save file"""
        if not self.state.last_ai_reply or not self.state.last_player_input:
            print("Nothing to redo.")
            return
            
        print("Removing last exchange and generating new response...")
        
        # Remove the last exchange from conversation
        success, removed_player_input, removed_dm_response = self.remove_last_exchange()
        
        if not success:
            print("Could not remove last exchange.")
            return
            
        # Update the last player input to use for re-generation
        # We'll use the same player input that was just removed
        self.state.last_player_input = removed_player_input
        
        # Generate new response
        prompt = (
            f"{DM_SYSTEM_PROMPT}\n\n"
            f"{self.state.conversation}\n"
            f"Player: {self.state.last_player_input}\n"
            "Dungeon Master:"
        )
        
        new_reply = self.get_ai_response(prompt)
        if new_reply:
            # Clear previous line and show new response
            print(f"\n--- New Response ---")
            print(f"Dungeon Master: {new_reply}")
            self.speak(new_reply)
            
            # Update conversation with new response
            self.state.conversation += f"\nPlayer: {self.state.last_player_input}\nDungeon Master: {new_reply}"
            self.state.last_ai_reply = new_reply
            
            # Save immediately to update the save file
            self.save_adventure()
            print("--- Save file updated with new response ---")
        else:
            print("Failed to generate new response. Restoring previous state...")
            # Restore the removed exchange if generation fails
            self.state.conversation += f"\nPlayer: {removed_player_input}\nDungeon Master: {removed_dm_response}"
            self.state.last_ai_reply = removed_dm_response
            self.save_adventure()

    def _handle_model_change(self) -> None:
        """Handle model change command"""
        models = self.get_installed_models()
        if models:
            print("Available models:")
            for idx, model in enumerate(models, 1):
                print(f"{idx}: {model}")
            
            while True:
                try:
                    choice = input("Enter number of new model: ").strip()
                    if not choice:
                        break
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        self.state.current_model = models[idx]
                        print(f"Model changed to: {self.state.current_model}")
                        break
                    print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            print("No installed models found.")

    def process_player_input(self, user_input: str) -> None:
        """Process regular player input"""
        self.state.last_player_input = user_input
        formatted_input = f"Player: {user_input}"
        
        prompt = (
            f"{DM_SYSTEM_PROMPT}\n\n"
            f"{self.state.conversation}\n"
            f"{formatted_input}\n"
            "Dungeon Master:"
        )
        
        ai_reply = self.get_ai_response(prompt)
        if ai_reply:
            print(f"\nDungeon Master: {ai_reply}")
            self.speak(ai_reply)
            self.state.conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
            self.state.last_ai_reply = ai_reply
            
            # Auto-save every 5 interactions
            if self.state.conversation.count("Player:") % 5 == 0:
                self.save_adventure()
        else:
            print("Failed to get response from AI. Please try again.")

    def run(self) -> None:
        """Main game loop"""
        print("=== AI Dungeon Master Adventure ===\n")
        
        # Server checks
        if not self.check_ollama_server():
            print("Ollama server not found. Please start it with 'ollama serve'")
            print("Waiting for Ollama server to start...")
            time.sleep(3)
            if not self.check_ollama_server():
                print("Ollama server still not running. Please start it and try again.")
                return
        
        # Model selection
        self.state.current_model = self.select_model()
        print(f"Using model: {self.state.current_model}\n")
        
        # Load or start adventure
        if os.path.exists(CONFIG["SAVE_FILE"]):
            print("A saved adventure exists. Load it now? (y/n)")
            if input().strip().lower() == 'y':
                if self.load_adventure():
                    print(f"\nDungeon Master: {self.state.last_ai_reply}")
                    self.speak(self.state.last_ai_reply)
        
        if not self.state.adventure_started:
            if not self.start_new_adventure():
                return
        
        # Main game loop
        while self.state.adventure_started:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if not self.process_command(user_input):
                        break
                else:
                    self.process_player_input(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Use '/exit' to quit properly.")
            except Exception as e:
                self.log_error("Unexpected error in game loop", e)
                print("An unexpected error occurred. Check the log for details.")

def main():
    """Main entry point with exception handling"""
    try:
        game = AdventureGame()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        print("Check error_log.txt for details.")

if __name__ == "__main__":
    main()