# AI Prompt Maker

A FastHTML + MonsterUI application for creating structured prompts for LLM interactions.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Create a .env file with your API keys
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open browser:**
   Visit `http://localhost:5001`

 ## Quick Usage Guide

### 🚀 **Getting Started**
1. **Choose a Template**: Select from 6 built-in templates or create your own
2. **Enter Criteria**: Describe what you want your prompt to achieve
3. **Generate**: Use Preview for instant results or Generate with AI for enhanced prompts
4. **Save & Export**: Save to history and export in multiple formats

### ⌨️ **Keyboard Shortcuts**
- `Ctrl+P` - Preview prompt
- `Ctrl+G` - Generate with AI  
- `Ctrl+S` - Save to history
- `Ctrl+H` - Toggle history
- `Ctrl+E` - Export prompt
- `Ctrl+A` - Select all components
- `Ctrl+D` - Clear all components
- `?` - Show help
- `Escape` - Close modals

### 💡 **Pro Tips**
- Use **templates** for consistent prompt structures
- Save **custom templates** for your specific use cases
- **Export templates** to share with your team
- **Version numbering** helps track prompt iterations
- Add **custom conditions** for specific requirements

## Features

### 🎯 **Core Functionality**
- **Dual Generation Modes**: Preview (instant) & AI-enhanced prompts
- **7 Prompt Components**: Role, Task, Context, Format, Examples, Constraints, Evaluation
- **6 LLM Models**: GPT-4, GPT-3.5, Claude 3 (Opus/Sonnet/Haiku), Gemini Pro

### 📚 **Template System**
- **6 Built-in Templates**: Content Creator, Educational Tutor, Business Analyst, Code Assistant, Creative Writer, Data Analyst
- **Custom Templates**: Save, manage, and share your own component combinations
- **Import/Export**: Share template libraries with your team

### 💾 **Smart Management**
- **Version Numbering**: Automatic versioning for prompt iterations (v1.0, v2.0...)
- **History Tracking**: Save up to 20 prompts with full metadata
- **Export Formats**: Plain Text, Markdown, JSON with full context

### ⚡ **Power User Features**
- **Keyboard Shortcuts**: Ctrl+P (preview), Ctrl+G (generate), Ctrl+S (save), and more
- **Auto-save**: Never lose your work with automatic draft saving
- **Real-time Counters**: Live word/character count as you type
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

### 🔧 **Technical**
- **Live Reload**: Instant updates during development
- **LiteLLM Integration**: Support for multiple AI providers
- **Professional UI**: MonsterUI components with clean, modern design

## Development Phases ✅

- [x] **Phase 1:** Core Setup (FastHTML + MonsterUI foundation)
- [x] **Phase 2:** Component Selection Interface (7 components + Select All/Clear)
- [x] **Phase 3:** Main Input Area (Auto-save + word count + examples)
- [x] **Phase 4:** LLM Integration (6 models + LiteLLM + status indicators)
- [x] **Phase 5:** Prompt Generation Engine (Preview + AI generation + templates)
- [x] **Phase 6:** Output and Management (Versioning + history + export options)
- [x] **Phase 7:** Templates and Presets (6 built-in + custom + import/export)
- [x] **Phase 8:** Polish and Testing (Shortcuts + help + responsive design)

## Tech Stack

- **FastHTML:** Python web framework
- **MonsterUI:** Component library (shadcn-like for FastHTML)
- **Uvicorn:** ASGI server
