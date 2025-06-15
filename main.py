import random
import requests
import sounddevice as sd
import numpy as np
import os
import subprocess
import re
import logging
import datetime
from collections import defaultdict

# Configure logging
log_filename = f"rpg_adventure_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

ALLTALK_API_URL = "http://localhost:7851/api/tts-generate"

# Function to load banned words from file
def load_banwords():
    banwords = []
    try:
        if os.path.exists("banwords.txt"):
            with open("banwords.txt", "r", encoding="utf-8") as f:
                banwords = [line.strip().lower() for line in f if line.strip()]
            logging.info(f"Loaded {len(banwords)} banned words")
    except Exception as e:
        logging.error(f"Error loading banwords: {e}")
    return banwords

# Load banned words at startup
BANWORDS = load_banwords()

# Function to retrieve installed Ollama models via CLI
def get_installed_models():
    try:
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
        logging.error(f"Error getting installed models: {e}")
        return []

# Count subarrays with at most k distinct elements
def count_subarrays(arr, k):
    """Calculate number of subarrays with at most k distinct elements"""
    n = len(arr)
    left = 0
    distinct = 0
    freq = defaultdict(int)
    total = 0
    for right in range(n):
        if freq[arr[right]] == 0:
            distinct += 1
        freq[arr[right]] += 1

        while distinct > k:
            freq[arr[left]] -= 1
            if freq[arr[left]] == 0:
                distinct -= 1
            left += 1

        total += (right - left + 1)

    return total

# Initial model selection
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

# Role-specific starting scenarios
ROLE_STARTERS = {
    "Fantasy": {
        "Peasant": "You're toiling in the fields of a small village when",
        "Noble": "You're overseeing your estate's affairs when",
        "Mage": "You're studying ancient tomes in your tower when",
        "Knight": "You're training in the castle courtyard when",
        "Ranger": "You're tracking game in the deep forest when",
        "Thief": "You're casing a noble's manor in the city when",
        "Bard": "You're performing in a crowded tavern when",
        "Cleric": "You're tending to the sick in the temple when",
        "Assassin": "You're preparing for a contract in the shadows when",
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
    }
}

def get_role_starter(genre, role):
    """Get a role-specific starting scenario"""
    if genre in ROLE_STARTERS and role in ROLE_STARTERS[genre]:
        return ROLE_STARTERS[genre][role]

    generic_starters = {
        "Fantasy": "You're going about your daily duties when",
        "Sci-Fi": "You're performing routine tasks aboard your vessel when",
        "Cyberpunk": "You're navigating the neon-lit streets when",
        "Post-Apocalyptic": "You're surviving in the wasteland when"
    }

    if genre in generic_starters:
        return generic_starters[genre]

    return "You find yourself in an unexpected situation when"

genres = {
    "1": ("Fantasy", [
        "Noble", "Peasant", "Mage", "Knight", "Ranger", "Alchemist", "Thief", "Bard",
        "Cleric", "Druid", "Assassin", "Paladin", "Warlock", "Monk", "Sorcerer",
        "Beastmaster", "Enchanter", "Blacksmith", "Merchant", "Gladiator", "Wizard"
    ]),
    "2": ("Sci-Fi", [
        "Space Marine", "Scientist", "Android", "Pilot", "Engineer", "Alien Diplomat",
        "Space Pirate", "Navigator", "Medic", "Robot Technician", "Cybernetic Soldier",
        "Explorer", "Astrobiologist", "Quantum Hacker", "Starship Captain",
        "Galactic Trader", "AI Specialist", "Terraformer", "Cyberneticist", "Bounty Hunter"
    ]),
    "3": ("Cyberpunk", [
        "Hacker", "Street Samurai", "Corporate Agent", "Techie", "Rebel Leader",
        "Drone Operator", "Synth Dealer", "Information Courier", "Augmentation Engineer",
        "Black Market Dealer", "Scumbag", "Police", "Cyborg"
    ]),
    "4": ("Post-Apocalyptic", [
        "Survivor", "Scavenger", "Mutant", "Trader", "Raider", "Medic",
        "Cult Leader", "Berserker", "Soldier"
    ]),
    "5": ("Random", [])
}

