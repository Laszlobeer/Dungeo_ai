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
    return generic_starters.get(genre, "You find yourself in an unexpected situation when")

genres = {
    "1": ("Fantasy", list(ROLE_STARTERS["Fantasy"].keys())),
    "2": ("Sci-Fi", list(ROLE_STARTERS["Sci-Fi"].keys())),
    "3": ("Cyberpunk", list(ROLE_STARTERS["Cyberpunk"].keys())),
    "4": ("Post-Apocalyptic", list(ROLE_STARTERS["Post-Apocalyptic"].keys())),
    "5": ("Random", [])
}

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

# Uncensored NSFW system prompt
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

Never break character as the Dungeon Master. Always continue the adventure.
"""

def get_current_state(player_choices):
    """Generate a string representation of the current world state"""
    state = [
        "### Current World State ###",
        f"Allies: {', '.join(player_choices['allies']) or 'None'}",
        f"Enemies: {', '.join(player_choices['enemies']) or 'None'}",
        f"Reputation: {player_choices['reputation']}",
        f"Active Quests: {', '.join(player_choices['active_quests']) or 'None'}",
        f"Completed Quests: {', '.join(player_choices['completed_quests']) or 'None'}",
    ]
    if player_choices['resources']:
        state.append("Resources:")
        for r, amt in player_choices['resources'].items():
            state.append(f"  - {r}: {amt}")
    if player_choices['factions']:
        state.append("Faction Relationships:")
        for f, lvl in player_choices['factions'].items():
            state.append(f"  - {f}: {'+' if lvl>0 else ''}{lvl}")
    if player_choices['world_events']:
        state.append("Recent World Events:")
        for ev in player_choices['world_events'][-3:]:
            state.append(f"  - {ev}")
    if player_choices['consequences']:
        state.append("Recent Consequences:")
        for c in player_choices['consequences'][-3:]:
            state.append(f"  - {c}")
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
        return response.json().get("response", "").strip()
    except Exception as e:
        logging.error(f"Error in get_ai_response: {e}")
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
        r = requests.post(ALLTALK_API_URL, data=payload, timeout=20)
        r.raise_for_status()
        if r.headers.get("Content-Type", "").startswith("audio/"):
            audio = np.frombuffer(r.content, dtype=np.int16)
            sd.play(audio, samplerate=22050)
            sd.wait()
    except Exception as e:
        logging.error(f"Error in speak: {e}")

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
""")

def remove_last_ai_response(conversation):
    pos = conversation.rfind("Dungeon Master:")
    return conversation[:pos].strip() if pos != -1 else conversation

def update_world_state(action, response, player_choices):
    # Record consequence
    player_choices['consequences'].append(f"After '{action}': {response}")
    if len(player_choices['consequences']) > 5:
        player_choices['consequences'] = player_choices['consequences'][-5:]
    # Allies
    ally_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:joins|helps|saves|allies with|becomes your ally|supports you)',
        response, re.IGNORECASE
    )
    for ally in ally_matches:
        if ally not in player_choices['allies']:
            player_choices['allies'].append(ally)
            if ally in player_choices['enemies']:
                player_choices['enemies'].remove(ally)
    # Enemies
    enemy_matches = re.findall(
        r'(\b[A-Z][a-z]+\b) (?:dies|killed|falls|perishes|becomes your enemy|turns against you|hates you)',
        response, re.IGNORECASE
    )
    for enemy in enemy_matches:
        if enemy not in player_choices['enemies']:
            player_choices['enemies'].append(enemy)
            if enemy in player_choices['allies']:
                player_choices['allies'].remove(enemy)
    # Resources gained
    resource_matches = re.findall(
        r'(?:get|find|acquire|obtain|receive|gain|steal|take) (\d+) (\w+)',
        response, re.IGNORECASE
    )
    for amount, res in resource_matches:
        res = res.lower()
        player_choices['resources'].setdefault(res, 0)
        player_choices['resources'][res] += int(amount)
    # Resources lost
    lost_matches = re.findall(
        r'(?:lose|drop|spend|use|expend|give|donate|surrender) (\d+) (\w+)',
        response, re.IGNORECASE
    )
    for amount, res in lost_matches:
        res = res.lower()
        if res in player_choices['resources']:
            player_choices['resources'][res] = max(0, player_choices['resources'][res] - int(amount))
    # World events
    world_event_matches = re.findall(
        r'(?:The|A|An) (\w+ \w+) (?:is|has been|becomes) (destroyed|created|changed|revealed|altered|ruined|rebuilt)',
        response, re.IGNORECASE
    )
    for loc, ev in world_event_matches:
        player_choices['world_events'].append(f"{loc} {ev}")
    # Quests
    if "quest completed" in response.lower() or "completed the quest" in response.lower():
        qm = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been) completed', response, re.IGNORECASE)
        if qm:
            qn = qm.group(1)
            if qn in player_choices['active_quests']:
                player_choices['active_quests'].remove(qn)
                player_choices['completed_quests'].append(qn)
    if "new quest" in response.lower() or "quest started" in response.lower():
        qm = re.search(r'quest ["\']?(.*?)["\']? (?:is|has been) (?:given|started)', response, re.IGNORECASE)
        if qm:
            qn = qm.group(1)
            if qn not in player_choices['active_quests'] and qn not in player_choices['completed_quests']:
                player_choices['active_quests'].append(qn)
    # Reputation
    if "reputation increases" in response.lower() or "reputation improved" in response.lower():
        player_choices['reputation'] += 1
    elif "reputation decreases" in response.lower() or "reputation damaged" in response.lower():
        player_choices['reputation'] = max(-5, player_choices['reputation'] - 1)
    # Factions
    faction_gain = re.findall(
        r'(?:The|Your) (\w+) faction (?:likes|respects|trusts|appreciates) you more',
        response, re.IGNORECASE
    )
    for f in faction_gain:
        player_choices['factions'][f] += 1
    faction_loss = re.findall(
        r'(?:The|Your) (\w+) faction (?:dislikes|distrusts|hates|condemns) you more',
        response, re.IGNORECASE
    )
    for f in faction_loss:
        player_choices['factions'][f] -= 1
    # Discoveries
    discovery_matches = re.findall(
        r'(?:discover|find|uncover|learn about|reveal) (?:a |an |the )?(.+?)\.',
        response, re.IGNORECASE
    )
    for d in discovery_matches:
        if d not in player_choices['discoveries']:
            player_choices['discoveries'].append(d)

