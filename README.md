# CLIP Screenshot Filter (ML)

🤖 **AI-powered image classifier** that intelligently sorts screenshots using OpenAI's CLIP model.

## Features

- 🔥 **AI Classification** - Uses CLIP model for smart image sorting
- 🌓 **Dark/Light Theme** - Modern UI with theme switching
- 🌐 **Multi-language** - Polish (default) and English support
- 💾 **Settings Memory** - Remembers your folders and preferences
- 📊 **Real-time Progress** - Live progress tracking with detailed stats
- ⚡ **Fast Processing** - Multi-threaded processing with configurable confidence

## Quick Start

```bash
# Install dependencies
pip install torch transformers pillow sv-ttk

# Run the app
python main.py
```

**First run:** CLIP model will auto-download (~1.7GB)

## How it works

1. **Select input folder** with your screenshots
2. **Choose output folder** for sorted results
3. **Adjust confidence threshold** (higher = stricter)
4. **Click "Start AI Classification"**

### Output Categories

- 📁 **`clean_images/`** - Photos, memes, regular images
- 💻 **`code_screenshots/`** - Code, IDE, terminal screenshots
- ❓ **`uncertain_images/`** - Low confidence (manual review needed)

## Interface

- **🌓 Theme Toggle** - Switch between dark/light modes
- **🌐 Language Toggle** - Switch between Polish/English
- **⚙️ Configurable** - Adjust confidence threshold and logging
- **📏 Resizable** - Responsive window design

## Requirements

- Python 3.7+
- PyTorch, Transformers, Pillow, sv-ttk

## Project Structure

```
clip-screenshot-filter/
├── main.py                 # Entry point
├── gui/                    # UI components
├── core/                   # AI classification logic  
├── utils/                  # Settings, logging, i18n
└── logs/                   # Auto-generated logs
```

---

*Uses OpenAI's CLIP model - check licensing for commercial use.*