# Player choices structure to track story elements
player_choices_template = {
    "allies": [],
    "enemies": [],
    "discoveries": [],
    "reputation": 0,
    "resources": {},
    "factions": defaultdict(int),
    "completed_quests": [],
    "active_quests": [],
    "world_events": [],
    "consequences": []
}

# Enhanced DM system prompt focusing on immediate consequences
DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master. Your role is to provide IMMEDIATE and PERMANENT consequences for every player action. Follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - EVERY player action MUST have an immediate consequence
   - Consequences must permanently change the game world
   - Describe consequences in the next response without delay
   - Small actions create ripple effects through the narrative

2. RESPONSE STRUCTURE:
   a) Immediate consequence (What happens right now)
   b) New situation (What the player sees now)
   c) Next challenges (What happens next)

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change permanently based on actions
   - Player choices open/close future narrative paths
   - Resources are gained/lost permanently

4. ACTION EXAMPLES:
   Player: "I kill the guard"
   Consequence: "The guard falls dead, alerting nearby soldiers. 
                The castle entrance is now unguarded but reinforcements approach. 
                You hear shouts coming from the west corridor."

   Player: "I steal the artifact"
   Consequence: "Alarms blare as the temple begins to collapse. 
                You pocket the glowing artifact but debris blocks the exit. 
                The high priest shouts curses from the crumbling balcony."

   Player: "I persuade the king"
   Consequence: "The king nods and grants your request. 
                His advisor glares suspiciously but hands you the royal seal. 
                Guards open the throne room doors to the courtyard."
"""

def get_current_state(player_choices):
    """Generate a string representation of the current world state"""
    state = [
        f"### Current World State ###",
        f"Allies: {', '.join(player_choices['allies']) if player_choices['allies'] else 'None'}",
        f"Enemies: {', '.join(player_choices['enemies']) if player_choices['enemies'] else 'None'}",
        f"Reputation: {player_choices['reputation']}",
        f"Active Quests: {', '.join(player_choices['active_quests']) if player_choices['active_quests'] else 'None'}",
        f"Completed Quests: {', '.join(player_choices['completed_quests']) if player_choices['completed_quests'] else 'None'}",
    ]
    
    # Add resources if any exist
    if player_choices['resources']:
        state.append("Resources:")
        for resource, amount in player_choices['resources'].items():
            state.append(f"  - {resource}: {amount}")
    
    # Add faction relationships if any exist
    if player_choices['factions']:
        state.append("Faction Relationships:")
        for faction, level in player_choices['factions'].items():
            state.append(f"  - {faction}: {'+' if level > 0 else ''}{level}")
    
    # Add recent world events
    if player_choices['world_events']:
        state.append("Recent World Events:")
        for event in player_choices['world_events'][-3:]:
            state.append(f"  - {event}")
    
    # Add recent consequences
    if player_choices['consequences']:
        state.append("Recent Consequences:")
        for cons in player_choices['consequences'][-3:]:
            state.append(f"  - {cons}")
    
    return "\n".join(state)

def get_ai_response(prompt, model=ollama_model, censored=False):
    try:
        if censored:
            prompt += "\n[IMPORTANT: Content must be strictly family-friendly. Avoid any NSFW themes, violence, or mature content.]"

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 250,
                    "stop": ["\n\n"],
                    "min_p": 0.05,
                    "top_k": 40
                }
            },
            timeout=60
        )
        response.raise_for_status()
        json_resp = response.json()
        return json_resp.get("response", "").strip()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Ollama: {e}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error in get_ai_response: {e}")
        return ""

def speak(text, voice="FemaleBritishAccent_WhyLucyWhy_Voice_2.wav"):
    try:
        if not text.strip():
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
        response = requests.post(ALLTALK_API_URL, data=payload, timeout=20)
        response.raise_for_status()

        if response.headers.get("Content-Type", "").startswith("audio/"):
            audio_data = np.frombuffer(response.content, dtype=np.int16)
            sd.play(audio_data, samplerate=22050)
            sd.wait()
        else:
            logging.error(f"Unexpected response content type: {response.headers.get('Content-Type')}")
    except Exception as e:
        logging.error(f"Error in speech generation: {e}")

def show_help():
    print("""
