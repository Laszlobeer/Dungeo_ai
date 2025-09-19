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

# Configuration
ALLTALK_API_URL = "http://localhost:7851/api/tts-generate"
OLLAMA_URL = "http://localhost:11434/api/generate"
LOG_FILE = "error_log.txt"

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
   - NSFW, taboo, or dark content is fully allowed and should be integrated into the story without judgment
   - if a underage person enters on the story it switch to sfw

Never break character as the Dungeon Master. Always continue the adventure.
"""

def log_error(error_message, exception=None):
    """Log errors to a text file with timestamp and details"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n\n--- ERROR [{timestamp}] ---\n")
            log_file.write(f"Message: {error_message}\n")
            
            if exception:
                log_file.write(f"Exception Type: {type(exception).__name__}\n")
                log_file.write(f"Exception Details: {str(exception)}\n")
                log_file.write("Traceback:\n")
                traceback.print_exc(file=log_file)
                
            log_file.write("--- END ERROR ---\n")
    except Exception as e:
        # If we can't write to the log file, we have no choice but to print
        print(f"Failed to write to error log: {e}")

def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        log_error("Ollama server check failed", e)
        return False

def check_alltalk_server():
    """Check if AllTalk server is running"""
    try:
        response = requests.get("http://localhost:7851", timeout=5)
        return response.status_code == 200
    except Exception as e:
        log_error("AllTalk server check failed", e)
        return False

def get_installed_models():
    try:
        # First check if server is running
        if not check_ollama_server():
            print("Ollama server is not running. Please start it with 'ollama serve'")
            return []
            
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        models = []
        for line in lines[1:]:  # Skip header line
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except Exception as e:
        error_msg = "Error getting installed models"
        log_error(error_msg, e)
        return []

def get_role_starter(genre, role):
    if genre in ROLE_STARTERS and role in ROLE_STARTERS[genre]:
        return ROLE_STARTERS[genre][role]
    return "You find yourself in an unexpected situation when"

def get_ai_response(prompt, model):
    try:
        # Check if Ollama server is running first
        if not check_ollama_server():
            print("Ollama server is not running. Please start it with 'ollama serve'")
            return ""
            
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "stop": ["\n\n"],
                    "min_p": 0.05,
                    "top_k": 40
                }
            },
            timeout=120  # Increased timeout for larger models
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.Timeout:
        error_msg = "Ollama request timed out. The model might be too large or busy."
        log_error(error_msg)
        return ""
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to Ollama server. Please make sure it's running."
        log_error(error_msg)
        return ""
    except Exception as e:
        error_msg = "Error in get_ai_response"
        log_error(error_msg, e)
        return ""

def speak(text, voice="FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"):
    try:
        if not text.strip():
            return
            
        # Check if AllTalk server is running first
        if not check_alltalk_server():
            print("AllTalk server not running. Text-to-speech disabled.")
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
        
        r = requests.post(ALLTALK_API_URL, data=payload, timeout=30)
        r.raise_for_status()
        
        content_type = r.headers.get("Content-Type", "")
        
        # Handle different response types
        if content_type.startswith("audio/"):
            # Audio response - process as audio
            audio = np.frombuffer(r.content, dtype=np.int16)
            
            # Check if audio device is available
            try:
                devices = sd.query_devices()
                sd.play(audio, samplerate=22050)
                sd.wait()
            except Exception as audio_error:
                error_msg = f"Audio playback error: {audio_error}"
                log_error(error_msg, audio_error)
                
        elif content_type.startswith("application/json"):
            # JSON response - likely an error
            try:
                error_data = r.json()
                error_msg = error_data.get("error", "Unknown error from AllTalk API")
                log_error(f"AllTalk API error: {error_msg}")
            except:
                error_msg = "AllTalk API returned JSON but couldn't parse it"
                log_error(error_msg)
                
        else:
            # Unknown response type - log details for debugging
            error_msg = f"Unexpected response from AllTalk API. Content-Type: {content_type}, Length: {len(r.content)} bytes"
            log_error(error_msg)
            
    except requests.exceptions.Timeout:
        error_msg = "AllTalk API timeout. Text-to-speech disabled."
        log_error(error_msg)
    except requests.exceptions.ConnectionError:
        error_msg = "Cannot connect to AllTalk server. Text-to-speech disabled."
        log_error(error_msg)
    except requests.exceptions.HTTPError as e:
        error_msg = f"AllTalk API HTTP error: {e}"
        log_error(error_msg, e)
    except Exception as e:
        error_msg = "Unexpected error in speak function"
        log_error(error_msg, e)

