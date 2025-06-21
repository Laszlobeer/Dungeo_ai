# 🤖 OpenSource AI Tool
![Project Banner](https://raw.githubusercontent.com/Laszlobeer/Dungeo_ai_lan_play/main/yyqWt5B%20-%20Imgur.png)

## 🌟 What is This Progect?

**OpenSource AI Dungeon adventure** is a free and open-source project [ this is a dungeon ai text base with alltalk tts support].

It’s created with ❤️ for all ages.
create your adventure with ai Dungeo

> 🛑 **Notice**: This software is free for **personal and educational use**.  
> However, **if you use this project commercially** or **force-integrate it into any monetized or restricted system**,  
> **YOU MUST CREDIT THE ORIGINAL AUTHOR.**

---

## ⚙️ Requirements

- 🐍 Python `3.10+`
- 📦 pip (Python package installer)
- 🦙 ollama [[www.ollama.com](https://ollama.com/)]
- 🧠 [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) GPU with CUDA for fast AI model inference
- 🧰 git (optional but useful)
- 🎤 (optional) alltalk tts for narrator [AllTalk TTS GitHub Repository](https://github.com/erew123/alltalk_tts)
  


---

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Laszlobeer/Dungeo_ai.git
cd Dungeo_ai

```

### 2A Create Virtual Environment 
```bash
python -m venv Dungeo_ai
source Dungeo_ai/bin/activate  # On Windows: Dungeo_ai\Scripts\activate
```

### 2B Create Conda Enviroment

```bash
conda create -n dungeo_ai python=3.10 -y
conda activate dungeo_ai
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> 💡 If `requirements.txt` is give you a error, install dependencies manually:

```bash
pip install torch transformers flask
```

---

## 🚀 Usage

![Example 1](ex.png)
![Example 3](ex3.png)
![Example 4](ex4.png)
![Example 2](ex2.png)

### 🧪 Basic Example

```bash
python main.py 
```
## commands

```bash
Available commands:  
/? or /help       - Show this help message  
/censored         - Toggle NSFW/SFW mode  commands
/redo             - Repeat last AI response with a new generation  banwords.txt for the band words
/save             - Save the full adventure to adventure.txt  
/load             - Load the adventure from adventure.txt  
/change           - Switch to a different Ollama model  
/exit             - Exit the game  
```

---

## 📜 License & Credits

🆓 **MIT License**

- You are free to use, modify, and distribute this software.
- **BUT** if you:
  - Use this project commercially 🏢
  - Integrate it into a monetized app 💵
  - Fork it with modifications for public use

👉 **You MUST give credit to the original author!**

### ✍️ Example Credit

```
This project is based on OpenSource AI Tool by [Laszlo]([https://github.com/yourusername/opensource-ai-tool](https://github.com/Laszlobeer/Dungeo_ai))
```



---


Thanks for supporting open source! 🫶
## ☕ Support My Work

If you find this project helpful, consider [buying me a coffee](https://ko-fi.com/laszlobeer)!  
Your support helps me keep building and maintaining open-source tools. Thanks! ❤️

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/laszlobeer)

---