def main():
    global ollama_model
    last_ai_reply = ""
    conversation = ""
    adventure_started = False
    last_player_input = ""
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

    # Load saved adventure if exists
    if os.path.exists("adventure.txt"):
        print("A saved adventure exists. Load it now? (y/n)")
        if input().strip().lower() == "y":
            try:
                with open("adventure.txt", "r", encoding="utf-8") as f:
                    conversation = f.read()
                print("Adventure loaded.\n")
                last_dm = conversation.rfind("Dungeon Master:")
                if last_dm != -1:
                    reply = conversation[last_dm + len("Dungeon Master:"):].strip()
                    print(f"Dungeon Master: {reply}")
                    speak(reply)
                    last_ai_reply = reply
                    adventure_started = True
                    if "### Persistent World State ###" in conversation:
                        state_section = conversation.split("### Persistent World State ###")[1]
                        if "Allies:" in state_section:
                            line = state_section.split("Allies:")[1].split("\n")[0].strip()
                            if line != "None":
                                player_choices["allies"] = [a.strip() for a in line.split(",")]
                        if "Enemies:" in state_section:
                            line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                            if line != "None":
                                player_choices["enemies"] = [e.strip() for e in line.split(",")]
                        if "Resources:" in state_section:
                            for ln in state_section.split("Resources:")[1].split("\n"):
                                if ln.strip().startswith("-"):
                                    parts = ln.strip().split(":")
                                    if len(parts) >= 2 and parts[1].strip().isdigit():
                                        player_choices["resources"][parts[0].replace("-", "").strip()] = int(parts[1].strip())
                        if "Consequences:" in state_section:
                            for ln in state_section.split("Consequences:")[1].split("\n"):
                                if ln.strip().startswith("-"):
                                    player_choices["consequences"].append(ln.replace("-", "").strip())
            except Exception as e:
                logging.error(f"Error loading adventure: {e}")
                print("Error loading adventure. Details logged.")

    if not adventure_started:
        # Genre selection
        print("Choose your adventure genre:")
        for key, (g, _) in genres.items():
            print(f"{key}: {g}")
        while True:
            gc = input("Enter the number of your choice: ").strip()
            if gc in genres:
                selected_genre, roles = genres[gc]
                if selected_genre == "Random":
                    opts = [v for k, v in genres.items() if k != "5"]
                    selected_genre, roles = random.choice(opts)
                break
            print("Invalid selection. Please try again.")

        if not roles:
            roles = genres[gc][1]

        # Role selection
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
            except:
                pass
            print("Invalid selection. Please try again.")

        character_name = input("\nEnter your character's name: ").strip() or "Alex"
        starter = get_role_starter(selected_genre, role)
        print(f"\n--- Adventure Start: {character_name} the {role} ---")
        print(f"Starting scenario: {starter}")
        print("Type '/?' or '/help' for commands.\n")

        initial_context = (
            f"### Adventure Setting ###\n"
            f"Genre: {selected_genre}\n"
            f"Player Character: {character_name} the {role}\n"
            f"Starting Scenario: {starter}\n\n"
            "Dungeon Master: "
        )
        conversation = initial_context

        ai_reply = get_ai_response(DM_SYSTEM_PROMPT + "\n\n" + conversation)
        if ai_reply:
            print(f"Dungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += ai_reply
            last_ai_reply = ai_reply
            player_choices['consequences'].append(f"Start: {ai_reply.split('.')[0]}")
            adventure_started = True

    # Main loop
    while adventure_started:
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
            for i, c in enumerate(player_choices['consequences'][-5:], 1):
                print(f"{i}. {c}")
            continue
        if cmd == "/state":
            print("\nCurrent World State:")
            print(get_current_state(player_choices))
            continue
        if cmd == "/redo":
            if last_ai_reply and last_player_input:
                conversation = remove_last_ai_response(conversation)
                state_ctx = get_current_state(player_choices)
                full = (
                    f"{DM_SYSTEM_PROMPT}\n\n"
                    f"### Current World State ###\n{state_ctx}\n\n"
                    f"{conversation}\n"
                    f"Player: {last_player_input}\n"
                    "Dungeon Master:"
                )
                new_reply = get_ai_response(full)
                if new_reply:
                    print(f"\nDungeon Master: {new_reply}")
                    speak(new_reply)
                    conversation += f"\nPlayer: {last_player_input}\nDungeon Master: {new_reply}"
                    last_ai_reply = new_reply
                    update_world_state(last_player_input, new_reply, player_choices)
            else:
                print("Nothing to redo.")
            continue
        if cmd == "/save":
            try:
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
                    last_dm = conversation.rfind("Dungeon Master:")
                    if last_dm != -1:
                        last_ai_reply = conversation[last_dm + len("Dungeon Master:"):].strip()
                    if "### Persistent World State ###" in conversation:
                        state_section = conversation.split("### Persistent World State ###")[1]
                        if "Allies:" in state_section:
                            line = state_section.split("Allies:")[1].split("\n")[0].strip()
                            if line != "None":
                                player_choices["allies"] = [a.strip() for a in line.split(",")]
                        if "Enemies:" in state_section:
                            line = state_section.split("Enemies:")[1].split("\n")[0].strip()
                            if line != "None":
                                player_choices["enemies"] = [e.strip() for e in line.split(",")]
                        if "Resources:" in state_section:
                            for ln in state_section.split("Resources:")[1].split("\n"):
                                if ln.strip().startswith("-"):
                                    parts = ln.strip().split(":")
                                    if len(parts) >= 2 and parts[1].strip().isdigit():
                                        player_choices["resources"][parts[0].replace("-", "").strip()] = int(parts[1].strip())
                        if "Consequences:" in state_section:
                            for ln in state_section.split("Consequences:")[1].split("\n"):
                                if ln.strip().startswith("-"):
                                    player_choices["consequences"].append(ln.replace("-", "").strip())
                except Exception as e:
                    logging.error(f"Error loading adventure: {e}")
                    print("Error loading adventure. Details logged.")
            else:
                print("No saved adventure found.")
            continue
        if cmd == "/change":
            models = get_installed_models()
            if models:
                print("Available models:")
                for i, m in enumerate(models, 1):
                    print(f"{i}: {m}")
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
        if cmd == "/count":
            try:
                arr = list(map(int, input("Enter integers separated by spaces: ").split()))
                k = int(input("Enter k value: "))
                res = count_subarrays(arr, k)
                print(f"Number of subarrays with at most {k} distinct elements: {res}")
            except Exception as e:
                print(f"Error: {e}. Please enter valid integers.")
            continue

        # Default: treat as player action
        formatted_input = f"Player: {user_input}"
        last_player_input = user_input
        state_ctx = get_current_state(player_choices)
        prompt = (
            f"{DM_SYSTEM_PROMPT}\n\n"
            f"### Current World State ###\n{state_ctx}\n\n"
            f"{conversation}\n"
            f"{formatted_input}\n"
            "Dungeon Master:"
        )
        ai_reply = get_ai_response(prompt)
        if ai_reply:
            print(f"\nDungeon Master: {ai_reply}")
            speak(ai_reply)
            conversation += f"\n{formatted_input}\nDungeon Master: {ai_reply}"
            last_ai_reply = ai_reply
            update_world_state(user_input, ai_reply, player_choices)

if __name__ == "__main__":
    main()
