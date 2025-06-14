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
        "Paladin": "You're praying at the altar of your deity when"
    },
    "Sci-Fi": {
        "Space Marine": "You're conducting patrol on a derelict space station when",
        "Scientist": "You're analyzing alien samples in your lab when",
        "Android": "You're performing system diagnostics on your ship when",
        "Pilot": "You're navigating through an asteroid field when",
        "Engineer": "You're repairing the FTL drive when",
        "Alien Diplomat": "You're negotiating with an alien delegation when",
        "Bounty Hunter": "You're tracking a target through a spaceport when",
        "Starship Captain": "You're commanding the bridge during warp travel when"
    },
    "Cyberpunk": {
        "Hacker": "You're infiltrating a corporate network when",
        "Street Samurai": "You're patrolling the neon-lit streets when",
        "Corporate Agent": "You're closing a deal in a high-rise office when",
        "Techie": "You're modifying cyberware in your workshop when",
        "Rebel Leader": "You're planning a raid on a corporate facility when",
        "Cyborg": "You're calibrating your cybernetic enhancements when"
    },
    "Post-Apocalyptic": {
        "Survivor": "You're scavenging in the ruins of an old city when",
        "Scavenger": "You're searching a pre-collapse bunker when",
        "Raider": "You're ambushing a convoy in the wasteland when",
        "Medic": "You're treating radiation sickness in your clinic when",
        "Cult Leader": "You're preaching to your followers at a ritual when"
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

# Enhanced player choices structure to track story elements
player_choices_template = {
    "allies": [],
    "enemies": [],
    "moral_alignment": "neutral",
    "discoveries": [],
    "reputation": 0,
    "resources": {},
    "locations": [],
    "factions": defaultdict(int),
    "completed_quests": [],
    "active_quests": [],
    "relationships": {},
    "world_events": [],
    "consequences": []
}

# Enhanced DM system prompt focusing on action consequences
DM_SYSTEM_PROMPT = """
You are a masterful Dungeon Master guiding an immersive role-playing adventure. Your responses MUST follow these rules:

1. ACTION-CONSEQUENCE SYSTEM:
   - EVERY player action MUST have immediate and meaningful consequences
   - Consequences should shape the narrative and world state
   - Small actions create ripple effects through the story
   - Maintain consistent world logic based on previous events

2. RESPONSE RULES:
   - NEVER take actions for the player
   - ALWAYS describe consequences through NPC dialogue and environmental changes
   - Keep responses concise (max 150 tokens)
   - Acknowledge any action from the player without restriction

3. STORY EVOLUTION:
   - The world MUST dynamically change based on the player's actions
   - NPCs MUST remember the player's choices and react accordingly
   - Environments MUST evolve based on previous events
   - Player choices should open/close future narrative paths

4. STORY BENDING:
   - Immediately incorporate narrative commands (starting with "I bend the story to...")
   - Treat these as reality-altering events that reshape the narrative
   - Describe immediate effects and consequences believably
   - Maintain internal consistency with the new reality

5. CONSEQUENCE TRACKING:
   - Track consequences in this format: [Consequence: <description>]
   - Always include at least one consequence per player action
   - Consequences can be: environmental changes, NPC reactions, quest updates, or world events

Current World State:
{player_choices}
"""

def get_current_state(player_choices):
    """Generate a string representation of the current world state"""
    state = [
        f"### Current World State ###",
        f"Allies: {', '.join(player_choices['allies']) if player_choices['allies'] else 'None'}",
        f"Enemies: {', '.join(player_choices['enemies']) if player_choices['enemies'] else 'None'}",
        f"Moral Alignment: {player_choices['moral_alignment']}",
        f"Reputation: {player_choices['reputation']}",
        f"Key Discoveries: {', '.join(player_choices['discoveries']) if player_choices['discoveries'] else 'None'}",
        f"Active Quests: {', '.join(player_choices['active_quests']) if player_choices['active_quests'] else 'None'}",
        f"Completed Quests: {', '.join(player_choices['completed_quests']) if player_choices['completed_quests'] else 'None'}",
        f"Recent Consequences: {', '.join(player_choices['consequences'][-3:]) if player_choices['consequences'] else 'None'}"
    ]
    
    # Add faction relationships if any exist
    if player_choices['factions']:
        state.append("Faction Relationships:")
        for faction, level in player_choices['factions'].items():
            state.append(f"  - {faction}: {'+' if level > 0 else ''}{level}")
    
    # Add relationships if any exist
    if player_choices['relationships']:
        state.append("NPC Relationships:")
        for npc, level in player_choices['relationships'].items():
            state.append(f"  - {npc}: {'+' if level > 0 else ''}{level}")
    
    # Add recent world events
    if player_choices['world_events']:
        state.append("Recent World Events:")
        for event in player_choices['world_events'][-3:]:
            state.append(f"  - {event}")
    
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
                    "temperature": 0.8,
                  
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

Narrative Control:
To bend the story to your will, start your input with:
  "I bend the story to..." 
  "I reshape reality so that..."
  "Suddenly, ..."
  "Miraculously, ..."

Examples:
  "I bend the story to make it rain frogs"
  "Suddenly, my character discovers a hidden power"
  "Miraculously, the dragon becomes friendly"

Story Adaptation:
Every action you take will shape the story. The world will remember:
  - Your choices and their consequences
  - Relationships with NPCs
  - Changes to the environment
  - Quest progress and world events
  - Faction relationships
  - Discoveries and creations
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

def process_narrative_command(user_input):
    """Process narrative commands that bend the story"""
    triggers = [
        "i bend the story to",
        "i reshape reality so that",
        "suddenly,",
        "miraculously,",
        "unexpectedly,",
        "against all odds,"
    ]
    
    for trigger in triggers:
        if user_input.lower().startswith(trigger):
            return f"Player (narrative command): {user_input}"
    
    return f"Player: {user_input}"

def update_world_state(response, player_choices):
    """Extract and update world state from AI response"""
    # Extract consequences
    consequence_matches = re.findall(r'\[Consequence: ([^\]]+)\]', response, re.IGNORECASE)
    for consequence in consequence_matches:
        player_choices['consequences'].append(consequence)
        # Keep only the last 5 consequences
        if len(player_choices['consequences']) > 5:
            player_choices['consequences'] = player_choices['consequences'][-5:]
    
    # Update allies
    ally_matches = re.findall(r'(\b[A-Z][a-z]+\b) (?:joins|becomes|swears loyalty to)', response, re.IGNORECASE)
    for ally in ally_matches:
        if ally not in player_choices['allies']:
            player_choices['allies'].append(ally)
            player_choices['consequences'].append(f"Gained ally: {ally}")
    
    # Update enemies
    enemy_matches = re.findall(r'(\b[A-Z][a-z]+\b) (?:hates|declares war on|vows revenge against)', response, re.IGNORECASE)
    for enemy in enemy_matches:
        if enemy not in player_choices['enemies']:
            player_choices['enemies'].append(enemy)
            player_choices['consequences'].append(f"Gained enemy: {enemy}")
    
    # Update moral alignment
    if re.search(r'heroic|selfless|virtuous', response, re.IGNORECASE):
        player_choices['moral_alignment'] = "good"
        player_choices['consequences'].append("Moral alignment shifted to good")
    elif re.search(r'villainous|selfish|ruthless', response, re.IGNORECASE):
        player_choices['moral_alignment'] = "evil"
        player_choices['consequences'].append("Moral alignment shifted to evil")
    
    # Update discoveries
    discovery_matches = re.findall(r'discovers (?:a|an|the) (\w+ \w+)', response, re.IGNORECASE)
    for discovery in discovery_matches:
        if discovery not in player_choices['discoveries']:
            player_choices['discoveries'].append(discovery)
            player_choices['consequences'].append(f"Discovered: {discovery}")
    
    # Update reputation
    if re.search(r'praise|admire|honor', response, re.IGNORECASE):
        player_choices['reputation'] += 1
        player_choices['consequences'].append("Reputation increased")
    elif re.search(r'condemn|distrust|shun', response, re.IGNORECASE):
        player_choices['reputation'] -= 1
        player_choices['consequences'].append("Reputation decreased")
    
    # Update quests
    if "quest complete" in response.lower():
        quest_match = re.search(r'[Qq]uest [Cc]omplete[:\s]*([\w\s]+)', response)
        if quest_match:
            quest_name = quest_match.group(1).strip()
            if quest_name in player_choices['active_quests']:
                player_choices['active_quests'].remove(quest_name)
                player_choices['completed_quests'].append(quest_name)
                player_choices['consequences'].append(f"Completed quest: {quest_name}")
    
    # Update faction relationships
    faction_matches = re.findall(r'(\b[A-Z][a-z]+ (?:Guild|Clan|Syndicate|Alliance)\b) (gains|loses) standing', response, re.IGNORECASE)
    for faction, direction in faction_matches:
        change = 1 if direction == "gains" else -1
        player_choices['factions'][faction] += change
        player_choices['consequences'].append(f"{faction} {'gained' if change > 0 else 'lost'} standing")
    
    # Update NPC relationships
    npc_matches = re.findall(r'(\b[A-Z][a-z]+\b) (?:likes|trusts|respects|dislikes|distrusts|hates) you', response, re.IGNORECASE)
    for npc in npc_matches:
        if npc not in player_choices['relationships']:
            player_choices['relationships'][npc] = 0
        
        if re.search(r'likes|trusts|respects', response, re.IGNORECASE):
            player_choices['relationships'][npc] += 1
            player_choices['consequences'].append(f"Relationship with {npc} improved")
        elif re.search(r'dislikes|distrusts|hates', response, re.IGNORECASE):
            player_choices['relationships'][npc] -= 1
            player_choices['consequences'].append(f"Relationship with {npc} worsened")
    
    # Update world events
    world_event_matches = re.findall(r'(?:The|A) (\w+ \w+) (?:has been|is now) (destroyed|rebuilt|conquered|liberated)', response, re.IGNORECASE)
    for location, event in world_event_matches:
        player_choices['world_events'].append(f"{location} {event}")
        player_choices['consequences'].append(f"World event: {location} {event}")

def enhance_player_action(user_input, player_choices):
    """Add context to player actions to ensure narrative consequences"""
    context = []
    
    if player_choices['active_quests']:
        context.append(f"Active Quests: {', '.join(player_choices['active_quests'])}")
    
    if player_choices['allies']:
        context.append(f"Allies: {', '.join(player_choices['allies'])}")
    
    if player_choices['enemies']:
        context.append(f"Enemies: {', '.join(player_choices['enemies'])}")
    
    if player_choices['consequences']:
        recent_consequences = player_choices['consequences'][-3:] if len(player_choices['consequences']) > 3 else player_choices['consequences']
        context.append(f"Recent Consequences: {', '.join(recent_consequences)}")
    
    if context:
        return f"{user_input} [Context: {'; '.join(context)}]"
    return user_input

def main():
    global ollama_model, BANWORDS
    censored = False
    last_ai_reply = ""
    conversation = ""
    character_name = "Laszlo"
    selected_genre = ""
    role = ""
    adventure_started = False

    # Initialize player choices with enhanced structure
    player_choices = {
        "allies": [],
        "enemies": [],
        "moral_alignment": "neutral",
        "discoveries": [],
        "reputation": 0,
        "resources": {},
        "locations": [],
        "factions": defaultdict(int),
        "completed_quests": [],
        "active_quests": [],
        "relationships": {},
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
                        # Simplified parsing - in a real implementation this would be more robust
                        if "Allies:" in state_section:
                            allies_line = state_section.split("Allies:")[1].split("\n")[0].strip()
                            if allies_line != "None":
                                player_choices["allies"] = [a.strip() for a in allies_line.split(",")]
                        if "Consequences:" in state_section:
                            cons_line = state_section.split("Consequences:")[1].split("\n")[0].strip()
                            if cons_line != "None":
                                player_choices["consequences"] = [c.strip() for c in cons_line.split(",")]
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

        # Build initial context with world state tracking
        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Player Character: {character_name} the {role}\n"
            f"Starting Scenario: {role_starter}\n"
            f"### World State Tracking ###\n"
            f"{get_current_state(player_choices)}"
        )
        conversation = DM_SYSTEM_PROMPT.format(player_choices=get_current_state(player_choices)) + "\n\n" + initial_context + "\n\nDungeon Master: "

        ai_reply = get_ai_response(conversation, ollama_model, censored)
        if ai_reply:
            ai_reply = sanitize_response(ai_reply, censored)
            print(f"Dungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += ai_reply
            last_ai_reply = ai_reply
            
            # Update world state based on initial response
            update_world_state(ai_reply, player_choices)
            
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
                            if "Consequences:" in state_section:
                                cons_line = state_section.split("Consequences:")[1].split("\n")[0].strip()
                                if cons_line != "None":
                                    player_choices["consequences"] = [c.strip() for c in cons_line.split(",")]
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

            # Enhance player actions with current world context
            enhanced_input = enhance_player_action(user_input, player_choices)
            
            # Process narrative commands that bend the story
            formatted_input = process_narrative_command(enhanced_input)
            
            # Build conversation with current world state
            state_context = get_current_state(player_choices)
            full_conversation = (
                f"{DM_SYSTEM_PROMPT.format(player_choices=state_context)}\n\n"
                f"{conversation}\n"
                f"{formatted_input}\n"
                "Dungeon Master:"
            )
            
            # Get AI response with state context
            ai_reply = get_ai_response(full_conversation, ollama_model, censored)
            
            if ai_reply:
                ai_reply = sanitize_response(ai_reply, censored)
                print(f"Dungeon Master: {ai_reply}")
                speak(ai_reply)
                
                # Update conversation
                conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
                last_ai_reply = ai_reply
                
                # Update world state based on AI response
                update_world_state(ai_reply, player_choices)
                
                # Show immediate consequence if available
                if player_choices['consequences']:
                    print(f"\n[Consequence: {player_choices['consequences'][-1]}]")

        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            print("An unexpected error occurred. The adventure continues...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error: {e}", exc_info=True)
        print("A critical error occurred. Please check the log file for details.")
