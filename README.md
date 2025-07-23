

---

# 🤖 OpenSource AI Tool

![Project Banner](https://raw.githubusercontent.com/Laszlobeer/Dungeo_ai_lan_play/main/yyqWt5B%20-%20Imgur.png)

## 🌟 What is This Project?

**OpenSource AI Dungeon Adventure** is a free and open-source interactive text adventure project with **AI-generated storytelling** and optional **AllTalk TTS narration support**.

Created with ❤️ for all ages, this project lets you explore, role-play, and create your own story-driven adventure using AI.

> 🛑 **Notice**: This software is free for **personal and educational use only**.
> If you **use it commercially** or **integrate it into monetized/restricted systems**,
> **YOU MUST CREDIT THE ORIGINAL AUTHOR.**

---

## ⚙️ Requirements

* 🐍 Python `3.10+`
* 📦 pip (Python package installer)
* 🦙 [Ollama](https://ollama.com/) (for local AI model inference)
* 🧠 [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) (for GPU acceleration)
* 🧰 git (optional but helpful)
* 🎤 (optional) [AllTalk TTS](https://github.com/erew123/alltalk_tts) for narrated voice output

---

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Laszlobeer/Dungeo_ai.git
cd Dungeo_ai
```

### 2A. Create a Virtual Environment (Python `venv`)

```bash
python -m venv Dungeo_ai
source Dungeo_ai/bin/activate  # On Windows: Dungeo_ai\Scripts\activate
```

### 2B. Create a Conda Environment (Optional)

```bash
conda create -n dungeo_ai python=3.10 -y
conda activate dungeo_ai
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> 💡 If you get errors from `requirements.txt`, try installing manually:

```bash
pip requests sounddevice numpy soundfile
```

---

## 🚀 Usage

### 🧪 Start the Adventure

```bash
python main.py
```

### 🎭 Alternate Modes

| Script           | Description                                                             |
| ---------------- | ----------------------------------------------------------------------- |
| `main.py`        | The default AI dungeon adventure experience                             |
| `funnymain.py`   | A humorous and quirky version of the game                               |
| `seriousmain.py` | A more immersive and serious roleplay with advanced class/ability logic |

> ✨ Use `funnymain.py` if you're looking for a laugh, or try `seriousmain.py` if you want a classic RPG-style experience with deeper presence, class systems, and improved logic!

---

## 💬 Available Commands

```bash
/? or /help       - Show help message  
/censored         - Toggle NSFW/SFW mode  
/redo             - Regenerate last AI response  
/save             - Save the story to adventure.txt  
/load             - Load adventure from adventure.txt  
/change           - Switch to another Ollama model  
/exit             - Exit the game  
```

---

## 📜 License & Credits

🆓 **MIT License** — Free to use, modify, and distribute.

> **If you:**
>
> * Use this commercially 🏢
> * Integrate into a monetized app 💵
> * Publicly modify/fork it
>
> 👉 **You MUST give credit to the original author.**

### ✍️ Example Credit

```
This project is based on OpenSource AI Tool by [Laszlo](https://github.com/Laszlobeer/Dungeo_ai)

