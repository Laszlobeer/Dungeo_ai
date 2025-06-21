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
MAX_CONTEXT_TOKENS = 6000  # Target context length

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

# Approximate token count (1 token ~ 4 characters in English)
def count_tokens(text):
    return len(text) // 4

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

# Enhanced DM system prompt focusing on narration only
DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master. Your role is to narrate the consequences of player actions. Follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - Describe ONLY the consequences of the player's action
   - Never perform actions on behalf of the player
   - Consequences must permanently change the game world
   - Narrate consequences naturally within the story flow
   - Small actions create ripple effects through the narrative

2. RESPONSE STYLE:
   - Describe what happens in the world as a result of the player's action
   - Do not describe the player performing actions - the player has already stated their action
   - Never use labels like "a)", "b)", "c)" - narrate everything naturally
   - Do not explicitly ask what the player does next

3. WORLD EVOLUTION:
   - NPCs remember player choices and react accordingly
   - Environments change permanently based on actions
   - Player choices open/close future narrative paths
   - Resources are gained/lost permanently
   - Player actions can fundamentally alter the story direction

4. PLAYER AGENCY:
   - Never say "you can't do that" - instead show the consequence of the attempt
   - Allow players to attempt any action, no matter how unexpected
   - If an action seems impossible, narrate why it fails and its consequences
   - Let players break quests, destroy locations, or alter factions

Example:
Player: "I attack the guard"
DM: "The guard parries your blow and calls for reinforcements. Three more guards appear from around the corner."

Player: "I try to pick the lock"
DM: "After several tense moments, you hear a satisfying click as the lock opens. The door creaks slightly as it swings inward."

Player: "I offer the merchant gold"
DM: "The merchant's eyes light up as he takes your gold. 'This will do nicely,' he says, handing you the artifact."
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

def get_ai_response(prompt, model=ollama_model):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
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
  - You can attempt ANY action, no matter how unconventional
  - The story adapts dynamically to your choices