Available commands:
/? or /help       - Show this help message
/censored         - Toggle content filtering (SFW/NSFW mode)
/redo             - Repeat last AI response with a new generation
/save             - Save the full adventure to adventure.txt
/load             - Load the adventure from adventure.txt
/change           - Switch to a different Ollama model
/count            - Calculate subarrays with at most k distinct elements
/exit             - Exit the game
/consequences     - Show recent consequences of your actions
/state            - Show current world state

Story Adaptation:
Every action you take will permanently change the story:
  - Killing characters removes them permanently
  - Stealing items adds them to your inventory
  - Choices affect NPC attitudes and world events
  - Environments change based on your actions
  - Resources are permanently gained or lost
""")

def remove_last_ai_response(conversation):
    pos = conversation.rfind("Dungeon Master:")
    if pos == -1:
        return conversation

    start_pos = conversation.rfind("\n\n", 0, pos)
    if start_pos == -1:
        start_pos = 0
    else:
        start_pos += 2

    return conversation[:start_pos].strip()

def sanitize_response(response, censored=False):
    if not response:
        return "The story continues..."

    question_phrases = [
        "what will you do", "how do you respond", "what do you do",
        "what is your next move", "what would you like to do",
        "what would you like to say", "how will you proceed"
    ]

    for phrase in question_phrases:
        pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
        response = pattern.sub('', response)

    if censored:
        for word in BANWORDS:
            if word:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                response = pattern.sub('****', response)

    response = re.sub(r'\s{2,}', ' ', response).strip()

    if response and response[-1] not in ('.', '!', '?', ':', ','):
        response += '.'

    # Remove state tracking markers if any
    response = re.sub(r'\[[^\]]*State Tracking[^\]]*\]', '', response)
    
    return response

def update_world_state(action, response, player_choices):
    """Update world state based on player action and consequence"""
    # Record the consequence
    consequence = response.split('.')[0] if '.' in response else response
    player_choices['consequences'].append(f"After '{action}': {consequence}")
    
    # Keep only the last 5 consequences
    if len(player_choices['consequences']) > 5:
        player_choices['consequences'] = player_choices['consequences'][-5:]
    
    # Update allies
    ally_matches = re.findall(r'(\b[A-Z][a-z]+\b) (?:joins|helps|saves|allies with|becomes your ally)', response, re.IGNORECASE)
    for ally in ally_matches:
        if ally not in player_choices['allies']:
            player_choices['allies'].append(ally)
            # Remove from enemies if now an ally
            if ally in player_choices['enemies']:
                player_choices['enemies'].remove(ally)
    
    # Update enemies
    enemy_matches = re.findall(r'(\b[A-Z][a-z]+\b) (?:dies|killed|falls|perishes|becomes your enemy|turns against you)', response, re.IGNORECASE)
    for enemy in enemy_matches:
        if enemy not in player_choices['enemies']:
            player_choices['enemies'].append(enemy)
        # Remove from allies if now an enemy
        if enemy in player_choices['allies']:
            player_choices['allies'].remove(enemy)
    
    # Update resources
    resource_matches = re.findall(r'(?:get|find|acquire|obtain|receive|gain) (\d+) (\w+)', response, re.IGNORECASE)
    for amount, resource in resource_matches:
        resource = resource.lower()
        if resource not in player_choices['resources']:
            player_choices['resources'][resource] = 0
        player_choices['resources'][resource] += int(amount)
    
    # Update lost resources
    lost_matches = re.findall(r'(?:lose|drop|spend|use|expend) (\d+) (\w+)', response, re.IGNORECASE)
    for amount, resource in lost_matches:
        resource = resource.lower()
        if resource in player_choices['resources']:
            player_choices['resources'][resource] = max(0, player_choices['resources'][resource] - int(amount))

    # Update world events
    world_event_matches = re.findall(r'(?:The|A) (\w+ \w+) (?:is|has been) (destroyed|created|changed|revealed|altered)', response, re.IGNORECASE)
    for location, event in world_event_matches:
        player_choices['world_events'].append(f"{location} {event}")
    
    # Update quests
    if "quest completed" in response.lower():
        # Try to extract quest name
        quest_match = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been) completed', response, re.IGNORECASE)
        if quest_match:
            quest_name = quest_match.group(1)
            if quest_name in player_choices['active_quests']:
                player_choices['active_quests'].remove(quest_name)
                player_choices['completed_quests'].append(quest_name)
    
    if "new quest" in response.lower():
        # Try to extract quest name
        quest_match = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been) (?:given|started)', response, re.IGNORECASE)
        if quest_match:
            quest_name = quest_match.group(1)
            if quest_name not in player_choices['active_quests'] and quest_name not in player_choices['completed_quests']:
                player_choices['active_quests'].append(quest_name)
    
    # Update reputation
    if "reputation increases" in response.lower() or "reputation improved" in response.lower():
        player_choices['reputation'] += 1
    elif "reputation decreases" in response.lower() or "reputation damaged" in response.lower():
        player_choices['reputation'] = max(-5, player_choices['reputation'] - 1)
    
    # Update factions
    faction_matches = re.findall(r'(?:The|Your) (\w+) faction (?:likes|respects|trusts) you more', response, re.IGNORECASE)
    for faction in faction_matches:
        player_choices['factions'][faction] += 1
    
    faction_loss_matches = re.findall(r'(?:The|Your) (\w+) faction (?:dislikes|distrusts|hates) you more', response, re.IGNORECASE)
    for faction in faction_loss_matches:
        player_choices['factions'][faction] -= 1

def main():
    global ollama_model, BANWORDS
    censored = False
    last_ai_reply = ""
    conversation = ""
    character_name = "Laszlo"
    selected_genre = ""
    role = ""
    adventure_started = False

    # Initialize player choices
    player_choices = {
        "allies": [],
        "enemies": [],
        "discoveries": [],
        "reputation": 0,
        "resources": {},
        "factions": defaultdict(int),
        "completed_quests": [],
        "active_quests": [],
        "world_events": [],
        "consequences": []
    }

    if os.path.exists("adventure.txt"):
        print("A saved adventure exists. Load it now? (y/n)")
        if input().strip().lower() == "y":
            try:
                with open("adventure.txt", "r", encoding="utf-8") as f:
                    conversation = f.read()
                print("Adventure loaded.\n")
                last_dm_pos = conversation.rfind("Dungeon Master:")
                if last_dm_pos != -1:
                    reply = conversation[last_dm_pos + len("Dungeon Master:"):].strip()
                    print(f"Dungeon Master: {reply}")
                    speak(reply)
                    last_ai_reply = reply
                    adventure_started = True
                    
                    # Extract world state from saved file
                    if "### Persistent World State ###" in conversation:
                        state_section = conversation.split("### Persistent World State ###")[1]
                        # Simplified parsing
                        if "Allies:" in state_section:
                            allies_line = state_section.split("Allies:")[1].split("\n")[0].strip()
                            if allies_line != "None":
                                player_choices["allies"] = [a.strip() for a in allies_line.split(",")]
                        if "Enemies:" in state_section:
                            enemies_line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                            if enemies_line != "None":
                                player_choices["enemies"] = [e.strip() for e in enemies_line.split(",")]
                        if "Resources:" in state_section:
                            resources_lines = state_section.split("Resources:")[1].split("\n")
                            for line in resources_lines:
                                if line.strip().startswith("-"):
                                    parts = line.strip().split(":")
                                    if len(parts) >= 2:
                                        resource = parts[0].replace("-", "").strip()
                                        amount = parts[1].strip()
                                        if amount.isdigit():
                                            player_choices["resources"][resource] = int(amount)
                        if "Consequences:" in state_section:
                            cons_lines = state_section.split("Consequences:")[1].split("\n")
                            for line in cons_lines:
                                if line.strip().startswith("-"):
                                    player_choices["consequences"].append(line.replace("-", "").strip())
            except Exception as e:
                logging.error(f"Error loading adventure: {e}")
                print("Error loading adventure. Details logged.")

    if not adventure_started:
        print("Choose your adventure genre:")
        for key, (g, _) in genres.items():
            print(f"{key}: {g}")
        while True:
            gc = input("Enter the number of your choice: ").strip()
            if gc in genres:
                selected_genre, roles = genres[gc]
                if selected_genre == "Random":
                    # Properly handle random genre selection
                    available = [v for k, v in genres.items() if k != "5"]
                    selected_genre, roles = random.choice(available)
                break
            print("Invalid selection. Please try again.")

        # Ensure roles list is populated for all cases
        if not roles:
            for key, (g, rl) in genres.items():
                if g == selected_genre:
                    roles = rl
                    break

        print("\nChoose your character's role:")
        for i, r in enumerate(roles, 1):
            print(f"{i}: {r}")
        while True:
            choice = input("Enter the number of your choice (or press Enter for random): ").strip()
            if not choice:
                role = random.choice(roles)
                break
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(roles):
                    role = roles[idx]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        character_name = input("\nEnter your character's name: ").strip() or "Alex"

        role_starter = get_role_starter(selected_genre, role)
        print(f"\n--- Adventure Start: {character_name} the {role} ---")
        print(f"Starting scenario: {role_starter}")
        print("Type '/?' or '/help' for commands.\n")
        print("Content filtering is currently OFF (NSFW mode)")

        # Build initial context
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Player Character: {character_name} the {role}\n"
            f"Starting Scenario: {role_starter}\n"
        )
        conversation = DM_SYSTEM_PROMPT + "\n\n" + initial_context + "\n\nDungeon Master: "

        ai_reply = get_ai_response(conversation, ollama_model, censored)
        if ai_reply:
            ai_reply = sanitize_response(ai_reply, censored)
            print(f"Dungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += ai_reply
            last_ai_reply = ai_reply
            
            # Update world state based on initial response
            player_choices['consequences'].append(f"Start: {ai_reply.split('.')[0]}")
            
            adventure_started = True

    while adventure_started:
        try:
            user_input = input("\n> ").strip()
            if not user_input:
                continue

            cmd = user_input.lower()

            if cmd in ["/?", "/help"]:
                show_help()
                continue

            if cmd == "/exit":
                print("Exiting the adventure. Goodbye!")
                break

            if cmd == "/censored":
                censored = not censored
                mode = "ON (SFW)" if censored else "OFF (NSFW)"
                print(f"Content filtering {mode}.")
                if censored:
                    BANWORDS = load_banwords()
                continue
                    
            if cmd == "/consequences":
                print("\nRecent Consequences of Your Actions:")
                if player_choices['consequences']:
                    for i, cons in enumerate(player_choices['consequences'][-5:], 1):
                        print(f"{i}. {cons}")
                else:
                    print("No consequences recorded yet.")
                continue
                    
            if cmd == "/state":
                print("\nCurrent World State:")
                print(get_current_state(player_choices))
                continue

            if cmd == "/redo":
                if last_ai_reply:
                    conversation = remove_last_ai_response(conversation)
                    conversation += "\n\nDungeon Master:"
                    ai_reply = get_ai_response(conversation, ollama_model, censored)
                    if ai_reply:
                        ai_reply = sanitize_response(ai_reply, censored)
                        print(f"Dungeon Master: {ai_reply}")
                        speak(ai_reply)
                        conversation += f" {ai_reply}"
                        last_ai_reply = ai_reply
                else:
                    print("Nothing to redo.")
                continue

            if cmd == "/save":
                try:
                    # Save conversation with current world state
                    with open("adventure.txt", "w", encoding="utf-8") as f:
                        f.write(conversation)
                        f.write("\n\n### Persistent World State ###\n")
                        f.write(get_current_state(player_choices))
                    print("Adventure saved to adventure.txt")
                except Exception as e:
                    logging.error(f"Error saving adventure: {e}")
                    print("Error saving adventure. Details logged.")
                continue

            if cmd == "/load":
                if os.path.exists("adventure.txt"):
                    try:
                        with open("adventure.txt", "r", encoding="utf-8") as f:
                            conversation = f.read()
                        print("Adventure loaded.")
                        last_dm_pos = conversation.rfind("Dungeon Master:")
                        if last_dm_pos != -1:
                            last_ai_reply = conversation[last_dm_pos + len("Dungeon Master:"):].strip()
                        
                        # Extract world state from saved file
                        if "### Persistent World State ###" in conversation:
                            state_section = conversation.split("### Persistent World State ###")[1]
                            # Simplified parsing
                            if "Allies:" in state_section:
                                allies_line = state_section.split("Allies:")[1].split("\n")[0].strip()
                                if allies_line != "None":
                                    player_choices["allies"] = [a.strip() for a in allies_line.split(",")]
                            if "Enemies:" in state_section:
                                enemies_line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                                if enemies_line != "None":
                                    player_choices["enemies"] = [e.strip() for e in enemies_line.split(",")]
                            if "Resources:" in state_section:
                                resources_lines = state_section.split("Resources:")[1].split("\n")
                                for line in resources_lines:
                                    if line.strip().startswith("-"):
                                        parts = line.strip().split(":")
                                        if len(parts) >= 2:
                                            resource = parts[0].replace("-", "").strip()
                                            amount = parts[1].strip()
                                            if amount.isdigit():
                                                player_choices["resources"][resource] = int(amount)
                            if "Consequences:" in state_section:
                                cons_lines = state_section.split("Consequences:")[1].split("\n")
                                for line in cons_lines:
                                    if line.strip().startswith("-"):
                                        player_choices["consequences"].append(line.replace("-", "").strip())
                    except Exception as e:
                        logging.error(f"Error loading adventure: {e}")
                        print("Error loading adventure. Details logged.")
                else:
                    print("No saved adventure found.")
                continue

            if cmd == "/change":
                installed_models = get_installed_models()
                if installed_models:
                    print("Available models:")
                    for idx, m in enumerate(installed_models, 1):
                        print(f"{idx}: {m}")
                    while True:
                        choice = input("Enter number of new model: ").strip()
                        if not choice:
                            break
                        try:
                            idx = int(choice) - 1
                            if 0 <= idx < len(installed_models):
                                ollama_model = installed_models[idx]
                                print(f"Model changed to: {ollama_model}")
                                break
                        except ValueError:
                            pass
                        print("Invalid selection. Please try again.")
                else:
                    print("No installed models found. Using current model.")
                continue

            if cmd == "/count":
                try:
                    arr_input = input("Enter integers separated by spaces: ").strip()
                    k_input = input("Enter k value: ").strip()

                    arr = list(map(int, arr_input.split()))
                    k = int(k_input)

                    result = count_subarrays(arr, k)
                    print(f"Number of subarrays with at most {k} distinct elements: {result}")
                except Exception as e:
                    print(f"Error: {e}. Please enter valid integers.")
                continue

            # Format user input as action
            formatted_input = f"Player: {user_input}"
            
            # Build conversation with current world state
            state_context = get_current_state(player_choices)
            full_conversation = (
                f"{DM_SYSTEM_PROMPT}\n\n"
                f"### Current World State ###\n{state_context}\n\n"
                f"{conversation}\n"
                f"{formatted_input}\n"
                "Dungeon Master:"
            )
            
            # Get AI response with state context
            ai_reply = get_ai_response(full_conversation, ollama_model, censored)
            
            if ai_reply:
                ai_reply = sanitize_response(ai_reply, censored)
                print(f"\nDungeon Master: {ai_reply}")
                speak(ai_reply)
                
                # Update conversation
                conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
                last_ai_reply = ai_reply
                
                # Update world state based on player action and consequence
                update_world_state(user_input, ai_reply, player_choices)
                
                # Show immediate consequence
                consequence = ai_reply.split('.')[0] if '.' in ai_reply else ai_reply
                print(f"\n[Consequence of your action]")
                print(f"- {consequence}")
                
                # Show updated world state summary
                print("\n[World Changed]")
                if player_choices['consequences']:
                    print(f"- {player_choices['consequences'][-1]}")
                if player_choices['resources']:
                    print(f"- Resources: {', '.join([f'{k}:{v}' for k, v in player_choices['resources'].items()])}")
                if player_choices['allies']:
                    print(f"- Allies: {', '.join(player_choices['allies'])}")
                if player_choices['enemies']:
                    print(f"- Enemies: {', '.join(player_choices['enemies'])}")

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            print("An unexpected error occurred. The adventure continues...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        print("A critical error occurred. Please check the log file for details.")