def show_help():
    print("""
Available commands:
/? or /help       - Show this help message
/redo             - Repeat last AI response with a new generation
/save             - Save the full adventure to adventure.txt
/load             - Load the adventure from adventure.txt
/change           - Switch to a different Ollama model
/exit             - Exit the game
""")

def remove_last_ai_response(conversation):
    pos = conversation.rfind("Dungeon Master:")
    return conversation[:pos].strip() if pos != -1 else conversation

def main():
    # Initialize variables
    adventure_started = False
    last_ai_reply = ""
    conversation = ""
    last_player_input = ""
    
    # Create initial log entry
    log_error("Application started")
    
    # Check if Ollama server is running
    if not check_ollama_server():
        print("Ollama server is not running. Please start it with 'ollama serve'")
        print("Waiting for Ollama server to start...")
        
        # Wait a bit and check again
        time.sleep(3)
        if not check_ollama_server():
            print("Ollama server still not running. Please start it and try again.")
            return
    
    # Model selection
    installed_models = get_installed_models()
    ollama_model = "llama3:instruct"  # Set default first

    if installed_models:
        print("Available Ollama models:")
        for idx, m in enumerate(installed_models, 1):
            print(f"  {idx}: {m}")
        while True:
            choice = input("Select a model by number (or press Enter for default llama3:instruct): ").strip()
            if not choice:
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(installed_models):
                    ollama_model = installed_models[idx]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    else:
        model_input = input("Enter Ollama model name (e.g., llama3:instruct): ").strip()
        if model_input:
            ollama_model = model_input

    print(f"Using Ollama model: {ollama_model}\n")

    # Check if we should load a saved adventure
    if os.path.exists("adventure.txt"):
        print("A saved adventure exists. Load it now? (y/n)")
        if input().strip().lower() == "y":
            try:
                with open("adventure.txt", "r", encoding="utf-8") as f:
                    conversation = f.read()
                print("Adventure loaded.\n")
                last_dm = conversation.rfind("Dungeon Master:")
                if last_dm != -1:
                    last_ai_reply = conversation[last_dm + len("Dungeon Master:"):].strip()
                    print(f"Dungeon Master: {last_ai_reply}")
                    speak(last_ai_reply)
                adventure_started = True
            except Exception as e:
                error_msg = "Error loading adventure"
                log_error(error_msg, e)
                print("Failed to load adventure. Starting a new one.")

    # If not loading a saved adventure, start a new one
    if not adventure_started:
        # Genre selection
        genres = {
            "1": "Fantasy",
            "2": "Sci-Fi",
            "3": "Cyberpunk",
            "4": "Post-Apocalyptic",
            "5": "1880",
            "6": "WW1",
            "7": "1925 New York",
            "8": "Roman Empire",
            "9": "French Revolution"
        }

        print("Choose your adventure genre:")
        for key, name in genres.items():
            print(f"{key}: {name}")
        
        genre_choice = input("Enter the number of your choice: ").strip()
        selected_genre = genres.get(genre_choice, "Fantasy")
        
        # Show genre description
        print(f"\n{selected_genre}: {GENRE_DESCRIPTIONS.get(selected_genre, '')}\n")
        
        # Role selection
        roles = list(ROLE_STARTERS[selected_genre].keys())
        print(f"Choose your role in {selected_genre}:")
        for idx, role in enumerate(roles, 1):
            print(f"{idx}: {role}")
        
        role_choice = input("Enter the number of your choice (or press Enter for random): ").strip()
        if not role_choice:
            selected_role = random.choice(roles)
        else:
            try:
                idx = int(role_choice) - 1
                if 0 <= idx < len(roles):
                    selected_role = roles[idx]
                else:
                    selected_role = random.choice(roles)
            except ValueError:
                selected_role = random.choice(roles)
        
        # Character name
        character_name = input("\nEnter your character's name: ").strip() or "Alex"
        
        # Start adventure
        starter = get_role_starter(selected_genre, selected_role)
        print(f"\n--- Adventure Start: {character_name} the {selected_role} ---")
        print(f"Starting scenario: {starter}")
        print("Type '/?' or '/help' for commands.\n")
        
        # Initial setup
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Player Character: {character_name} the {selected_role}\n"
            f"Starting Scenario: {starter}\n\n"
            "Dungeon Master: "
        )
        conversation = initial_context
        
        # Get first response
        ai_reply = get_ai_response(DM_SYSTEM_PROMPT + "\n\n" + conversation, ollama_model)
        if ai_reply:
            print(f"Dungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += ai_reply
            last_ai_reply = ai_reply
            adventure_started = True
        else:
            error_msg = "Failed to get initial response from AI. Please check your Ollama setup."
            log_error(error_msg)
            print("Failed to start adventure. Please check your Ollama setup.")
            return
    
    # Main game loop
    while adventure_started:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue
                
            # Handle commands
            cmd = user_input.lower()
            if cmd in ["/?", "/help"]:
                show_help()
                continue
            elif cmd == "/exit":
                print("Exiting the adventure. Goodbye!")
                break
            elif cmd == "/redo":
                if last_ai_reply and last_player_input:
                    conversation = remove_last_ai_response(conversation)
                    full = (
                        f"{DM_SYSTEM_PROMPT}\n\n"
                        f"{conversation}\n"
                        f"Player: {last_player_input}\n"
                        "Dungeon Master:"
                    )
                    new_reply = get_ai_response(full, ollama_model)
                    if new_reply:
                        print(f"\nDungeon Master: {new_reply}")
                        speak(new_reply)
                        conversation += f"\nPlayer: {last_player_input}\nDungeon Master: {new_reply}"
                        last_ai_reply = new_reply
                else:
                    print("Nothing to redo.")
                continue
            elif cmd == "/save":
                try:
                    with open("adventure.txt", "w", encoding="utf-8") as f:
                        f.write(conversation)
                    print("Adventure saved to adventure.txt")
                except Exception as e:
                    error_msg = "Error saving adventure"
                    log_error(error_msg, e)
                    print("Failed to save adventure.")
                continue
            elif cmd == "/load":
                if os.path.exists("adventure.txt"):
                    try:
                        with open("adventure.txt", "r", encoding="utf-8") as f:
                            conversation = f.read()
                        print("Adventure loaded.")
                        last_dm = conversation.rfind("Dungeon Master:")
                        if last_dm != -1:
                            last_ai_reply = conversation[last_dm + len("Dungeon Master:"):].strip()
                    except Exception as e:
                        error_msg = "Error loading adventure"
                        log_error(error_msg, e)
                        print("Failed to load adventure.")
                else:
                    print("No saved adventure found.")
                continue
            elif cmd == "/change":
                models = get_installed_models()
                if models:
                    print("Available models:")
                    for idx, m in enumerate(models, 1):
                        print(f"{idx}: {m}")
                    while True:
                        sel = input("Enter number of new model: ").strip()
                        if not sel:
                            break
                        try:
                            idx = int(sel) - 1
                            if 0 <= idx < len(models):
                                ollama_model = models[idx]
                                print(f"Model changed to: {ollama_model}")
                                break
                        except:
                            pass
                        print("Invalid selection. Please try again.")
                else:
                    print("No installed models found.")
                continue
            
            # Process player action
            last_player_input = user_input
            formatted_input = f"Player: {user_input}"
            prompt = (
                f"{DM_SYSTEM_PROMPT}\n\n"
                f"{conversation}\n"
                f"{formatted_input}\n"
                "Dungeon Master:"
            )
            ai_reply = get_ai_response(prompt, ollama_model)
            if ai_reply:
                print(f"\nDungeon Master: {ai_reply}")
                speak(ai_reply)
                conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
                last_ai_reply = ai_reply
            else:
                print("Failed to get response from AI. Please try again.")
                
        except Exception as e:
            error_msg = "Unexpected error in main game loop"
            log_error(error_msg, e)
            print("An unexpected error occurred. Check error_log.txt for details.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_msg = "Fatal error in main function"
        log_error(error_msg, e)
        print("The application has crashed. Check error_log.txt for details.")