""")

def remove_last_ai_response(conversation):
    pos = conversation.rfind("Dungeon Master:")
    if pos == -1:
        return conversation

    return conversation[:pos].strip()

def sanitize_response(response):
    if not response:
        return "The story continues..."

    # Remove any explicit question prompts
    question_phrases = [
        r"what will you do", r"how do you respond", r"what do you do",
        r"what is your next move", r"what would you like to do",
        r"what would you like to say", r"how will you proceed",
        r"do you:", r"choose one", r"select an option", r"pick one"
    ]

    for phrase in question_phrases:
        pattern = re.compile(rf'{phrase}.*?$', re.IGNORECASE)
        response = pattern.sub('', response)

    # Remove any explicit structure markers
    structure_phrases = [
        r"a\)", r"b\)", r"c\)", r"d\)", r"e\)", r"option [a-e]:",
        r"immediate consequence:", r"new situation:", r"next challenges:",
        r"choices:", r"options:"
    ]
    for phrase in structure_phrases:
        pattern = re.compile(phrase, re.IGNORECASE)
        response = pattern.sub('', response)

    # Remove player action descriptions
    player_action_patterns = [
        r"you (?:try to|attempt to|begin to|start to|decide to) .+?\.", 
        r"you (?:successfully|carefully|quickly) .+?\.", 
        r"you (?:manage to|fail to) .+?\."
    ]
    
    for pattern in player_action_patterns:
        response = re.sub(pattern, '', response, flags=re.IGNORECASE)

    # Remove multiple-choice blocks
    response = re.sub(
        r'(?:\n|\. )?[A-Ea-e]\)[^\.\?\!\n]*(\n|\. |$)', 
        '', 
        response,
        flags=re.IGNORECASE
    )
    
    # Remove "something else" options
    response = re.sub(
        r'(?:something else|other) \(.*?\)', 
        '', 
        response, 
        flags=re.IGNORECASE
    )

    # Clean up extra spaces
    response = re.sub(r'\s{2,}', ' ', response).strip()

    # Ensure proper punctuation
    if response and response[-1] not in ('.', '!', '?', ':', ','):
        response += '.'
    
    # Remove state tracking markers if any
    response = re.sub(r'\[[^\]]*State Tracking[^\]]*\]', '', response)
    
    return response

def update_world_state(action, response, player_choices):
    """Update world state based on player action and consequence"""
    # Record the consequence
    player_choices['consequences'].append(f"After '{action}': {response}")
    
    # Keep only the last 5 consequences
    if len(player_choices['consequences']) > 5:
        player_choices['consequences'] = player_choices['consequences'][-5:]
    
    # Update allies
    ally_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:joins|helps|saves|allies with|becomes your ally|supports you)',
        response, 
        re.IGNORECASE
    )
    for ally in ally_matches:
        if ally not in player_choices['allies']:
            player_choices['allies'].append(ally)
            if ally in player_choices['enemies']:
                player_choices['enemies'].remove(ally)
    
    # Update enemies
    enemy_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:dies|killed|falls|perishes|becomes your enemy|turns against you|hates you)',
        response, 
        re.IGNORECASE
    )
    for enemy in enemy_matches:
        if enemy not in player_choices['enemies']:
            player_choices['enemies'].append(enemy)
        if enemy in player_choices['allies']:
            player_choices['allies'].remove(enemy)
    
    # Update resources (more flexible matching)
    resource_matches = re.findall(
        r'(?:get|find|acquire|obtain|receive|gain|steal|take) (\d+) (\w+)',
        response, 
        re.IGNORECASE
    )
    for amount, resource in resource_matches:
        resource = resource.lower()
        player_choices['resources'].setdefault(resource, 0)
        player_choices['resources'][resource] += int(amount)
    
    # Update lost resources (more flexible matching)
    lost_matches = re.findall(
        r'(?:lose|drop|spend|use|expend|give|donate|surrender) (\d+) (\w+)',
        response, 
        re.IGNORECASE
    )
    for amount, resource in lost_matches:
        resource = resource.lower()
        if resource in player_choices['resources']:
            player_choices['resources'][resource] = max(0, player_choices['resources'][resource] - int(amount))

    # Update world events (more flexible matching)
    world_event_matches = re.findall(
        r'(?:The|A|An) (\w+ \w+) (?:is|has been|becomes) (destroyed|created|changed|revealed|altered|ruined|rebuilt)',
        response, 
        re.IGNORECASE
    )
    for location, event in world_event_matches:
        player_choices['world_events'].append(f"{location} {event}")
    
    # Update quests (more flexible matching)
    if "quest completed" in response.lower() or "completed the quest" in response.lower():
        quest_match = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been) completed', response, re.IGNORECASE)
        if quest_match:
            quest_name = quest_match.group(1)
            if quest_name in player_choices['active_quests']:
                player_choices['active_quests'].remove(quest_name)
                player_choices['completed_quests'].append(quest_name)
    
    if "new quest" in response.lower() or "quest started" in response.lower():
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
    faction_matches = re.findall(
        r'(?:The|Your) (\w+) faction (?:likes|respects|trusts|appreciates) you more', 
        response, 
        re.IGNORECASE
    )
    for faction in faction_matches:
        player_choices['factions'][faction] += 1
    
    faction_loss_matches = re.findall(
        r'(?:The|Your) (\w+) faction (?:dislikes|distrusts|hates|condemns) you more', 
        response, 
        re.IGNORECASE
    )
    for faction in faction_loss_matches:
        player_choices['factions'][faction] -= 1
        
    # Add dynamic discoveries
    discovery_matches = re.findall(
        r'(?:discover|find|uncover|learn about|reveal) (?:a |an |the )?(.+?)\.', 
        response, 
        re.IGNORECASE
    )
    for discovery in discovery_matches:
        if discovery not in player_choices['discoveries']:
            player_choices['discoveries'].append(discovery)

def main():
    global ollama_model
    last_ai_reply = ""
    conversation = ""
    character_name = "Laszlo"
    selected_genre = ""
    role = ""
    adventure_started = False
    last_player_input = ""

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

        # Build initial context
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Player Character: {character_name} the {role}\n"
            f"Starting Scenario: {role_starter}\n"
        )
        conversation = initial_context + "\n\nDungeon Master: "

        ai_reply = get_ai_response(DM_SYSTEM_PROMPT + "\n\n" + conversation)
        if ai_reply:
            ai_reply = sanitize_response(ai_reply)
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
                if last_ai_reply and last_player_input:
                    # Save current conversation length to restore if needed
                    original_length = len(conversation)
                    
                    # Remove last AI response
                    conversation = remove_last_ai_response(conversation)
                    
                    # Build full context for redo
                    state_context = get_current_state(player_choices)
                    full_conversation = (
                        f"{DM_SYSTEM_PROMPT}\n\n"
                        f"### Current World State ###\n{state_context}\n\n"
                        f"{conversation}\n"
                        f"Player: {last_player_input}\n"
                        "Dungeon Master:"
                    )
                    
                    # Get new AI response
                    ai_reply = get_ai_response(full_conversation)
                    if ai_reply:
                        ai_reply = sanitize_response(ai_reply)
                        print(f"\nDungeon Master: {ai_reply}")
                        speak(ai_reply)
                        
                        # Update conversation
                        conversation += f"\nPlayer: {last_player_input}\nDungeon Master: {ai_reply}"
                        last_ai_reply = ai_reply
                        
                        # Update world state with new consequence
                        update_world_state(last_player_input, ai_reply, player_choices)
                    else:
                        # Restore original conversation if generation failed
                        conversation = conversation[:original_length]
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
            last_player_input = user_input
            
            # Build base prompt components
            state_context = get_current_state(player_choices)
            base_prompt = (
                f"{DM_SYSTEM_PROMPT}\n\n"
                f"### Current World State ###\n{state_context}\n\n"
            )
            variable_part = f"{conversation}\n{formatted_input}\nDungeon Master:"
            
            # Calculate token count
            tokens = count_tokens(base_prompt + variable_part)
            
            # Truncate conversation if needed while preserving key elements
            if tokens > MAX_CONTEXT_TOKENS:
                # Find important sections to preserve
                preserve_sections = []
                
                # Preserve character setup
                if "Adventure Setting" in conversation:
                    start_idx = conversation.find("### Adventure Setting ###")
                    end_idx = conversation.find("\n\n", start_idx)
                    if end_idx == -1:
                        end_idx = len(conversation)
                    preserve_sections.append(conversation[start_idx:end_idx])
                
                # Preserve recent consequences (last 3)
                if "Recent Consequences:" in state_context:
                    start_idx = state_context.find("Recent Consequences:")
                    preserve_sections.append(state_context[start_idx:])
                
                # Preserve world state summary
                if "Current World State" in state_context:
                    start_idx = state_context.find("### Current World State ###")
                    preserve_sections.append(state_context[start_idx:])
                
                # Preserve last 2 interactions
                last_interactions = []
                dm_occurrences = [m.start() for m in re.finditer(r'Dungeon Master:', conversation)]
                if len(dm_occurrences) > 2:
                    # Get position of third-to-last DM response
                    start_idx = dm_occurrences[-3]
                    last_interactions.append(conversation[start_idx:])
                
                # Rebuild conversation with preserved sections
                new_conversation = "\n\n".join(preserve_sections + last_interactions)
                
                # Calculate new token count
                new_variable_part = f"{new_conversation}\n{formatted_input}\nDungeon Master:"
                new_tokens = count_tokens(base_prompt + new_variable_part)
                
                # If still too long, do more aggressive truncation
                if new_tokens > MAX_CONTEXT_TOKENS:
                    # Remove oldest consequences but keep summary
                    if "Recent Consequences:" in new_conversation:
                        new_conversation = re.sub(
                            r'Recent Consequences:.*?(- .*?)(?:\n\n|$)',
                            'Recent Consequences:\n  - ... (older consequences truncated)',
                            new_conversation,
                            flags=re.DOTALL
                        )
                
                conversation = new_conversation
                variable_part = f"{conversation}\n{formatted_input}\nDungeon Master:"
                print(f"\n[Context truncated to maintain performance. Current tokens: {count_tokens(base_prompt + variable_part)}]")
            
            full_conversation = base_prompt + variable_part
            
            # Get AI response with state context
            ai_reply = get_ai_response(full_conversation)
            
            if ai_reply:
                ai_reply = sanitize_response(ai_reply)
                print(f"\nDungeon Master: {ai_reply}")
                speak(ai_reply)
                
                # Update conversation
                conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
                last_ai_reply = ai_reply
                
                # Update world state based on player action and consequence
                update_world_state(user_input, ai_reply, player_choices)

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            print("An unexpected error occurred. The adventure continues...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        print("A critical error occurred. Please check the log file for details.")