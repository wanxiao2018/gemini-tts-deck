# Contributing to Gemini TTS Deck

[English](./CONTRIBUTING.md) · [简体中文](./CONTRIBUTING_zh.md)

Thank you for your interest in contributing to **Gemini TTS Deck**! We welcome all kinds of contributions, from bug reports and documentation enhancements to major feature developments.

---

## 🛠 Local Development Setup

### 1. Prerequisites
This project uses [`uv`](https://github.com/astral-sh/uv), an extremely fast Python package manager.

```bash
# Clone the repository
git clone https://github.com/wanxiao2018/gemini-tts-deck.git
cd gemini-tts-deck

# Setup virtual environment and dependencies
uv venv .venv
uv pip install -e .
```

### 2. Configure Environment
Copy the example environment file and configure your Gemini API Key:
```bash
cp .env.example .env
# Edit .env and insert your GEMINI_API_KEY
```

### 3. Running & Testing
- **Web Recording Deck**:
  ```bash
  # macOS / Linux / Terminal
  uv run python run.py

  # Windows (One-Click)
  run.bat
  ```
- **CLI Terminal Speech**:
  ```bash
  uv run python cli.py "Hello world, testing speech synthesis." --play
  ```

---

## 🤝 Contribution Workflow (Pull Request)

1. **Fork** the repository to your own GitHub account;
2. Create a feature branch off `main`: `git checkout -b feature/your-feature-name`;
3. Write clean, readable code and commit your changes with clear semantic messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation updates
   - `refactor:` for code restructuring
4. Push your branch to GitHub: `git push origin feature/your-feature-name`;
5. Open a **Pull Request** on GitHub with a thorough description of your changes.

---

## 💡 Roadmap & Welcome Contributions

- [ ] Multi-speaker dialogue script layout & visualization
- [ ] Docker & Docker-Compose deployment recipes
- [ ] Extended emotion tags and custom style presets
- [ ] Multilingual web UI (i18n)

---

## 📄 Code of Conduct

Please adhere to the values of mutual respect, constructive discussion, and collaboration.
